import time
import math
from PyQt5.QtCore import pyqtSignal, QObject

from lib.model import array_builder, area_builder, tree_builder, root_builder, nodule_finder
from lib.view import printer


class Model(QObject):
    controller = None

    array_builder = None

    area_builder = None

    tree_builder = None

    root_builder = None

    nodule_finder = None

    printer = None

    # Time objects for performance tracking
    start_time = None
    last_time = None

    # Statistical output
    total_area = None
    calculated_average_diameter = None
    expected_length = None
    total_length = None
    nodule_area = None
    nodule_count = None

    csv_out_string = None

    log_string = None

    log_update = pyqtSignal()
    img_update = pyqtSignal()

    def __init__(self, controller):
        QObject.__init__(self)
        self.controller = controller
        self.log_update.connect(self.controller.signal_log_update)
        self.img_update.connect(self.controller.signal_image_update)

    def signal_log_update(self):
        self.log_update.emit()

    def signal_image_update(self):
        self.img_update.emit()

    def load_image_to_array(self, file_path):
        self.start_time = time.time()
        self.last_time = time.time()

        self.log_string = "Loading image {0}:".format(self.controller.config.file_name)
        self.signal_log_update()
        self.array_builder = array_builder.ArrayBuilder(file_path)

        shape, scaling = self.array_builder.load_to_array(self.controller.config.image_scaled_height)
        self.controller.config.image_dimensions = shape
        self.controller.scale_config(scaling)
        self.log_string += "\n- Loaded image to array in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Detected effective DPI of {0}".format(self.controller.config.dpi)
        self.log_string += "\n   - Image size: {0}x{1}".format(self.array_builder.image_width,
                                                               self.array_builder.image_height)
        self.signal_log_update()

        self.array_builder.filter_array(self.controller.config.threshold_multiplier)
        self.array_builder.mask_ruler(self.controller.config.area_whitelist, self.controller.config.area_blacklist)
        self.log_string += "\n- Filtered and masked array in {0}".format(self.print_timestamp())
        self.signal_log_update()

    def build_areas(self):
        self.log_string += "\n\nConstructing pixels and areas:"
        self.signal_log_update()
        self.area_builder = area_builder.AreaBuilder()

        self.area_builder.load_pixels(self.array_builder.array)
        self.log_string += "\n- Constructed pixel_dict in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Total area found on first pass: {0} px.".format(
            len(self.area_builder.pixel_dict))
        self.signal_log_update()

        self.area_builder.find_neighbors()
        self.log_string += "\n- Added neighbors in {0}".format(self.print_timestamp())
        self.signal_log_update()

        self.area_builder.set_radii()
        self.log_string += "\n- Set radii in {0}".format(self.print_timestamp())
        self.signal_log_update()

    def print_background(self):
        """
        Function to print a faint background of the original image to a file for error checking.
        :return: Nothing. Upon successful completion, printer.array contains the faint background to be drawn on later.
        """

        self.log_string += "\n\nPrinting initial area's outline:"
        self.signal_log_update()
        self.printer = printer.Printer(self.controller.config.updated_image_path,
                                       self.array_builder.array.shape)

        self.printer.print_original_image(self.area_builder.pixel_dict)
        self.log_string += "\n- Printed gray outline in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_log_update()

    def build_trees(self):
        """
        Function to iteratively prune the pixels in pixel_dict until only a 1px-wide skeleton remains to represent the
        original image. This skeleton has parent-child relationships set up already.
        :return: Nothing. Upon successful completion, tree_builder.pixel_dict contains the skeleton and
        tree_builder.all_seed_pixels contains the starting points of each tree.
        """

        self.log_string += "\n\nPruning areas down to trees:"
        self.signal_log_update()
        self.tree_builder = tree_builder.TreeBuilder(self.area_builder.pixel_dict)

        seedY_loc = math.floor(self.controller.config.seedYX[0] * self.controller.config.image_dimensions[0])
        seedX_loc = math.floor(self.controller.config.seedYX[1] * self.controller.config.image_dimensions[1])

        self.controller.config.seedYX = (seedY_loc, seedX_loc)

        self.tree_builder.best_pixel = self.tree_builder.find_best_pixel(self.controller.config.seedYX)
        self.tree_builder.all_seed_pixels.add(self.tree_builder.best_pixel)
        self.log_string += "\n- Found best approximation for click point in {0}".format(
            self.print_timestamp())
        self.log_string += "\n   - Best approximation found for click point: ({0}, {1}) with radius of {2}".format(
            self.tree_builder.best_pixel.x, self.tree_builder.best_pixel.y, self.tree_builder.best_pixel.radius)
        self.signal_log_update()

        self.tree_builder.find_small_areas(self.controller.config.minimum_tree_size_multiplier *
                                           self.controller.config.image_dimensions[0])
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string += "\n- Removed small areas in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Total small area removed: {0} px ({1}% of original area)".format(
            removal_count, removed_percentage)
        self.signal_log_update()

        self.total_area = float(len(self.tree_builder.pixel_dict)) * self.controller.config.cm_per_pixel ** 2 \
            * ((1 + math.sqrt(2)) / 2)

        self.tree_builder.prune_redundant_pixels()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string += "\n- Removed redundant areas in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Total redundant area removed: {0} px ({1}% of original area)".format(
            removal_count,
            removed_percentage)
        self.signal_log_update()

        self.tree_builder.set_tree_relationships()
        self.log_string += "\n- Set parent-child relationships for trees in {0}".format(
            self.print_timestamp())
        self.signal_log_update()

        self.tree_builder.remove_right_angles()
        removal_count = self.tree_builder.previous_pixel_count - len(self.tree_builder.pixel_dict)
        self.tree_builder.previous_pixel_count = len(self.tree_builder.pixel_dict)
        removed_percentage = round(100 * (removal_count / self.tree_builder.initial_pixel_count), 1)
        self.log_string += "\n- Removed inefficient right-angle connections in {0}".format(
            self.print_timestamp())
        self.log_string += "\n   - Total inefficient connection area removed: {0} px ({1}% of original area)".format(
            removal_count, removed_percentage)
        self.signal_log_update()

        compression_percentage = round(100 * (1 - len(self.tree_builder.pixel_dict) /
                                              self.tree_builder.initial_pixel_count), 1)
        self.log_string += "\n- Total pixels in final area representation: {0}".format(
            self.tree_builder.previous_pixel_count)
        self.log_string += "\n   - Total compression: {0}%".format(compression_percentage)
        self.signal_log_update()

    def print_skeleton(self):
        """
        Calls the existing printer to print the colorized skeletons of the trees stored in the tree_builder.
        :return: Nothing. Upon successful run, the output image can be found in the same directory as the original,
        with "-skeleton" appended to its filename
        """

        self.log_string += "\n\nPrinting skeleton onto gray outline:"
        self.signal_log_update()
        self.printer.print_skeletal_outline(self.tree_builder.all_seed_pixels)
        self.log_string += "\n   - Printed skeletal outline in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_log_update()

    def print_test_radii(self):

        self.log_string += "\n\nPrinting test radii:"
        self.signal_log_update()
        testcase_count = self.controller.config.testcase_count
        file_name = self.controller.config.testcase_count
        self.printer.print_test_radii(testcase_count, file_name, self.area_builder.pixel_dict)
        self.log_string += "\n   - Printed {0} test cases in {1}".format(testcase_count,
                                                                         self.print_timestamp())
        self.signal_log_update()

    def build_roots(self):
        """
        Function to build a series of Root objects to represent the trees in a pixel_dict. It creates the roots, removes
        short invalid roots, and untangles them by correctly combining them into longer roots.
        :return: Nothing. Upon successful completion, root_builder.root_dict contains all the roots, and
        root_builder.all_seed_roots contains the start points to use them.
        """

        self.log_string += "\n\nBuilding root structures:"
        self.signal_log_update()
        self.root_builder = root_builder.RootBuilder(self.tree_builder.pixel_dict, self.tree_builder.all_seed_pixels)

        self.root_builder.create_initial_roots()
        initial_root_count = len(self.root_builder.root_dict)
        self.log_string += "\n- Constructed initial roots in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Total number of initial roots: {0}".format(initial_root_count)
        self.signal_log_update()

        self.root_builder.update_root_statistics_and_totals()
        initial_root_length = round(self.root_builder.total_root_length, 1)
        initial_average_radius = round(self.root_builder.average_radius, 1)
        self.log_string += "\n- Calculated initial root average radii and total lengths in {0}".format(
            self.print_timestamp())
        self.log_string += "\n   - Total root length (unrefined): {0} px.".format(initial_root_length)
        self.log_string += "\n   - Overall average radius (unrefined): {0} px.".format(
            initial_average_radius)
        self.signal_log_update()

        self.root_builder.set_remaining_lengths()
        self.log_string += "\n- Set remaining lengths for each root in {0}".format(
            self.print_timestamp())
        self.signal_log_update()

        self.root_builder.untangle_roots()
        roots_lost_to_combination = initial_root_count - len(self.root_builder.root_dict)
        removed_percentage = round(100 * (roots_lost_to_combination / initial_root_count), 1)
        self.log_string += "\n- Combined and untangled roots in {0}".format(self.print_timestamp())
        self.log_string += "\n   - Roots lost to combination: {0} ({1}% of original count)".format(
            roots_lost_to_combination, removed_percentage)
        self.log_string += "\n   - Final root count: {0}".format(len(self.root_builder.root_dict))
        self.signal_log_update()

        self.root_builder.update_root_statistics_and_totals()
        self.log_string += "\n- Calculated final root average radii and total lengths in {0}".format(
            self.print_timestamp())
        self.log_string += "\n   - Final total root length: {0} px.".format(
            round(self.root_builder.total_root_length, 1))
        self.log_string += "\n   - Overall average radius: {0} px.".format(
            round(self.root_builder.average_radius, 1))
        self.signal_log_update()

        cm_per_pixel = self.controller.config.cm_per_pixel
        self.log_string += "\n- Final statistics:"
        self.log_string += "\n   - Total root length: {0} cm.".format(
            round(self.root_builder.total_root_length * cm_per_pixel, 2))
        self.log_string += "\n   - Overall average diameter: {0} cm.".format(
            round(2 * self.root_builder.average_radius * cm_per_pixel, 4))
        self.signal_log_update()

        self.calculated_average_diameter = 2 * self.root_builder.average_radius * \
            cm_per_pixel * ((1 + math.sqrt(2)) / 2)
        self.total_length = self.root_builder.total_root_length * cm_per_pixel * ((1 + math.sqrt(2)) / 2)
        self.expected_length = self.total_area / self.calculated_average_diameter * ((1 + math.sqrt(2)) / 2)

    def print_roots(self):

        self.log_string += "\n\nPrinting root representation:"
        self.signal_log_update()
        self.printer.print_by_root(self.root_builder.all_seed_roots)
        self.log_string += "\n   - Printed root representation in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_log_update()

    def find_nodules(self):

        self.log_string += "\n\nSearching for nodules:"
        self.signal_log_update()
        self.nodule_finder = nodule_finder.NoduleFinder(self.root_builder.root_dict, self.root_builder.all_seed_roots,
                                                        self.root_builder.total_root_length,
                                                        self.root_builder.average_radius)

        multipliers = (self.controller.config.abs_threshold_multiplier, self.controller.config.min_threshold_multiplier, self.controller.config.rad_multiplier)
        self.nodule_finder.find_by_windows(multipliers)
        self.log_string += "\n   - Completed threshold-based search in {0}".format(
            self.print_timestamp())
        self.signal_log_update()

        self.nodule_count = self.printer.count_nodules(self.nodule_finder.nodule_set)
        self.log_string += "\n   - Counted nodules in {0}".format(self.print_timestamp())
        self.signal_log_update()
        self.log_string += "\n   - Nodules found: {0}".format(self.nodule_count)
        self.signal_log_update()

        nodule_area_px = self.printer.count_white_px(self.nodule_finder.nodule_set) * ((1 + math.sqrt(2)) / 2)
        self.nodule_area = nodule_area_px * self.controller.config.cm_per_pixel**2
        self.log_string += "\n   - Computed nodule area (hacky solution) in {0}".format(
            self.print_timestamp())
        self.signal_log_update()
        self.log_string += "\n   - Estimated nodule area: {0} cm^2".format(round(self.nodule_area, 2))
        self.signal_log_update()

    def print_nodules(self):

        self.log_string += "\n\nPrinting nodule view:"
        self.signal_log_update()
        self.printer.print_by_nodule(self.nodule_finder.nodule_set)
        self.log_string += "\n   - Printed nodule representation in {0}".format(self.print_timestamp())
        self.signal_image_update()
        self.signal_log_update()

    def display_final_data(self):
        self.log_string += "\n\n#   Program complete! Total runtime: {0}".format(
            self.print_total_time())
        self.log_string += "\n#   - Measured total area: {0} cm2".format(round(self.total_area, 4))
        self.log_string += "\n#   - Measured average diameter: {0} cm".format(
            round(self.calculated_average_diameter, 4))
        self.log_string += "\n#   - Expected total length: {0} cm".format(
            round(self.expected_length, 4))
        self.log_string += "\n#   - Measured total length: {0} cm".format(round(self.total_length, 4))
        self.log_string += "\n#   - Deviation from expected length: {0}%".format(
            round(100 * ((self.total_length - self.expected_length) / self.total_length), 2))
        if self.controller.config.search_for_nodules:
            self.log_string += "\n#   - Measured total nodule area: {0} cm2".format(
                round(self.nodule_area, 4))
            self.log_string += "\n#   - Nodule count: {0}".format(self.nodule_count)

        self.csv_out_string = "\n{0},{1},{2},{3}".format(self.controller.config.file_name, round(self.total_length, 4),
                                                    round(self.calculated_average_diameter, 4),
                                                    round(self.total_area, 4))
        if self.controller.config.search_for_nodules:
            self.csv_out_string += ",{0},{1}".format(self.nodule_count, round(self.nodule_area, 4))

        self.signal_log_update()

    def clean_up(self):
        del self.array_builder
        del self.area_builder
        del self.tree_builder
        del self.root_builder
        del self.nodule_finder
        del self.printer

        self.start_time = None
        self.last_time = None

        self.total_area = None
        self.calculated_average_diameter = None
        self.expected_length = None
        self.total_length = None
        self.nodule_area = None
        self.nodule_count = None

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
