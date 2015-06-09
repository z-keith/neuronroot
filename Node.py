# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       Node
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Object that represents a single pixel in the original image.
#               Holds information about the image at that point.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Node:

    # Key this node is given in node_dict
    key = None

    # Physical location of this node, measured in pixels as a positive integer
    x = None
    y = None

    # Intensity/brightness of this node, measured as an integer 0 <= i <= 255
    intensity = None

    # Radius of the root at this node, measured in pixels as a positive integer
    radius = None

    # Immediate neighbors of this node, listed as references.
    # Stored as a list of length 8, each position relates to an orientation like so:
    #
    # [0, 1, 2, 3, 4, 5, 6, 7] ->   0   1   2
    #                               3   n   4
    #                               5   6   7
    neighbors = None

    # Parents and children of this node, stored as references to the relatives themselves.
    parents = None
    children = None

    # Set of nodes within the radius of this node, stored by reference
    covered_set = None

    # Set of nodes this node is covered by, stored by reference
    covered_by = None

    # Toggle for lazy deletion - true deletion would break the mass operator for covered sets
    removed = False

    # Toggle to ensure a node is only printed once per print
    printed = False

    def __init__(self, key, x, y, i):
        """
        Initialize a node by location and intensity
        :param key: id this node has in node_dict (int)
        :param x: x-location of the node being created (int)
        :param y: y-location of the node being created (int)
        :param i: intensity of the node being created (int)
        """

        self.key = key
        self.x = x
        self.y = y
        self.intensity = i
        self.radius = None  # Leave as None until set by a function later, but adding here for clarity/consistency

        self.neighbors = [None, None, None, None, None, None, None, None]  # 8 items allow location-based placement
        self.parents = set()
        self.children = set()

        self.covered_set = set()
        self.covered_by = set()

    def __repr__(self):
        """
        :return: String displaying a node's information
        """
        info_string = "\nX: {0} Y: {1} I: {2} R: {3}".format(self.x, self.y, round(self.intensity, 1), self.radius)
        neighbor_string = "\nNeighbors:  {0}{1}{2}\n\t\t\t{3}  x   {4}\n\t\t\t{5}{6}{7}"\
            .format(str(self.neighbors[0]).ljust(6), str(self.neighbors[1]).ljust(6), str(self.neighbors[2]).ljust(6),
                    str(self.neighbors[3]).ljust(6), str(self.neighbors[4]).ljust(6),
                    str(self.neighbors[5]).ljust(6), str(self.neighbors[6]).ljust(6), str(self.neighbors[7]).ljust(6))
        child_string = self.print_children()
        parent_string = self.print_parents()
        return "\t{0}\t{1}\t{2}\t{3}\n".format(info_string, neighbor_string, child_string, parent_string)

    def __str__(self):
        """
        :return: A simple representation of the node: its key ID
        """
        return str(self.key)

    def print_children(self):
        """
        Prints a pretty list of the children of this node
        :return: A string representing this node's children
        """
        children = "\nChildren: "
        for child in self.children:
            children += (str(child) + ", ")

        if len(children) > 11:
            children = children[:-2]

        return children

    def print_parents(self):
        """
        Prints a pretty list of the parents of this node
        :return: A string representing this node's parents
        """
        parents = "\nParents: "
        for parent in self.parents:
            parents += (str(parent) + ", ")

        if len(parents) > 10:
            parents = parents[:-2]

        return parents

    def set_child(self, child):
        """
        Sets a parent/child relationship between two nodes
        :param child: the node to be set as the child of this
        """

        self.children.add(child)
        child.parents.add(self)

    def set_neighbors(self, neighbor):
        """
        Sets a neighbor relationship between 2 nodes
        :param neighbor: the node to be added as a neighbor to this node
        """

        diff_x = neighbor.x - self.x
        diff_y = neighbor.y - self.y

        # The neighbor node is on the row above this
        if diff_y == -1:

            # The neighbor node is in the top-left position relative to this
            if diff_x == -1:
                self.neighbors[0] = neighbor
                neighbor.neighbors[7] = self

            # The neighbor node is in the top-center position relative to this
            if diff_x == 0:
                self.neighbors[1] = neighbor
                neighbor.neighbors[6] = self

            # The neighbor node is in the top-right position relative to this
            if diff_x == 1:
                self.neighbors[2] = neighbor
                neighbor.neighbors[5] = self

        # The neighbor node is on the same row as this
        if diff_y == 0:

            # The neighbor node is in the center-left position relative to this
            if diff_x == -1:
                self.neighbors[3] = neighbor
                neighbor.neighbors[4] = self

            # The neighbor node is in the center-right position relative to this
            if diff_x == 1:
                self.neighbors[4] = neighbor
                neighbor.neighbors[3] = self

        # The neighbor node is on the row below this
        if diff_y == 1:

            # The neighbor node is in the bottom-left position relative to this
            if diff_x == -1:
                self.neighbors[5] = neighbor
                neighbor.neighbors[2] = self

            # The neighbor node is in the bottom-center position relative to this
            if diff_x == 0:
                self.neighbors[6] = neighbor
                neighbor.neighbors[1] = self

            # The neighbor node is in the bottom-right position relative to this
            if diff_x == 1:
                self.neighbors[7] = neighbor
                neighbor.neighbors[0] = self

    def add_to_covered_set(self, covered):
        """
        Sets a covered/covered by relationship between 2 nodes
        :param covered: the node considered "covered" by this node
        """

        self.covered_set.add(covered)
        covered.covered_by.add(self)

    def clean_up_node(self):
        """

        :return:
        """

        remove_set = set()

        for node in self.children:
            if node.removed:
                remove_set.add(node)

        for node in remove_set:
            self.children.discard(node)

        remove_set.clear()

        for node in self.parents:
            if node.removed:
                remove_set.add(node)

        for node in remove_set:
            self.parents.discard(node)

        remove_set.clear()

        for i in range(8):
            if self.neighbors[i]:
                if self.neighbors[i].removed:
                    remove_set.add(i)

        for i in remove_set:
            self.neighbors[i] = None