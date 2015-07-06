# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root_builder.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Builds roots from a pixel_dict skeleton, removes invalid roots, and disentangles them to create an
#               accurate representation of the source root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import root as rt


class RootBuilder:

    # Contains the tree structures being built in the format {(int y, int x) : Pixel}
    # WARNING: This is only a shallow copy of TreeBuilder's pixel_dict, and changes to one affect the other.
    pixel_dict = None

    # Contains the roots that currently exist in the format {int unique_ID : Root}
    root_dict = None

    # A set of Pixel objects representing the seed points of the trees contained in pixel_dict
    all_seed_pixels = None

    # A set of Root objects representing the roots from which all other roots can be accessed
    all_seed_roots = None

    # Statistical information
    total_root_length = None
    average_radius = None

    def __init__(self, pixel_dict, all_seed_pixels):
        self.pixel_dict = pixel_dict
        self.root_dict = dict()
        self.all_seed_pixels = all_seed_pixels
        self.all_seed_roots = set()

    def create_initial_roots(self):
        """

        :return:
        """
        # Trace each tree, one at a time
        for seed in self.all_seed_pixels:

            initial_root = rt.Root([seed])

            self.all_seed_roots.add(initial_root)

            root_queue = {initial_root}

            while root_queue:
                for output_root in self.trace_along_children(root_queue.pop()):
                    root_queue.add(output_root)

    def trace_along_children(self, start_root):

        created_roots = set()

        for current_pixel in start_root.pixel_list[-1].children:

            pixel_list = [start_root.pixel_list[-1]]

            not_at_branch = True
            root_not_ended = True

            while not_at_branch and root_not_ended:

                pixel_list.append(current_pixel)

                if len(current_pixel.children) > 1:
                    not_at_branch = False

                elif not current_pixel.children:
                    root_not_ended = False

                else:
                    for child in current_pixel.children:
                        current_pixel = child

            new_root = rt.Root(pixel_list)

            self.root_dict[len(self.root_dict)] = new_root
            created_roots.add(new_root)
            branch_location = len(start_root.pixel_list) - 1
            start_root.branch_list.append((branch_location, new_root))
            new_root.parent_root = start_root

        return created_roots

    def update_root_statistics_and_totals(self):

        self.average_radius = 0
        self.total_root_length = 0

        total_radius = 0

        for root in self.root_dict.values():

            root.calculate_root_statistics()

            self.total_root_length += root.total_length

            total_radius += root.total_length * root.average_radius

        self.average_radius = total_radius / self.total_root_length

    def update_only_total_statistics(self):

        self.average_radius = 0
        self.total_root_length = 0

        total_radius = 0

        for root in self.root_dict.values():

            self.total_root_length += root.total_length

            total_radius += root.total_length * root.average_radius

        self.average_radius = total_radius / self.total_root_length