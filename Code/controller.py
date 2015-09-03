# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       controller.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Mediates the interaction of the Builder classes, the printer, and the user interface for a single file
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import time

# noinspection PyUnresolvedReferences
import tree_builder
# noinspection PyUnresolvedReferences
import array_builder
# noinspection PyUnresolvedReferences
import root_builder
# noinspection PyUnresolvedReferences
import printer
# noinspection PyUnresolvedReferences
import config
# noinspection PyUnresolvedReferences
import area_builder


class Controller:

    printer = None

    array_builder = None

    area_builder = None

    tree_builder = None

    root_builder = None

    # Time objects for performance tracking
    start_time = None
    last_time = None

    def __init__(self):

        config.initialize()
        self.start_time = time.time()
        self.last_time = time.time()

    def load_image_to_array(self):
        """
        Function to handle the ArrayBuilder's image loading and filtering functions
        :return: Nothing. Upon successful completion, array_builder.array contains a representation of the input image.
        """

        print("\nLoading image {0}:".format(config.file_name))
        self.array_builder = array_builder.ArrayBuilder(config.file_name)

        self.array_builder.load_to_array()
        print("- Loaded image to array in {0}".format(self.print_timestamp()))
        print("\t- Image size: {0}x{1}".format(self.array_builder.image_width, self.array_builder.image_height))

        self.array_builder.filter_array()
        self.array_builder.mask_ruler()
        print("- Filtered and masked array in {0}".format(self.print_timestamp()))

    def build_areas(self):
        """
        Function to handle the AreaBuilder's Pixel creation and neighbor-detection functions
        :return: Nothing. Upon successful completion, area_builder.pixel_dict represents all bright pixels in the image.
        """

        print("\nConstructing pixels and areas:")
        self.area_builder = area_builder.AreaBuilder()

        self.area_builder.load_pixels(self.array_builder.array)
        print("- Constructed pixel_dict in {0}".format(self.print_timestamp()))
        print("\t- Total area found on first pass: {0} px.".format(len(self.area_builder.pixel_dict)))

        self.area_builder.find_neighbors()
        print("- Added neighbors in {0}".format(self.print_timestamp()))

        self.area_builder.set_radii()
        print("- Set radii in {0}".format(self.print_timestamp()))

    def print_background(self):
        """
        Function to print a faint background of the original image to a file for error checking.
        :return: Nothing. Upon successful completion, printer.array contains the faint background to be drawn on later.
        """

        print("\nPrinting initial area's outline:")
        self.printer = printer.Printer(self.array_builder.array.shape)

        self.printer.print_original_image(self.area_builder.pixel_dict)
        print("- Printed gray outline in {0}".format(self.print_timestamp()))

    def build_trees(self):
        """
        Function to iteratively prune the pixels in pixel_dict until only a 1px-wide skeleton remains to represent the
        original image. This skeleton has parent-child relationships set up already.
        :return: Nothing. Upon successful completion, tree_builder.pixel_dict contains the skeleton and
        tree_builder.all_seed_pixels contains the starting points of each tree.
        """

        print("\nPruning areas down to trees:")
        self.tree_builder = tree_builder.TreeBuilder(self.area_builder.pixel_dict)

        self.tree_builder.best_pixel = self.tree_builder.find_best_pixel(config.seedYX)
        self.tree_builder.all_seed_pixels.add(self.tree_builder.best_pixel)
        print("- Found best approximation for click point in {0}".format(self.print_timestamp()))
        print("\t- Best approximation found for click point: ({0}, {1}) with radius of {2}".format(
            self.tree_builder.best_pixel.x, self.tree_builder.best_pixel.y, self.tree_builder.best_pixel.radius))

        self.tree_builder.find_small_areas()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        print("- Removed small areas in {0}".format(self.print_timestamp()))
        print("\t- Total small area removed: {0} px ({1}% of original area)".format(removal_count, removed_percentage))

        self.tree_builder.prune_redundant_pixels()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        print("- Removed redundant areas in {0}".format(self.print_timestamp()))
        print("\t- Total redundant area removed: {0} px ({1}% of original area)".format(removal_count,
                                                                                        removed_percentage))

        self.tree_builder.set_tree_relationships()
        print("- Set parent-child relationships for trees in {0}".format(self.print_timestamp()))

        # self.tree_builder.prune_internal_pixels()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        print("- Removed internal areas in {0}".format(self.print_timestamp()))
        print("\t- Total internal area removed: {0} px ({1}% of original area)".format(removal_count,
                                                                                       removed_percentage))

        self.tree_builder.remove_right_angles()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        print("- Removed inefficient right-angle connections in {0}".format(self.print_timestamp()))
        print("\t- Total inefficient connection area removed: {0} px ({1}% of original area)"
              .format(removal_count, removed_percentage))

        compression_percentage = round(100 * (1 - len(self.tree_builder.pixel_dict) /
                                              self.tree_builder.initial_pixel_count), 1)
        print("- Total pixels in final area representation: {0}".format(self.tree_builder.previous_pixel_count))
        print("\t- Total compression: {0}%".format(compression_percentage))

    def print_skeleton(self):
        """
        Calls the existing printer to print the colorized skeletons of the trees stored in the tree_builder.
        :return: Nothing. Upon successful run, the output image can be found in the same directory as the original,
        with "-skeleton" appended to its filename
        """

        print("\nPrinting skeleton onto gray outline:")
        self.printer.print_skeletal_outline(self.tree_builder.all_seed_pixels)
        print("\t- Printed skeletal outline in {0}".format(self.print_timestamp()))

    def build_roots(self):
        """
        Function to build a series of Root objects to represent the trees in a pixel_dict. It creates the roots, removes
        short invalid roots, and untangles them by correctly combining them into longer roots.
        :return: Nothing. Upon successful completion, root_builder.root_dict contains all the roots, and
        root_builder.all_seed_roots contains the start points to use them.
        """

        print("\nBuilding root structures:")
        self.root_builder = root_builder.RootBuilder(self.tree_builder.pixel_dict, self.tree_builder.all_seed_pixels)

        self.root_builder.create_initial_roots()
        initial_root_count = len(self.root_builder.root_dict)
        print("- Constructed initial roots in {0}"
              .format(self.print_timestamp()))
        print("\t- Total number of initial roots: {0}"
              .format(initial_root_count))

        self.root_builder.update_root_statistics_and_totals()
        initial_root_length = round(self.root_builder.total_root_length, 1)
        initial_average_radius = round(self.root_builder.average_radius, 1)
        print("- Calculated initial root average radii and total lengths in {0}"
              .format(self.print_timestamp()))
        print("\t- Total root length (unrefined): {0} px."
              .format(initial_root_length))
        print("\t- Overall average radius (unrefined): {0} px."
              .format(initial_average_radius))

        self.root_builder.remove_short_roots()
        removed_short_roots = initial_root_count - len(self.root_builder.root_dict)
        removed_percentage = round(100 * (removed_short_roots / initial_root_count), 1)
        print("- Removed invalid short roots in {0}"
              .format(self.print_timestamp()))
        print("\t- Total short roots removed: {0} ({1}% of original count)"
              .format(removed_short_roots, removed_percentage))

        self.root_builder.update_only_total_statistics()
        removed_short_length = round(initial_root_length - self.root_builder.total_root_length, 1)
        removed_short_radius_percent_of_initial = round(100*self.root_builder.average_radius/initial_average_radius, 1)
        print("- Calculated post-removal root average radii and total lengths in {0}"
              .format(self.print_timestamp()))
        print("\t- Total root length removed: {0} px. ({1}% of original length)"
              .format(removed_short_length, round(100*removed_short_length/initial_root_length, 1)))
        print("\t- Overall average radius: {0} px. ({1}% of original value)"
              .format(round(self.root_builder.average_radius, 1), removed_short_radius_percent_of_initial))

        self.root_builder.set_remaining_lengths()
        print("- Set remaining lengths for each root in {0}"
              .format(self.print_timestamp()))

        self.root_builder.untangle_roots()
        roots_lost_to_combination = initial_root_count - removed_short_roots - len(self.root_builder.root_dict)
        removed_percentage = round(100 * (roots_lost_to_combination / initial_root_count), 1)
        print("- Combined and untangled roots in {0}"
              .format(self.print_timestamp()))
        print("\t- Roots lost to combination: {0} ({1}% of original count)"
              .format(roots_lost_to_combination, removed_percentage))
        print("\t- Final root count: {0}"
              .format(len(self.root_builder.root_dict)))

        self.root_builder.update_root_statistics_and_totals()
        print("- Calculated final root average radii and total lengths in {0}"
              .format(self.print_timestamp()))
        print("\t- Final total root length: {0} px."
              .format(round(self.root_builder.total_root_length, 1)))
        print("\t- Overall average radius : {0} px."
              .format(round(self.root_builder.average_radius, 1)))

        print("- Final statistics:")
        print("\t- Total root length: {0} cm."
              .format(round(self.root_builder.total_root_length*config.cm_per_pixel, 2)))
        print("\t- Overall average diameter : {0} cm."
              .format(round(2*self.root_builder.average_radius*config.cm_per_pixel, 4)))

    def print_roots(self):

        print("\nPrinting root representation:")
        self.printer.print_by_root(self.root_builder.all_seed_roots)
        print("\t- Printed root representation in {0}".format(self.print_timestamp()))

    def print_timestamp(self):
        """
        Creates a representation of the time since the last time this function was called
        :return: a string such as "3 minutes and 1.71 seconds"
        """

        # Find and parse minutes and seconds since last time
        elapsed = time.time() - self.last_time
        minutes = int(elapsed / 60)
        seconds = round((elapsed % 60), 2)

        # Handle grammar for special times
        plural_min = "s"
        plural_sec = "s"
        if minutes == 1:
            plural_min = ""
        if seconds == 1.00:
            plural_sec = ""

        # Update last_time
        self.last_time = time.time()

        return "{0} minute{1} and {2} second{3}.".format(minutes, plural_min, seconds, plural_sec)

    def print_total_time(self):
        """
        Creates a representation of the time since the program started
        :return: a string such as "3 minutes and 1.71 seconds"
        """

        # Find and parse minutes and seconds since last time
        elapsed = time.time() - self.start_time
        minutes = int(elapsed / 60)
        seconds = round((elapsed % 60), 2)

        # Handle grammar for special times
        plural_min = "s"
        plural_sec = "s"
        if minutes == 1:
            plural_min = ""
        if seconds == 1.00:
            plural_sec = ""

        # Update last_time
        self.last_time = time.time()

        return "{0} minute{1} and {2} second{3}.".format(minutes, plural_min, seconds, plural_sec)
