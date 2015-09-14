# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       nodule_finder.py
#   author=     Zackery Keith
#   date=       Sep 8 2015
#   purpose=    Finds likely nodule locations in a Root-based reconstruction of the root system
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class NoduleFinder:

    # Dictionary of form (ID: Root) containing all Roots that represent the image
    # WARNING: This is only a shallow copy of RootBuilder's root_dict, and changes to one affect the other.
    root_dict = None

    # A set of Root objects representing the roots from which all other roots can be accessed
    all_seed_roots = None

    # A set of Pixel objects representing the nodules found in the image
    nodule_set = None

    def __init__(self, root_dict, all_seed_roots):

        self.root_dict = root_dict
        self.all_seed_roots = all_seed_roots

        self.nodule_set = set()

    def find_by_thresholds(self, global_average_radius):

        # Set the absolute threshold
        global_radius_threshold_multiplier = 10
        global_radius_threshold = global_radius_threshold_multiplier * global_average_radius

        # Set the multiplier for the local radius threshold
        local_radius_threshold_multiplier = 1.5

        # Set the minimum radius of a nodule pixel
        minimum_nodule_radius = 12

        # Iterate through all roots of significant length and find pixels with radius greater than either threshold
        significant_root_length = 7  # Measured in number of pixels

        for root in self.root_dict.values():
            if len(root.pixel_list) > significant_root_length:

                local_radius_threshold = local_radius_threshold_multiplier * root.average_radius
                if local_radius_threshold < minimum_nodule_radius:
                    local_radius_threshold = minimum_nodule_radius

                for pixel in root.pixel_list:
                    if pixel.radius > global_radius_threshold:
                        self.nodule_set.add(pixel)
                    elif pixel.radius > local_radius_threshold:
                        self.nodule_set.add(pixel)
