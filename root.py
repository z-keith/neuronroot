# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Object that hold information about a sequence of pixels that make up a root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import math


class Root:

    pixel_list = None

    parent_root = None

    branch_list = None

    total_length = None

    average_radius = None

    def __init__(self, pixel_list):
        self.pixel_list = pixel_list
        self.branch_list = []

    def calculate_root_statistics(self):
        """
        Calculates the total length and average radius for this root
        :return: Nothing.
        """
        total_length = 0
        total_radius = 0

        for i in range(0, len(self.pixel_list)-1):

            total_radius += self.pixel_list[i].radius

            if i>0:
                # Use the distance formula
                delta_x = self.pixel_list[i].x - self.pixel_list[i-1].x
                delta_y = self.pixel_list[i].y - self.pixel_list[i-1].y
                segment_length = math.sqrt(delta_x**2 + delta_y**2)
                total_length += segment_length

        self.total_length = total_length
        self.average_radius = total_radius/len(self.pixel_list)