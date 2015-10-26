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

    # Overall system statistics for threshold scaling
    total_length = 0
    average_radius = 0

    def __init__(self, root_dict, all_seed_roots, total_length, average_radius):

        self.root_dict = root_dict
        self.all_seed_roots = all_seed_roots
        self.total_length = total_length
        self.average_radius = average_radius

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
        for seed_root in self.all_seed_roots:

            empty_list = list()
            # send that pixel set to an instance of window_search
            self.window_search(seed_root, empty_list)

    def window_search(self, root, recent_pixels):

        starter_pixels = list()
        branching_dict = dict()
        pixel_idx = 0
        target_length = int(self.total_length/550)
        absolute_threshold = int(5*self.average_radius)
        min_local_threshold = int(1.5*self.average_radius)
        radius_multiplier = 2.5

        # Make deep copy so multiple branches don't overwrite each other
        for pixel in recent_pixels:
            starter_pixels.append(pixel)

        # Generate dict of branch indices
        for branch in root.branch_list:
            if branch[0] in branching_dict:
                branching_dict[branch[0]].append(branch[1])
            else:
                branching_dict[branch[0]]=[branch[1]]

        # construct and iterate over a n pixel window (start with 10? a number dependent on the root length? higher numbers will yield more positives)

        total_radius = 0
        for n in starter_pixels:
            total_radius += n.radius

        # at branch points where the branch has length of at least z , spin off a new function and feed it the most recent n-1 radii
        # track the current total radius and a list of radii that match the window for efficient recalculation
        # pop the oldest pixel, add a new one to the other end, then check the status of the pixel at index n/2
        # when a pixel is more than m times the average radius of the window, flag it (start with 2? lower numbers will yield more positives)
        # when x out of y pixels are flagged, declare a nodule at all of them (including any unflagged) (start with 4/5? lower numbers will yield more positives)

        recent_nodules = [False, False, False]

        while pixel_idx < len(root.pixel_list):

            # pop the first/oldest element from the window if the window has ramped up to the correct length
            if starter_pixels and len(starter_pixels) >= target_length:
                outgoing = starter_pixels.pop(0)
                total_radius -= outgoing.radius

            # append a new pixel to the end
            starter_pixels.append(root.pixel_list[pixel_idx])
            total_radius += root.pixel_list[pixel_idx].radius

            branched = False
            # check if you should branch here
            if pixel_idx in branching_dict:
                for out_root in branching_dict[pixel_idx]:
                    if len(out_root.pixel_list) > 2:
                        branched = True
                        self.window_search(out_root, recent_pixels)

            # check if this is nodule-like
            average_radius = total_radius/len(starter_pixels)
            local_threshold = max(radius_multiplier*average_radius, min_local_threshold)
            if starter_pixels[-1].radius > local_threshold and not branched:
                if False not in recent_nodules:
                    self.nodule_set.add(starter_pixels[-1])
                recent_nodules.pop(0)
                recent_nodules.append(True)
            elif starter_pixels[-1].radius > absolute_threshold:
                if False not in recent_nodules:
                    self.nodule_set.add(starter_pixels[-1])
                recent_nodules.pop(0)
                recent_nodules.append(True)
            else:
                recent_nodules.pop(0)
                recent_nodules.append(False)

            # next iteration
            pixel_idx += 1