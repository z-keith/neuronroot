# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root_builder.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Builds roots from a pixel_dict skeleton, removes invalid roots, and disentangles them to create an
#               accurate representation of the source root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# noinspection PyUnresolvedReferences
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
        Creates initial set of roots. On this pass, roots end whenever they meet a branching point, which yields two or
        more child roots.
        :return:
        """

        # Trace each tree, one at a time
        initial_roots = []

        for seed in self.all_seed_pixels:

            initial_root = rt.Root([seed], len(self.root_dict))
            self.root_dict[len(self.root_dict)] = initial_root

            self.all_seed_roots.add(initial_root)
            initial_roots.append(initial_root)

            # Iteratively create all child roots from the initial point
        root_queue = initial_roots
        while root_queue:
            for output_root in self.trace_along_children(root_queue.pop(0)):
                root_queue.append(output_root)

    def trace_along_children(self, start_root):
        """

        :param start_root: A Root to find children of
        :return: The roots created as offshoots of start_root, as a set. They're passed back into the root_queue in
        create_initial_roots to be used as start_roots in the future.
        """

        created_roots = []

        # Not it
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
                    # get the single child from the set
                    for child in current_pixel.children:
                        current_pixel = child

            new_root = rt.Root(pixel_list, len(self.root_dict))

            # Connect the parent root to the new root
            branch_location = len(start_root.pixel_list) - 1
            start_root.branches_at_endpoint.append(new_root)
            start_root.branch_list.append((branch_location, new_root))
            new_root.parent_root = start_root

            # Add the new root to the dictionary for future use and to the return set
            self.root_dict[len(self.root_dict)] = new_root
            created_roots.append(new_root)

        # Not it
        return created_roots

    def remove_short_roots(self):
        """
        Remove 'roots' that are relatively too short to truly represent roots. These tend to show up as perpendicular
        roots within real roots,
        :return: Nothing.
        """

        # Proportion of the branch point's radius that the total length has to be to avoid removal.
        # Lower multipliers remove less incorrect roots, but also don't incorrectly remove real roots
        radius_multiplier = 0

        edge_roots = []

        for root in self.root_dict.values():
            if not root.branches_at_endpoint:
                edge_roots.append(root)

        while edge_roots:

            next_root_list = []

            for root in edge_roots:

                if root and len(root.pixel_list) < radius_multiplier * root.pixel_list[0].radius and root.parent_root:

                    self.remove_pixels(root.pixel_list)

                    parent = root.remove_edge_root()
                    if parent and not parent.branches_at_endpoint:
                        next_root_list.append(parent)

                    self.root_dict.pop(root.key, None)

            edge_roots = next_root_list

    def set_remaining_lengths(self):
        """

        :return:
        """

        current_list = []

        for root in self.root_dict.values():
            if not root.branches_at_endpoint:
                current_list.append(root)

        while current_list:

            next_list = []

            for root in current_list:

                if root.remaining_length_ready():
                    length_list = []
                    for branch in root.branches_at_endpoint:
                        length_list.append(branch.remaining_length)

                    if length_list:
                        root.remaining_length = max(length_list) + root.total_length
                    else:
                        root.remaining_length = root.total_length

                    if root.parent_root:
                        next_list.append(root.parent_root)

                else:
                    next_list.append(root)

            current_list = next_list


    def untangle_roots(self):
        """
        Connects the many root segments created by create_initial_roots into coherent roots based on their orientation,
        length, and radius.
        :return: Nothing. Upon successful completion, all_seed_roots can be traced to create the final representation
        """

        for root in self.all_seed_roots:
            root_queue = [root]
            while root_queue:
                for output_root in self.connect_roots(root_queue.pop(0)):
                    root_queue.append(output_root)

    def connect_roots(self, start_root):
        """

        :param start_root:
        :return:
        """
        next_roots = []
        to_attach = (-1, None)

        if not start_root.branches_at_endpoint:
            pass

        elif len(start_root.branches_at_endpoint) == 1:
            to_attach = (100, start_root.branches_at_endpoint[0])

        else:
            for root in start_root.branches_at_endpoint:
                # score = start_root.score_candidate_branch(root)
                score = root.remaining_length
                if score > to_attach[0]:
                    to_attach = (score, root)

        if to_attach[1]:

            next_roots.append(start_root)

            for root in start_root.branches_at_endpoint:
                if root is not to_attach[1]:
                    next_roots.append(root)

            for root in to_attach[1].branches_at_endpoint:
                next_roots.append(root)

            removal_key = start_root.combine(to_attach[1])
            self.root_dict.pop(removal_key, None)

        return next_roots


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