# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Object that hold information about a sequence of pixels that make up a root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import math


class Root:
    key = None

    pixel_list = None

    parent_root = None

    branch_list = None

    total_length = None

    average_radius = None

    def __init__(self, pixel_list, key):
        self.pixel_list = pixel_list
        self.branch_list = []
        self.key = key

    def calculate_root_statistics(self):
        """
        Calculates the total length and average radius for this root
        :return: Nothing.
        """
        total_length = 0
        total_radius = 0

        for i in range(len(self.pixel_list)):

            total_radius += self.pixel_list[i].radius

            if i > 0:
                # Use the distance formula
                delta_x = self.pixel_list[i].x - self.pixel_list[i - 1].x
                delta_y = self.pixel_list[i].y - self.pixel_list[i - 1].y
                segment_length = math.sqrt(delta_x ** 2 + delta_y ** 2)
                total_length += segment_length

        self.total_length = total_length
        self.average_radius = total_radius / len(self.pixel_list)

    def remove_edge_root(self):
        """
        Remove a root from its parent's branch list.
        :return: Returns the parent if it is now an edge root itself, and None otherwise.
        """

        to_remove = None

        # Find this in the parent's branch list
        if self.parent_root:
            for branch_tuple in self.parent_root.branch_list:
                if branch_tuple[1] is self:
                    to_remove = branch_tuple
                    break

        if to_remove:
            self.parent_root.branch_list.remove(to_remove)

        if self.parent_root.branch_list:
            return None
        else:
            return self.parent_root

    def score_candidate_branch(self, other):
        """
        Calculates the fit between this root and the branch root
        :param other: The branch root to calculate the fit with
        :return: a float between 0 and 100 inclusive, where 100 is a perfect fit
        """
        # The maximum difference in radius between self and other to earn any radius score
        max_allowable_radius_difference = 4
        # Weights on the components of the final score
        vector_weight = 0.50
        radius_weight = 1 - vector_weight

        # Find the direction trend of the current region of each root
        vector_near_end_self = self.get_ending_direction_vector()
        vector_near_start_other = other.get_starting_direction_vector()

        if vector_near_end_self and vector_near_start_other:

            # Find the angle between the direction vectors
            dot = (vector_near_end_self[0]*vector_near_start_other[0] + vector_near_end_self[1]*vector_near_start_other[1])
            len_self = math.sqrt(vector_near_end_self[0]**2 + vector_near_end_self[1]**2)
            len_other = math.sqrt(vector_near_start_other[0]**2 + vector_near_start_other[1]**2)
            angle_cos = dot/(len_other*len_self)
            angle_radians = math.acos(angle_cos)

            # Score the direction component out of 100
            vector_score = 100 - 100*(angle_radians/(2*math.pi))

        else:

            # Handle 1-length roots
            vector_score = 50

        # Get the average radii in the area of interest
        average_end_radius_self = self.get_average_end_radius()
        average_start_radius_other = other.get_average_start_radius()

        # Score the radius component out of 100
        radius_difference = abs(average_end_radius_self - average_start_radius_other)
        radius_score = max(0, 100 - (100/max_allowable_radius_difference)*radius_difference)

        return vector_weight*vector_score + radius_weight*radius_score

    def get_starting_direction_vector(self):
        """
        Gets the general direction represented by the first few pixels of this root
        :return: a (y,x) coordinate pair representing the difference in y and the difference in x between the last pixel
        of interest and the first
        """

        total_length = len(self.pixel_list)

        if total_length < 2:
            return None
        elif total_length < 5:
            delta_x = self.pixel_list[-1].x - self.pixel_list[0].x
            delta_y = self.pixel_list[-1].y - self.pixel_list[0].y
            return delta_y, delta_x
        else:
            delta_x = self.pixel_list[-5].x - self.pixel_list[0].x
            delta_y = self.pixel_list[-5].y - self.pixel_list[0].y
            return delta_y, delta_x

    def get_ending_direction_vector(self):
        """
        Gets the general direction represented by the last few pixels of this root
        :return: a (y,x) coordinate pair representing the difference in y and the difference in x between the last pixel
        of interest and the first
        """

        total_length = len(self.pixel_list)

        if total_length < 2:
            return None
        elif total_length < 5:
            delta_x = self.pixel_list[-1].x - self.pixel_list[0].x
            delta_y = self.pixel_list[-1].y - self.pixel_list[0].y
            return delta_y, delta_x
        else:
            delta_x = self.pixel_list[-5].x - self.pixel_list[-1].x
            delta_y = self.pixel_list[-5].y - self.pixel_list[-1].y
            return delta_y, delta_x

    def get_average_start_radius(self):
        """
        Gets the general radius trend represented by the first few pixels of this root
        :return: a positive float representing the average radius in the area of interest
        """
        total_length = len(self.pixel_list)

        if total_length < 5:
            return self.average_radius
        else:
            total_radius = 0
            for i in range(5):
                total_radius += self.pixel_list[i].radius
            return total_radius/5

    def get_average_end_radius(self):
        """
        Gets the general radius trend represented by the last few pixels of this root
        :return: a positive float representing the average radius in the area of interest
        """
        total_length = len(self.pixel_list)

        if total_length < 5:
            return self.average_radius
        else:
            total_radius = 0
            for i in range(total_length-5, total_length):
                total_radius += self.pixel_list[i].radius
            return total_radius/5