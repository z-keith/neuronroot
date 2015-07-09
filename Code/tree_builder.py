# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       tree_builder.py
#   author=     Zackery Keith
#   date=       Jul 2 2015
#   purpose=    Adds parent-child relationships to a pixel_dict full of area relationships, and prunes those areas down
#               to representative 1-px wide skeletons
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from Code import config


class TreeBuilder:

    # Contains the tree structures being built in the format {(int y, int x) : Pixel}
    # WARNING: This is only a shallow copy of AreaBuilder's pixel_dict, and changes to one affect the other.
    # This is also copied by RootBuilder, and is likely to be unreliable after RootBuilder is initialized.
    pixel_dict = None

    # A Pixel object that best approximates a user's click location. Is the most reliable starting point for tree
    # building and root tracing
    best_pixel = None

    # A set consisting of best_pixel and the automatically generated seed points for any auxiliary trees
    all_seed_pixels = None

    # Pixel counts, for statistical output purposes
    initial_pixel_count = None
    previous_pixel_count = None

    # Trash set for handling deletion from pixel_dict when other functions are iterating over it.
    # TODO: implement a better way to handle trash, like in right_angles
    trash = None

    def __init__(self, pixel_dict):
        self.pixel_dict = pixel_dict
        self.all_seed_pixels = set()
        self.trash = set()
        self.initial_pixel_count = len(pixel_dict)
        self.previous_pixel_count = len(pixel_dict)

    def find_best_pixel(self, click_location):
        """
        Finds the ideal seed point location near the user's click location
        :param click_location: Tuple of form (int y, int x) with both values positive. Represents the location on the
        image that was clicked.
        :return: Nothing.
        """
        key_range = 0
        looking_for_seed_pixel = True

        while looking_for_seed_pixel:
            for x in range(click_location[1] - key_range, click_location[1] + key_range + 1):
                for y in range(click_location[0] - key_range, click_location[0] + key_range + 1):
                    key = (y, x)
                    if key in self.pixel_dict:
                        largest_local = self.find_local_max_radius(self.pixel_dict[key])
                        return largest_local
                    else:
                        key_range += 1

    @staticmethod
    def find_local_max_radius(start_pixel):
        """
        Finds the local maximum of radius, to find the center-most point of the local root. This function will not
        traverse neighbors of equal or lesser radius. This keeps the output point near the click point and keeps the
        code simple.
        :param start_pixel: The Pixel object to start the search from
        :return: The largest Pixel encountered by the function
        """
        larger_neighbor_exists = True
        largest_local = start_pixel

        while larger_neighbor_exists:
            larger_neighbor_exists = False

            for neighbor in largest_local.neighbors:
                if neighbor and neighbor.radius > largest_local.radius:
                    largest_local = neighbor
                    larger_neighbor_exists = True

        return largest_local

    def find_small_areas(self):
        """
        Iterates over the pixel_dict, calling check_area_for_size on each disjoint area it finds. If an area is large
        enough, its candidate seed point is added to the set of all_seed_pixels. If not, all its member pixels
        are removed.
        :return: Nothing.
        """
        for pixel in self.pixel_dict.values():

            if None not in pixel.neighbors:

                if not pixel.is_visited:

                    if self.check_area_for_size(pixel):
                        self.all_seed_pixels.add(pixel)

        # Take out trash (avoid repeat deletion attempts!)
        self.remove_pixels(self.trash)
        self.trash = set()

    def check_area_for_size(self, start_pixel):
        """
        Iteratively add the neighbors of a set of pixels to an overall pixel set. If their total area is too small to
        be considered a significant tree, remove all pixels in the pixel set.
        :param start_pixel: The pixel to start the area tracing from.
        :return: True if the area is valid, False otherwise.
        """
        # TODO: rewrite this to keep a pixel count and break immediately upon reaching config.minimum_tree_size

        pixel_set = {start_pixel}

        previous_set = {start_pixel}

        current_set = set()
        for neighbor in start_pixel.neighbors:
            if neighbor:
                current_set.add(neighbor)

        next_set_exists = False

        if current_set:
            next_set_exists = True

        while next_set_exists:

            next_set = set()

            for pixel in current_set:
                pixel.is_visited = True
                for neighbor in pixel.neighbors:
                    if neighbor and (neighbor not in previous_set) and (neighbor not in current_set):
                            if not neighbor.is_visited:
                                next_set.add(neighbor)
                                pixel_set.add(neighbor)

            if not next_set:
                next_set_exists = False
            else:
                previous_set = current_set
                current_set = next_set

        if len(pixel_set) < config.minimum_tree_size:
            for pixel in pixel_set:
                self.trash.add(pixel)
            return False
        else:
            return True

    #TODO: Find a way to make prune_redundant_pixels deterministic (currently varies by about 1%)
    def prune_redundant_pixels(self):
        """
        Iteratively strips the outermost set of pixels from the dictionary, leaving only those touching black space on
        at least two sides. This necessarily leaves a line of width 1 px at the midpoint of the root (and a lot of other
        intricate-garbage offshoots we'll deal with in the next several steps)
        :return: Nothing.
        """
        current_set = set()
        current_radius_value = 0

        # Build initial edge set
        for pixel in self.pixel_dict.values():
            if pixel.radius == current_radius_value:
                current_set.add(pixel)

        # Iteratively build the next set and call check_if_skeleton on the current set, removing pixels that aren't part
        # of the skeleton
        while current_set:
            current_radius_value += 1

            next_set = set()

            for pixel in current_set:

                for neighbor in pixel.neighbors:
                    if neighbor and neighbor.radius == current_radius_value:
                        if neighbor not in current_set:
                            next_set.add(neighbor)

                if not self.check_if_skeleton(pixel):
                    self.remove_pixel(pixel)

            current_set = next_set

    def check_if_skeleton(self, pixel):
        """
        Breaks a pixel's neighbors into lists of the location of neighbors and black space, and calls check_sequences to
        analyze if the pixel is a skeleton pixel or not.
        :param pixel: The Pixel up for analysis.
        :return: The result of check_sequences(pixel's neighbor's locations), unless the node is completely surrounded
        by black space, which yields False.
        """
        pixel_loc_list = []

        # Create a list of the locations pixel has neighbors. Locations are identified by the numbers assigned to them
        # in the pixel.py file the class was defined in (clockwise from northwest, starting at 0)
        for i in range(8):
            if pixel.neighbors[i]:
                pixel_loc_list.append(i)

        if not pixel_loc_list:
            return False
        else:
            return self.check_sequences(pixel_loc_list)

    @staticmethod
    def check_sequences(loc_list):
        """
        Find out how many times the sequence of neighbor locations is broken (i.e. how many places this node touches
        black space.)
        :param loc_list: A list of neighbor locations, starting from northwest at 0 and proceeding clockwise.
        :return: True if this location list represents a skeletal node, False otherwise
        """
        # Do not allow nodes with only a single diagonal attachment
        if len(loc_list) == 1:
            if loc_list[0] % 2:
                return False

        sequence_count = 0
        # Account for the possibility of a sequence breaking between 7 and 0
        if loc_list[0] is not 0 or loc_list[-1] is not 7:
            sequence_count += 1

        # Find every interruption in a linear progression of locations, recording each as a broken sequence
        for i in range(len(loc_list) - 1):
            if loc_list[i+1] - loc_list[i] is not 1:
                sequence_count += 1

        # Return True for lists representing multiple sequences
        return sequence_count > 1

    def prune_internal_pixels(self):
        """
        Removes any pixels that are completely covered by a neighboring pixel.
        :return: Nothing.
        """
        current_set = set()
        current_radius = 0
        for pixel in self.pixel_dict.values():
            if pixel.radius == current_radius:
                current_set.add(pixel)

        while current_set:
            next_set = set()
            for pixel in current_set:

                pixel_is_covered = False

                # Check if any of this pixel's neighbors have a larger radius than this
                # Because of the method used to assign radii, a neighbor with a radius one larger than the current
                # pixel's is guaranteed to cover all the area that the original pixel does
                for neighbor in pixel.neighbors:
                    if neighbor and neighbor.radius > pixel.radius:
                        next_set.add(neighbor)
                        pixel_is_covered = True

                if pixel_is_covered:
                    self.remove_pixel(pixel)

            current_set = next_set

    def set_tree_relationships(self):
        """
        Sets parent-child relationships through all remaining areas of the dictionary. It's assumed that the head of the
        tree is represented by its seed point.
        :return: Nothing.
        """
        # Ensure that the seed pixels haven't been removed and update them if they have
        # TODO: change all_seed_pixels to store locations, not nodes. Write a function to return the set of pixels
        # represented by the seed_pixels
        new_seed_pixels = set()
        for pixel in self.all_seed_pixels:
            key = (pixel.y, pixel.x)
            new_seed = self.find_best_pixel(key)
            new_seed_pixels.add(new_seed)
        self.all_seed_pixels = new_seed_pixels

        previous_set = set()
        current_set = self.all_seed_pixels
        while current_set:
            next_set = set()
            for pixel in current_set:
                for neighbor in pixel.neighbors:
                    if neighbor and neighbor not in current_set and neighbor not in previous_set:
                        if not neighbor.parents:
                            pixel.set_child(neighbor)
                            next_set.add(neighbor)
            previous_set = current_set
            current_set = next_set

    def remove_right_angles(self):
        """
        Removes certain inefficient connection patterns that make some roots appear to have 2-pixel wide skeletons
        :return: Nothing.
        """
        all_pixels = set()

        for pixel in self.pixel_dict.values():
            all_pixels.add(pixel)

        for pixel in all_pixels:

            loc_list = []

            for i in range(8):
                if pixel.neighbors[i]:
                    loc_list.append(i)

            invalid_l_trees = [[1, 3], [3, 5], [5, 7], [1, 7]]

            if len(loc_list) == 2:
                if loc_list in invalid_l_trees:
                    self.remove_pixel(pixel)

            invalid_t_trees = [[1, 3, 5], [3, 5, 7], [1, 5, 7], [1, 3, 7]]

            invalid_z_trees = [[0, 1, 3], [0, 5, 7], [1, 2, 7], [1, 3, 4], [1, 6, 7], [2, 3, 5], [3, 5, 6], [4, 5, 7]]

            if len(loc_list) == 3:
                if loc_list in invalid_t_trees:
                    self.remove_pixel(pixel)
                elif loc_list in invalid_z_trees:
                    self.remove_pixel(pixel)

            invalid_w_trees = [[0, 1, 3, 4], [0, 4, 5, 7], [1, 2, 6, 7], [2, 3, 5, 6]]

            if len(loc_list) == 4:
                if loc_list in invalid_w_trees:
                    self.remove_pixel(pixel)

    def remove_pixels(self, pixel_set):
        """
        Iteratively sends pixels from a set to remove_pixel
        :param pixel_set: A set of pixel objects slated for removal
        :return: Nothing.
        """
        for pixel in pixel_set:
            self.remove_pixel(pixel)

    def remove_pixel(self, pixel):
        """
        Cleanly remove all references to a Pixel object, while preserving overall tree structure. This is like deleting
        the pixel, but without those nasty errors when a former neighbor references it.
        :param pixel: The pixel to be removed.
        :return: Nothing.
        """
        key = (pixel.y, pixel.x)

        if pixel.children:
            for child in pixel.children:
                child.parents.discard(pixel)

        if pixel.parents:
            for parent in pixel.parents:
                parent.children.discard(pixel)

        if pixel.children and pixel.parents:
            for child in pixel.children:
                for parent in pixel.parents:
                    parent.set_child(child)

        for i in range(8):
            if pixel.neighbors[i]:
                neighbor = pixel.neighbors[i]
                this_pixel_loc = (i+4) % 8
                neighbor.neighbors[this_pixel_loc] = None

        self.pixel_dict.pop(key, None)
