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

    def find_by_windows(self):

        # start from seed points
        # build a pixel set up to length n or the first branch, whichever is first
        # send that pixel set to an instance of window_search

    def window_search(self, recent_pixels):

        # iterate over a n pixel window (start with 30? a number dependent on the root length? higher numbers will yield more positives)
        # add pixels from the beginning of this root until recent_pixels + new pixels = n
        # track the current total radius and a list of radii that match the window for efficient recalculation
        # pop the oldest pixel, add a new one to the other end, then check the status of the pixel at index n/2
        # when a pixel is more than m times the average radius of the window, flag it (start with 2? lower numbers will yield more positives)
        # when x out of y pixels are flagged, declare a nodule at all of them (including any unflagged) (start with 4/5? lower numbers will yield more positives)
        # at branch points, spin off a new function and feed it the most recent n-1 radii