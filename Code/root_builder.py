# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root_builder.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Builds roots from a pixel_dict skeleton, removes invalid roots, and disentangles them to create an
#               accurate representation of the source root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from Code import root as rt


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
        Creates initial set of roots. On this pass, roots end whenever they meet a branching point, which yields two or
        more child roots.
        :return:
        """

        # Trace each tree, one at a time
        for seed in self.all_seed_pixels:

            initial_root = rt.Root([seed], len(self.root_dict))
            self.root_dict[len(self.root_dict)] = initial_root

            self.all_seed_roots.add(initial_root)

            # Iteratively create all child roots from the initial point
            root_queue = {initial_root}
            while root_queue:
                for output_root in self.trace_along_children(root_queue.pop()):
                    root_queue.add(output_root)

    def trace_along_children(self, start_root):
        """

        :param start_root: A Root to find children of
        :return: The roots created as offshoots of start_root, as a set. They're passed back into the root_queue in
        create_initial_roots to be used as start_roots in the future.
        """

        created_roots = set()

        for current_pixel in start_root.pixel_list[-1].children:

            # Build a pixel_list to the next branch or endpoint
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

            new_root = rt.Root(pixel_list, len(self.root_dict))

            # Connect the parent root to the new root
            branch_location = len(start_root.pixel_list) - 1
            start_root.branch_list.append((branch_location, new_root))
            new_root.parent_root = start_root

            # Add the new root to the dictionary for future use and to the return set
            self.root_dict[len(self.root_dict)] = new_root
            created_roots.add(new_root)

        return created_roots

    def remove_short_roots(self):
        """
        Remove 'roots' that are relatively too short to truly represent roots. These tend to show up as perpendicular
        roots within real roots,
        :return: Nothing.
        """

        # Proportion of the branch point's radius that the total length has to be to avoid removal.
        # Lower multipliers remove less incorrect roots, but also don't incorrectly remove real roots
        radius_multiplier = 2.5

        edge_roots = set()

        for root in self.root_dict.values():
            if not root.branch_list:
                edge_roots.add(root)

        while edge_roots:

            next_root_set = set()

            for root in edge_roots:

                if root and len(root.pixel_list) < radius_multiplier * root.pixel_list[0].radius:

                    self.remove_pixels(root.pixel_list)

                    parent = root.remove_edge_root()
                    next_root_set.add(parent)

                    self.root_dict.pop(root.key, None)

            edge_roots = next_root_set

    def untangle_roots(self):
        """

        :return:
        """
        pass

    def update_root_statistics_and_totals(self):
        """
        Recalculates the statistics for each individual root, then calculates the aggregate statistics.
        :return: Nothing.
        """

        self.average_radius = 0
        self.total_root_length = 0

        total_radius = 0

        for root in self.root_dict.values():

            root.calculate_root_statistics()

            self.total_root_length += root.total_length

            total_radius += root.total_length * root.average_radius

        self.average_radius = total_radius / self.total_root_length

    def update_only_total_statistics(self):
        """
        Only recalculates the aggregate statistics- use only when roots have been deleted, but not changed.
        :return: Nothing.
        """

        self.average_radius = 0
        self.total_root_length = 0

        total_radius = 0

        for root in self.root_dict.values():

            self.total_root_length += root.total_length

            total_radius += root.total_length * root.average_radius

        self.average_radius = total_radius / self.total_root_length

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
        Cleanly remove all references to a Pixel object, without preserving overall tree structure. This is like
        deleting the pixel, but without those nasty errors when a former neighbor references it.
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

        for i in range(8):
            if pixel.neighbors[i]:
                neighbor = pixel.neighbors[i]
                this_pixel_loc = (i+4) % 8
                neighbor.neighbors[this_pixel_loc] = None

        self.pixel_dict.pop(key, None)