import math
import networkx as nx
import Config
from Node import Node


class TreeHandler:

    # Dictionary of the form {int: Node} that contains all the node objects in the image
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
                    key = self.graph.number_of_nodes()
                    self.node_dict[key] = Node(key, x, y, image_h.array[y][x])
                    self.graph.add_node(self.graph.number_of_nodes())

        self.initial_nodecount = self.graph.number_of_nodes()
        self.current_nodecount = self.graph.number_of_nodes()

    def find_best_node(self):
        """
        Check the entire node_dict for the best approximation to the click location
        """
        # TODO: Improve algorithm to start in the center of the image and move towards the seed point

        best_distance_to_seed = 999999

        for key in self.graph:
            # check if this node is closer by linear distance to the seed location than the current best
            this_distance_to_seed = math.sqrt((Config.seedX - self.node_dict[key].x)**2 +
                                              (Config.seedY - self.node_dict[key].y)**2)
            if this_distance_to_seed < best_distance_to_seed:
                best_distance_to_seed = this_distance_to_seed
                self.best_node = self.node_dict[key]
                self.best_node_key = key
                self.all_seed_nodes.add(self.node_dict[key])

    def find_edges(self):
        """
        Manage the search_in_direction function to check the edges that potentially extend ahead of each
        node in the graph
        """

        for key in self.graph:
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
        # TODO: This is the most time-consuming part of the program. Should look into methods to speed it up.

        node2_x = self.node_dict[node1_key].x + delta[0]
        node2_y = self.node_dict[node1_key].y + delta[1]

        for node2_key in range(node1_key, self.calc_max_range(node1_key)):
            if self.node_dict[node2_key].x == node2_x:
                if self.node_dict[node2_key].y == node2_y:
                    edge_weight = self.calculate_weight(node1_key, node2_key)
                    self.graph.add_edge(node1_key, node2_key)
                    self.graph[node1_key][node2_key]['weight'] = edge_weight
                    self.node_dict[node1_key].set_neighbors(self.node_dict[node2_key])
                    break

    def calc_max_range(self, node1_key):
        """
        Calculates the index within node_dict of the last possible node that could represent the pixel one down and one
        to the right from the current node1. If the entire image is made of nodes, this index is node1 + the height of
        the image + 2, for a complete line across the image plus the pixel to the right and below-right (the target)
        :param node1_key: node to search from
        :return: the maximum distance an adjacent node
        """
        if (node1_key + Config.image_scaled_height + 2) < (self.initial_nodecount - 1):
            return node1_key + Config.image_scaled_height + 2
        else:
            return self.initial_nodecount - 1

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

