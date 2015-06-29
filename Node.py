# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       Node
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Object that represents a single pixel in the original image.
#               Holds information about the image at that point.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Node:
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
    #                               7   n   3
    #                               6   5   4
    neighbors = None

    # Toggle to make sure this node is only visited once for tree sizing
    visited = False

    # Parents and children of this node, stored as references to the relatives themselves.
    parents = None
    children = None

    # Toggle to represent a skeleton node that can be ignored in printing
    is_skeleton = False

    # Toggle to ensure a node is only printed once per print
    printed = False

    def __init__(self, x, y, i):
        """
        Initialize a node by location and intensity
        :param x: x-location of the node being created (int)
        :param y: y-location of the node being created (int)
        :param i: intensity of the node being created (int)
        """

        self.x = x
        self.y = y
        self.intensity = i
        self.radius = None  # Leave as None until set by a function later, but adding here for clarity/consistency

        self.neighbors = [None, None, None, None, None, None, None, None]  # 8 items allow location-based placement
        self.parents = set()
        self.children = set()

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
                neighbor.neighbors[4] = self

            # The neighbor node is in the top-center position relative to this
            if diff_x == 0:
                self.neighbors[1] = neighbor
                neighbor.neighbors[5] = self

            # The neighbor node is in the top-right position relative to this
            if diff_x == 1:
                self.neighbors[2] = neighbor
                neighbor.neighbors[6] = self

        # The neighbor node is on the same row as this
        if diff_y == 0:

            # The neighbor node is in the center-left position relative to this
            if diff_x == -1:
                self.neighbors[7] = neighbor
                neighbor.neighbors[3] = self

            # The neighbor node is in the center-right position relative to this
            if diff_x == 1:
                self.neighbors[3] = neighbor
                neighbor.neighbors[7] = self

        # The neighbor node is on the row below this
        if diff_y == 1:

            # The neighbor node is in the bottom-left position relative to this
            if diff_x == -1:
                self.neighbors[6] = neighbor
                neighbor.neighbors[2] = self

            # The neighbor node is in the bottom-center position relative to this
            if diff_x == 0:
                self.neighbors[5] = neighbor
                neighbor.neighbors[1] = self

            # The neighbor node is in the bottom-right position relative to this
            if diff_x == 1:
                self.neighbors[4] = neighbor
                neighbor.neighbors[0] = self