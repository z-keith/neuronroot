# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       controller.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Mediates the interaction of the Builder classes, the printer, and the user interface for a single file
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import time, math
from PyQt4.QtCore import pyqtSignal, QObject
from PIL import Image

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
# noinspection PyUnresolvedReferences
import nodule_finder

class Controller(QObject):

    printer = None

    array_builder = None

    area_builder = None

    tree_builder = None

    root_builder = None

    nodule_finder = None

    outstring = ""

    # Time objects for performance tracking
    start_time = None
    last_time = None

    # Debug/testing objects
    total_area = None
    calculated_average_diameter = None
    expected_length = None
    total_length = None
    nodule_area = None
    log_string = ""

    # Updated signal
    image_update = pyqtSignal() 
    ui_update = pyqtSignal()
    image_spawned = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)

        self.start_time = time.time()
        self.last_time = time.time()

    def signal_ui_update(self):
        self.ui_update.emit()
        
    def signal_image_update(self):
        self.image_update.emit()

    def load_image_to_array(self):
        """
        Function to handle the ArrayBuilder's image loading and filtering functions
        :return: Nothing. Upon successful completion, array_builder.array contains a representation of the input image.
        """

        self.log_string ="Loading image {0}:".format(config.file_name)
        self.signal_ui_update()
        self.array_builder = array_builder.ArrayBuilder(config.file_name)

        self.array_builder.load_to_array()
        self.log_string = self.log_string + "\n- Loaded image to array in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Detected DPI of {0}".format(config.dpi)
        self.log_string = self.log_string + "\n   - Image size: {0}x{1}".format(self.array_builder.image_width, self.array_builder.image_height)
        self.signal_ui_update()

        self.array_builder.filter_array()
        self.array_builder.mask_ruler()
        self.log_string = self.log_string + "\n- Filtered and masked array in {0}".format(self.print_timestamp())
        self.signal_ui_update()

    def build_areas(self):
        """
        Function to handle the AreaBuilder's Pixel creation and neighbor-detection functions
        :return: Nothing. Upon successful completion, area_builder.pixel_dict represents all bright pixels in the image.
        """

        self.log_string = self.log_string + "\n\nConstructing pixels and areas:"
        self.signal_ui_update()
        self.area_builder = area_builder.AreaBuilder()

        self.area_builder.load_pixels(self.array_builder.array)
        self.log_string = self.log_string + "\n- Constructed pixel_dict in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total area found on first pass: {0} px.".format(len(self.area_builder.pixel_dict))
        self.signal_ui_update()

        self.area_builder.find_neighbors()
        self.log_string = self.log_string + "\n- Added neighbors in {0}".format(self.print_timestamp())
        self.signal_ui_update()

        self.area_builder.set_radii()
        self.log_string = self.log_string + "\n- Set radii in {0}".format(self.print_timestamp())
        self.signal_ui_update()

    def print_background(self):
        """
        Function to print a faint background of the original image to a file for error checking.
        :return: Nothing. Upon successful completion, printer.array contains the faint background to be drawn on later.
        """

        self.log_string = self.log_string + "\n\nPrinting initial area's outline:"
        self.signal_ui_update()
        self.printer = printer.Printer(self.array_builder.array.shape)

        self.printer.print_original_image(self.area_builder.pixel_dict)
        self.log_string = self.log_string + "\n- Printed gray outline in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_ui_update()

    def build_trees(self):
        """
        Function to iteratively prune the pixels in pixel_dict until only a 1px-wide skeleton remains to represent the
        original image. This skeleton has parent-child relationships set up already.
        :return: Nothing. Upon successful completion, tree_builder.pixel_dict contains the skeleton and
        tree_builder.all_seed_pixels contains the starting points of each tree.
        """

        self.log_string = self.log_string + "\n\nPruning areas down to trees:"
        self.signal_ui_update()
        self.tree_builder = tree_builder.TreeBuilder(self.area_builder.pixel_dict)

        self.tree_builder.best_pixel = self.tree_builder.find_best_pixel(config.seedYX)
        self.tree_builder.all_seed_pixels.add(self.tree_builder.best_pixel)
        self.log_string = self.log_string + "\n- Found best approximation for click point in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Best approximation found for click point: ({0}, {1}) with radius of {2}".format(
            self.tree_builder.best_pixel.x, self.tree_builder.best_pixel.y, self.tree_builder.best_pixel.radius)
        self.signal_ui_update()

        self.tree_builder.find_small_areas()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string = self.log_string + "\n- Removed small areas in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total small area removed: {0} px ({1}% of original area)".format(removal_count, removed_percentage)
        self.signal_ui_update()

        self.total_area = float(len(self.tree_builder.pixel_dict)) * config.cm_per_pixel**2 * ((1+math.sqrt(2))/2)

        self.tree_builder.prune_redundant_pixels()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string = self.log_string + "\n- Removed redundant areas in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total redundant area removed: {0} px ({1}% of original area)".format(removal_count,
                                                                                        removed_percentage)
        self.signal_ui_update()

        self.tree_builder.set_tree_relationships()
        self.log_string = self.log_string + "\n- Set parent-child relationships for trees in {0}".format(self.print_timestamp())
        self.signal_ui_update()

        self.tree_builder.remove_right_angles()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string = self.log_string + "\n- Removed inefficient right-angle connections in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total inefficient connection area removed: {0} px ({1}% of original area)".format(removal_count, removed_percentage)
        self.signal_ui_update()

        compression_percentage = round(100 * (1 - len(self.tree_builder.pixel_dict) /
                                              self.tree_builder.initial_pixel_count), 1)
        self.log_string = self.log_string + "\n- Total pixels in final area representation: {0}".format(self.tree_builder.previous_pixel_count)
        self.log_string = self.log_string + "\n   - Total compression: {0}%".format(compression_percentage)
        self.signal_ui_update()

    def print_skeleton(self):
        """
        Calls the existing printer to print the colorized skeletons of the trees stored in the tree_builder.
        :return: Nothing. Upon successful run, the output image can be found in the same directory as the original,
        with "-skeleton" appended to its filename
        """

        self.log_string = self.log_string + "\n\nPrinting skeleton onto gray outline:"
        self.signal_ui_update()
        self.printer.print_skeletal_outline(self.tree_builder.all_seed_pixels)
        self.log_string = self.log_string + "\n   - Printed skeletal outline in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_ui_update()

    def print_test_radii(self):

        self.log_string = self.log_string + "\n\nPrinting test radii:"
        self.signal_ui_update()
        self.printer.print_test_radii(self.area_builder.pixel_dict)
        self.log_string = self.log_string + "\n   - Printed {0} test cases in {1}".format(config.testcase_count, self.print_timestamp())
        self.signal_ui_update()

    def build_roots(self):
        """
        Function to build a series of Root objects to represent the trees in a pixel_dict. It creates the roots, removes
        short invalid roots, and untangles them by correctly combining them into longer roots.
        :return: Nothing. Upon successful completion, root_builder.root_dict contains all the roots, and
        root_builder.all_seed_roots contains the start points to use them.
        """

        self.log_string = self.log_string + "\n\nBuilding root structures:"
        self.signal_ui_update()
        self.root_builder = root_builder.RootBuilder(self.tree_builder.pixel_dict, self.tree_builder.all_seed_pixels)

        self.root_builder.create_initial_roots()
        initial_root_count = len(self.root_builder.root_dict)
        self.log_string = self.log_string + "\n- Constructed initial roots in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total number of initial roots: {0}".format(initial_root_count)
        self.signal_ui_update()

        self.root_builder.update_root_statistics_and_totals()
        initial_root_length = round(self.root_builder.total_root_length, 1)
        initial_average_radius = round(self.root_builder.average_radius, 1)
        self.log_string = self.log_string + "\n- Calculated initial root average radii and total lengths in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Total root length (unrefined): {0} px.".format(initial_root_length)
        self.log_string = self.log_string + "\n   - Overall average radius (unrefined): {0} px.".format(initial_average_radius)
        self.signal_ui_update()

        self.root_builder.set_remaining_lengths()
        self.log_string = self.log_string + "\n- Set remaining lengths for each root in {0}".format(self.print_timestamp())
        self.signal_ui_update()

        self.root_builder.untangle_roots()
        roots_lost_to_combination = initial_root_count - len(self.root_builder.root_dict)
        removed_percentage = round(100 * (roots_lost_to_combination / initial_root_count), 1)
        self.log_string = self.log_string + "\n- Combined and untangled roots in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Roots lost to combination: {0} ({1}% of original count)".format(roots_lost_to_combination, removed_percentage)
        self.log_string = self.log_string + "\n   - Final root count: {0}".format(len(self.root_builder.root_dict))
        self.signal_ui_update()

        self.root_builder.update_root_statistics_and_totals()
        self.log_string = self.log_string + "\n- Calculated final root average radii and total lengths in {0}".format(self.print_timestamp())
        self.log_string = self.log_string + "\n   - Final total root length: {0} px.".format(round(self.root_builder.total_root_length, 1))
        self.log_string = self.log_string + "\n   - Overall average radius: {0} px.".format(round(self.root_builder.average_radius, 1))
        self.signal_ui_update()

        self.log_string = self.log_string + "\n- Final statistics:"
        self.log_string = self.log_string + "\n   - Total root length: {0} cm.".format(round(self.root_builder.total_root_length*config.cm_per_pixel, 2))
        self.log_string = self.log_string + "\n   - Overall average diameter: {0} cm.".format(round(2*self.root_builder.average_radius*config.cm_per_pixel, 4))
        self.signal_ui_update()

        self.calculated_average_diameter = 2*self.root_builder.average_radius*config.cm_per_pixel * ((1+math.sqrt(2))/2)
        self.total_length = self.root_builder.total_root_length*config.cm_per_pixel * ((1+math.sqrt(2))/2)
        self.expected_length = self.total_area/self.calculated_average_diameter * ((1+math.sqrt(2))/2)


    def print_roots(self):

        self.log_string = self.log_string + "\n\nPrinting root representation:"
        self.signal_ui_update()
        self.printer.print_by_root(self.root_builder.all_seed_roots)
        self.log_string = self.log_string + "\n   - Printed root representation in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_ui_update()

    def find_nodules(self):

        self.log_string = self.log_string + "\n\nSearching for nodules:"
        self.signal_ui_update()
        self.nodule_finder = nodule_finder.NoduleFinder(self.root_builder.root_dict, self.root_builder.all_seed_roots, self.root_builder.total_root_length, self.root_builder.average_radius)

        self.nodule_finder.find_by_windows()
        self.log_string = self.log_string + "\n   - Completed threshold-based search in {0}".format(self.print_timestamp())
        self.signal_ui_update()

        self.nodule_count = self.printer.count_nodules(self.nodule_finder.nodule_set)
        self.log_string = self.log_string + "\n   - Counted nodules in {0}".format(self.print_timestamp())
        self.signal_ui_update()
        self.log_string = self.log_string + "\n   - Nodules found: {0}".format(self.nodule_count)
        self.signal_ui_update()

        self.nodule_area = self.printer.count_white_px(self.nodule_finder.nodule_set) * ((1+math.sqrt(2))/2)
        self.log_string = self.log_string + "\n   - Computed nodule area (hacky solution) in {0}".format(self.print_timestamp())
        self.signal_ui_update()
        self.log_string = self.log_string + "\n   - Estimated nodule area: {0} cm^2".format(round(self.nodule_area, 2))
        self.signal_ui_update()


    def print_nodules(self):

        self.log_string = self.log_string + "\n\nPrinting nodule view:"
        self.signal_ui_update()
        self.printer.print_by_nodule(self.nodule_finder.nodule_set)
        self.log_string = self.log_string + "\n   - Printed nodule representation in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_ui_update()

    def print_final_data(self):
        self.log_string = self.log_string + "\n\n#   Program complete! Total runtime: {0}".format(self.print_total_time())
        self.log_string = self.log_string + "\n#   - Measured total area: {0} cm2".format(round(self.total_area, 4))
        self.log_string = self.log_string + "\n#   - Measured average diameter: {0} cm".format(round(self.calculated_average_diameter, 4))
        self.log_string = self.log_string + "\n#   - Expected total length: {0} cm".format(round(self.expected_length, 4))
        self.log_string = self.log_string + "\n#   - Measured total length: {0} cm".format(round(self.total_length, 4))
        self.log_string = self.log_string + "\n#   - Deviation from expected length: {0}%".format(round(100*((self.total_length-self.expected_length) / self.total_length), 2))
        self.log_string = self.log_string + "\n#   - Measured total nodule area: {0} cm2".format(round(self.nodule_area, 4))

        self.outstring = "\n{0},{1},{2},{3}".format(config.file_name, self.total_length, self.calculated_average_diameter, self.total_area)
        if config.search_for_nodules:
            self.outstring = self.outstring + ",{0}".format(self.nodule_area)

        self.signal_ui_update()

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

    def spawn_proper_infile(self):
        initial_image = Image.open(config.infile_path + "/" + config.file_name + config.file_extension)
        initial_image.save(config.outfile_path + "/" + config.file_name + "-initial" + config.proper_file_extension)
        self.image_spawned.emit()

    def write_output(self):
        outfile = open("output.csv", "a")
        outfile.writelines(self.outstring)
        outfile.close()