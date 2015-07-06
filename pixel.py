# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       pixel.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Object that represents a single pixel in the original image.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Pixel:
    # Physical location of this pixel, measured in pixels as a positive integer
    x = None
    y = None

    # Intensity/brightness of this pixel, measured as a float 0 <= i <= 255
    intensity = None

    # Radius of the root at this pixel, measured in pixels as a positive integer
    radius = None

    # Immediate neighbors of this pixel, listed as references.
    # Stored as a list of length 8, each position relates to an orientation like so:
    #
    # [0, 1, 2, 3, 4, 5, 6, 7] ->   0   1   2
    #                               7   n   3
    #                               6   5   4
    # 'None' is used to represent that there is no pixel adjacent to this one in a given position
    neighbors = None

    # Parents and children of this pixel, stored as sets of references to the relatives
    parents = None
    children = None

    # Toggle to make sure this pixel is only visited once for tree sizing
    is_visited = False

    def __init__(self, x, y, i):
        """
        Initialize a pixel by location and intensity
        :param x: x-location of the pixel being created (int)
        :param y: y-location of the pixel being created (int)
        :param i: intensity of the pixel being created (int)
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
        Sets a parent/child relationship between two pixels
        :param child: the pixel to be set as the child of this
        """

        self.children.add(child)
        child.parents.add(self)

    def set_neighbors(self, neighbor):
        """
        Sets a neighbor relationship between 2 pixels
        :param neighbor: the pixel to be added as a neighbor to this pixel
        """

        diff_x = neighbor.x - self.x
        diff_y = neighbor.y - self.y

        # The neighbor pixel is on the row above this
        if diff_y == -1:

            # The neighbor pixel is in the top-left position relative to this
            if diff_x == -1:
                self.neighbors[0] = neighbor
                neighbor.neighbors[4] = self

            # The neighbor pixel is in the top-center position relative to this
            if diff_x == 0:
                self.neighbors[1] = neighbor
                neighbor.neighbors[5] = self

            # The neighbor pixel is in the top-right position relative to this
            if diff_x == 1:
                self.neighbors[2] = neighbor
                neighbor.neighbors[6] = self

        # The neighbor pixel is on the same row as this
        if diff_y == 0:

            # The neighbor pixel is in the center-left position relative to this
            if diff_x == -1:
                self.neighbors[7] = neighbor
                neighbor.neighbors[3] = self

            # The neighbor pixel is in the center-right position relative to this
            if diff_x == 1:
                self.neighbors[3] = neighbor
                neighbor.neighbors[7] = self

        # The neighbor pixel is on the row below this
        if diff_y == 1:

            # The neighbor pixel is in the bottom-left position relative to this
            if diff_x == -1:
                self.neighbors[6] = neighbor
                neighbor.neighbors[2] = self

            # The neighbor pixel is in the bottom-center position relative to this
            if diff_x == 0:
                self.neighbors[5] = neighbor
                neighbor.neighbors[1] = self

            # The neighbor pixel is in the bottom-right position relative to this
            if diff_x == 1:
                self.neighbors[4] = neighbor
                neighbor.neighbors[0] = self
