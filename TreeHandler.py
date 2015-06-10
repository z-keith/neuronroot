import math
import networkx as nx
import Config
from Node import Node


class TreeHandler:

    # Dictionary of the form {(y, x): Node} that contains all the node objects in the image
    node_dict = None

    # Graph that holds node_dict keys and their relationships
    graph = None

    # The node that best approximates the seed point, and its key in node_dict
    best_node = None
    best_node_key = None

    # A set containing the seed node for each tree
    all_seed_nodes = None

    # Node and tree counts, stored for analytics purposes
    initial_nodecount = None
    current_nodecount = None
    tree_count = None

    def __init__(self):
        """
        Initializes a TreeHandler object
        """

        self.node_dict = dict()
        self.graph = nx.Graph()
        self.all_seed_nodes = set()

    def load_nodes(self, image_h):
        """
        Loads an array from an ImageHandler into a node_dict and graph
        :param image_h: An ImageHandler containing an array and information on it
        """

        # create nodes out of array locations of nonzero brightness
        for y in range(0, image_h.image_height):
            for x in range(0, image_h.image_width):
                if image_h.array[y][x]:
                    # current number of nodes in the graph is used for the key to node_dict and for the
                    # node label in the graph, to keep the two associated.
                    key = (y, x)
                    self.node_dict[key] = Node(x, y, image_h.array[y][x])
                    self.graph.add_node(self.graph.number_of_nodes())

        self.initial_nodecount = self.graph.number_of_nodes()
        self.current_nodecount = self.graph.number_of_nodes()

    def find_best_node(self):
        """
        Check the entire node_dict for the best approximation to the click location
        """

        start_key = (Config.seedY, Config.seedX)
        key_range = 0
        looking_for_seed_node = True

        while looking_for_seed_node:
            for x in range(start_key[1] - key_range, start_key[1] + key_range + 1):
                for y in range(start_key[0] - key_range, start_key[0] + key_range + 1):
                    key = (y, x)
                    if key in self.node_dict:
                        looking_for_seed_node = False
                        self.best_node_key = key
                        self.best_node = self.node_dict[key]
                        self.all_seed_nodes.add(self.node_dict[key])
                    else:
                        key_range += 1

    def find_edges(self):
        """
        Manage the search_in_direction function to check the edges that potentially extend ahead of each
        node in the graph
        """

        for key in self.node_dict:
            # If each node checks the same half of eight possible directions, they will tessellate to
            # cover all possible edges. By convention, we choose to choose the 4 nodes that would come
            # after the current node in its neighbor list.
            for delta in [(1, 0), (-1, 1), (0, 1), (1, 1)]:
                self.search_in_direction(key, delta)

    def search_in_direction(self, node1_key, delta):
        """
        Searches for any possible neighbor nodes in the graph that exist in the direction given by delta
        :param node1_key: node we are looking for neighbors to
        :param delta: tuple of the change in (x,y) we're looking for for node 2
        """

        node2_x = node1_key[1] + delta[0]
        node2_y = node1_key[0] + delta[1]
        node2_key = (node2_y, node2_x)

        if node2_key in self.node_dict:
            edge_weight = self.calculate_weight(node1_key, node2_key)
            self.graph.add_edge(node1_key, node2_key)
            self.graph[node1_key][node2_key]['weight'] = edge_weight
            self.node_dict[node1_key].set_neighbors(self.node_dict[node2_key])

    def calculate_weight(self, node1_key, node2_key):
        """
        Formula taken from Peng et al section 2.2 to calculate the weight of an edge between 2 nodes
        :param node1_key: key of the first node
        :param node2_key: key of the second node
        :return: float indicating the proper weight
        """

        result1 = math.exp(10*(1-self.node_dict[node1_key].intensity/255)**2)
        result2 = math.exp(10*(1-self.node_dict[node2_key].intensity/255)**2)
        return (result1+result2)/2

    def build_tree(self, start_key):
        """
        Builds a flowing tree representation of the graph in the node. It must have a total size greater than
        or equal to Config.minimum_tree_size to be considered valid.
        :param start_key:
        :return: True if a tree was successfully built from the start key, or False
        """

        # Current tree size is 1, because you're starting with one pixel
        tree_size = 1

        previous_set = set()
        current_set = {self.node_dict[start_key]}
        next_set_exists = True

        # Continue iterating as long as there are unattached neighbors
        while next_set_exists:

            next_set = set()
            for node in current_set:
                for neighbor in node.neighbors:
                    if neighbor and (neighbor not in previous_set) and (neighbor not in current_set):
                        if not neighbor.removed:
                            if not neighbor.parents:
                                next_set.add(neighbor)
                                tree_size += 1
                            node.set_child(neighbor)

            if not next_set:
                next_set_exists = False
            else:
                previous_set = current_set
                current_set = next_set

        # Make sure the tree is large enough to not be noise
        if tree_size < Config.minimum_tree_size:
            self.set_tree_removed(self.node_dict[start_key])
            return False
        else:
            return True

    def set_tree_removed(self, start_node):
        """
        Remove a tree, starting from a given seed node. Will not remove anything upstream of start_node
        :param start_node: The node to remove everything below it. To remove an entire tree, use its seed node
        """
        # Recursively call this function on all children
        for child in start_node.children:
            if not child.removed:
                self.set_tree_removed(child)
        # Remove this node
        start_node.removed = True
        self.current_nodecount -= 1

    def find_additional_trees(self):
        """
        Finds all nodes with 8 neighbors and attempts to group them into trees.
        """

        self.tree_count = 0

        for key in self.node_dict:

            # Use only completely-surrounded nodes as potential seed points
            if None not in self.node_dict[key].neighbors:

                # Use only nodes that haven't been put in a tree (no children or parents)
                if not self.node_dict[key].children and not self.node_dict[key].parents:

                    # Build tree and increment tree count if it's valid
                    if self.build_tree(key):
                        self.tree_count += 1
                        self.all_seed_nodes.add(self.node_dict[key])

    def prune_dark_nodes(self):
        """
        Removes dark leaf nodes from the dictionary. Anything darker than minimum_visible_intensity is removed.
        """

        minimum_visible_intensity = 0.5

        # Loop until there are no dark nodes on the edges of the tree
        dark_node_in_leaf_set = True
        while dark_node_in_leaf_set:

            leaf_set = set()

            for key in self.node_dict:
                if not self.node_dict[key].removed:

                    # Make sure all potential 'neighbors' actually exist
                    self.node_dict[key].clean_up_node()

                    # If None is present in a neighbor list, this node must be touching the black
                    if None in self.node_dict[key].neighbors:
                        leaf_set.add(key)

            dark_node_in_leaf_set = False

            for key in leaf_set:

                # Prune the dark nodes found in the leaf set
                if self.node_dict[key].intensity < minimum_visible_intensity:
                    self.node_dict[key].removed = True
                    self.current_nodecount -= 1
                    dark_node_in_leaf_set = True

    def set_radii(self):
        """
        Iterates through the nodes of a root structure setting the radius of each node. It can be assumed that any node
        that does not have 8 neighbors is touching black space and the maximum radius of a circle centered at the node
        and contained within the root is 0. It follows that all nodes touching that node (the second layer inward) have
        radius 1, and so on and so forth.
        """

        # create set of nodes that touch the black
        outermost_node_set = set()
        for key in self.node_dict:
            node = self.node_dict[key]
            if None in node.neighbors and not node.removed:
                outermost_node_set.add(node)

        # recursively iterate through until all radii are set
        current_radius_value = 0
        while outermost_node_set:
            new_outermost_set = set()

            # set current list's radii first, to avoid conflicts
            for node in outermost_node_set:
                node.radius = current_radius_value

            # add all nodes that a) touch the current set and b) haven't had a radius set yet
            for node in outermost_node_set:
                for neighbor in node.neighbors:
                    if neighbor and neighbor.radius is None:
                        new_outermost_set.add(neighbor)

            # increment current radius, reloop
            current_radius_value += 1
            outermost_node_set = new_outermost_set

    def set_covered_areas(self):
        """
        For each node in the dictionary, find all nodes within its radius and add it to the original node's covered-set
        """

        for node in self.node_dict.values():
            if not node.removed:
                node.add_to_covered_set(node)
                old_cover_set = set()
                old_cover_set.add(node)

                for r in range(node.radius):
                    cover_set = set()
                    for cover_node in old_cover_set:
                        for neighbor in cover_node.neighbors:
                            if neighbor:
                                cover_set.add(neighbor)
                    for cover_node in cover_set:
                        node.add_to_covered_set(cover_node)

    def modern_covered_areas(self):

        # TODO: Figure out the differences between this and set_covered_areas()
        for node in self.node_dict.values():
            if not node.removed:

                radius_range = node.radius

                # Set up the square to search in
                for x in range(node.x - radius_range, node.x + radius_range + 1):
                    for y in range(node.y - radius_range, node.y + radius_range + 1):

                        # If a given node exists, add it to the covered set
                        if (y, x) in self.node_dict:
                            if not self.node_dict[(y, x)].removed:
                                node.add_to_covered_set(self.node_dict[(y, x)])

    def prune_redundant_nodes(self):
        """
        Implements the covered-leaf removal algorithm as described in Peng et al 2.3.2
        """

        covering_threshold = 0.5

        nodes_left_to_remove = True

        while nodes_left_to_remove:

            nodes_left_to_remove = False

            leaf_set = set()

            # TODO: Make this work

    @staticmethod
    def mass_operator(set_to_mass):
        """

        :param set_to_mass:
        :return:
        """
        total = 0.0
        for node in set_to_mass:
            total += node.intensity

        return total
