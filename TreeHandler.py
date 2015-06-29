import math
import networkx as nx
import Config
from Node import Node

import time


class TreeHandler:

    # Dictionary of the form {(y, x): Node} that contains all the node objects in the image
    node_dict = None

    # The node that best approximates the seed point, and its key in node_dict
    best_node = None

    # A set containing the seed node for each tree
    all_seed_nodes = None

    # Node and tree counts, stored for analytics purposes
    initial_nodecount = 0
    current_nodecount = 0
    tree_count = 0

    # Trash can for removing nodes after iteration
    trash = set()

    def __init__(self):
        """
        Initializes a TreeHandler object
        """

        self.node_dict = dict()
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
                    self.initial_nodecount += 1
                    self.current_nodecount += 1

    def find_best_node(self, start_key):
        """
        Check the entire node_dict for the best approximation to the click location
        """

        key_range = 0
        looking_for_seed_node = True

        while looking_for_seed_node:
            for x in range(start_key[1] - key_range, start_key[1] + key_range + 1):
                for y in range(start_key[0] - key_range, start_key[0] + key_range + 1):
                    key = (y, x)
                    if key in self.node_dict:
                        return self.node_dict[key]
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
            self.node_dict[node1_key].set_neighbors(self.node_dict[node2_key])

    def build_tree(self, start_node):
        """
        Builds a flowing tree representation of the graph in the node. It must have a total size greater than
        or equal to Config.minimum_tree_size to be considered valid.
        :param start_node:
        :return: True if a tree was successfully built from the start key, or False
        """

        # Current tree size is 1, because you're starting with one pixel
        node_set = {start_node}

        previous_set = {start_node}
        current_set = set(start_node.neighbors)
        next_set_exists = True

        # Continue iterating as long as there are unattached neighbors
        while next_set_exists:

            next_set = set()
            for node in current_set:

                for neighbor in node.neighbors:
                    if neighbor and (neighbor not in previous_set) and (neighbor not in current_set):
                            if not neighbor.visited:
                                next_set.add(neighbor)
                                node_set.add(neighbor)

                node.visited = True

            if not next_set:
                next_set_exists = False
            else:
                previous_set = current_set
                current_set = next_set

        # Make sure the tree is large enough to not be noise
        if len(node_set) < Config.minimum_tree_size:
            for node in node_set:
                self.trash.add(node)
            return False
        else:
            return True

    def remove_nodes(self, node_set):
        """

        """
        for node in node_set:
            self.remove_node(node)

    def remove_node(self, node):
        """

        :param node:
        :return:
        """

        key = (node.y, node.x)

        if node.children:
            for child in node.children:
                child.parents.discard(node)

        if node.parents:
            for parent in node.parents:
                parent.children.discard(node)

        if node.children and node.parents:
            for child in node.children:
                for parent in node.parents:
                    parent.set_child(child)

        for i in range(8):
            if node.neighbors[i]:
                neighbor = node.neighbors[i]
                this_node_loc = (i+4)%8
                neighbor.neighbors[this_node_loc] = None

        self.current_nodecount -= 1

        self.node_dict.pop(key, None)

    def find_additional_trees(self):
        """
        Finds all nodes with 8 neighbors and attempts to group them into trees.
        """

        for node in self.node_dict.values():

            # Use only completely-surrounded nodes as potential seed points
            if None not in node.neighbors:

                # Use only nodes that haven't been put in a tree (no children or parents)
                if not node.visited:

                    # Build tree and increment tree count if it's valid
                    if self.build_tree(node):
                        self.tree_count += 1
                        self.all_seed_nodes.add(node)

        self.remove_nodes(self.trash)
        self.trash = set()

    def prune_dark_nodes(self):
        """
        Removes dark leaf nodes from the dictionary. Anything darker than minimum_visible_intensity is removed.
        """

        minimum_visible_intensity = .25

        # Loop until there are no dark nodes on the edges of the tree
        dark_node_in_leaf_set = True
        while dark_node_in_leaf_set:

            leaf_set = set()

            for node in self.node_dict.values():

                    # If None is present in a neighbor list, this node must be touching the black
                    if None in node.neighbors:
                        leaf_set.add(node)

            dark_node_in_leaf_set = False

            for node in leaf_set:

                # Prune the dark nodes found in the leaf set
                if node.intensity < minimum_visible_intensity:
                    self.remove_node(node)
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
        for node in self.node_dict.values():
            if None in node.neighbors:
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

    def prune_redundant_nodes(self):
        """

        :return:
        """

        # create initial set of nodes that touch the black
        current_set = set()
        current_radius_value = 0

        for node in self.node_dict.values():
            if node.radius == current_radius_value:
                current_set.add(node)

        while current_set:
            print(len(current_set))
            current_radius_value += 1

            next_set = set()

            for node in current_set:

                for neighbor in node.neighbors:
                    if neighbor and neighbor.radius == current_radius_value:
                        if neighbor not in current_set:
                            next_set.add(neighbor)

                if not self.check_if_skeleton(node):
                    self.remove_node(node)

            current_set = next_set

    def check_if_skeleton(self, node):
        """

        :param node:
        :return:
        """

        node_loc_list = []
        black_loc_list = []

        #
        for i in range(8):
            if node.neighbors[i]:
                node_loc_list.append(i)
            else:
                black_loc_list.append(i)

        if len(black_loc_list) == 8:
            return False
        else:
            return self.check_sequences(node_loc_list)

    @staticmethod
    def check_sequences(loc_list):
        """

        :param loc_list:
        :return:
        """

        # check if the location list only contains a diagonal attachment
        if len(loc_list) == 1:
            if loc_list[0] %2:
                return False

        sequence_count = 0
        if loc_list[0] is not 0 or loc_list[-1] is not 7:
            sequence_count += 1

        for i in range(len(loc_list) - 1):
            if loc_list[i+1] - loc_list[i] is not 1:
                sequence_count += 1

        return sequence_count > 1

    def prune_internal_nodes(self):
        """

        :return:
        """
        # rebuild all trees from the neighbor lists and the remaining nodes closest to the seed points
        # this will ensure that parent-child relationships are consistent and usable
        self.rebuild_trees()

        # find the initial set (all nodes with radius 0)
        current_set = set()
        current_radius = 0
        for node in self.node_dict.values():
            if node.radius == current_radius:
                current_set.add(node)

        # check each node to see if it has a neighbor.radius > node.radius
        while current_set:
            next_set = set()
            for node in current_set:

                # add its neighbors with radius = current_radius+1 to next set
                node_is_covered = False
                for neighbor in node.neighbors:
                    if neighbor and neighbor.radius > node.radius:
                        next_set.add(neighbor)
                        node_is_covered = True

                if node_is_covered:
                    self.remove_node(node)

            current_set = next_set

        # fix excessively thick roots
        self.cleanup_right_angles()

        # remove short 'branches' (actually just bumps on root edges)
        self.remove_short_branches()

    def rebuild_trees(self):
        """

        :return:
        """
        # update the set of all_seed_nodes (find the closest remaining node to each seed node)
        new_seed_nodes = set()

        for node in self.all_seed_nodes:
            key = (node.y, node.x)
            new_seed = self.find_best_node(key)
            new_seed_nodes.add(new_seed)

        self.all_seed_nodes = new_seed_nodes

        # reset parent and child fields
        for node in self.node_dict.values():
            node.children = set()
            node.parents = set()

        # iteratively attach neighbors as children to each seed
        previous_set = set()
        current_set = self.all_seed_nodes
        while current_set:
            next_set = set()
            for node in current_set:
                for neighbor in node.neighbors:
                    if neighbor and neighbor not in current_set and neighbor not in previous_set:
                        if not neighbor.parents:
                            node.set_child(neighbor)
                            next_set.add(neighbor)
            previous_set = current_set
            current_set = next_set

    def cleanup_right_angles(self):
        """

        :return:
        """
        pass

    def remove_short_branches(self):
        """

        :return:
        """
        pass