# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       Controller
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Mediates the interaction of the ImageHandler and TreeHandler
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import time
import Config
import ImageHandler as iH
import TreeHandler as tH


class Controller:

    # Reference to image handling object
    image_h = None

    # Reference to tree handling object
    tree_h = None

    # Time objects for performance tracking
    start_time = None
    last_time = None

    def __init__(self):
        """
        Initializes a Controller object
        :return:
        """

        Config.init()
        self.start_time = time.time()
        self.last_time = time.time()

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

        # Increment last_time
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

        # Increment last_time
        self.last_time = time.time()

        return "{0} minute{1} and {2} second{3}.".format(minutes, plural_min, str(seconds).rjust(5), plural_sec)

    def print_node_summary(self):
        """
        Prints node_dict as a .txt file for debugging use
        """

        # Open output file named according to image filename
        filename = Config.filename + "-node_summary.txt"
        nodefile = open(filename, 'w')

        node_dict = self.tree_h.node_dict

        for key in node_dict:
            nodefile.write('ID: {0}'.format(key))
            nodefile.write('\n')

            nodefile.write('X: {0} '.format(node_dict[key].x))
            nodefile.write('Y: {0} '.format(node_dict[key].y))
            nodefile.write('I: {0} '.format(node_dict[key].i))
            nodefile.write('R: {0} '.format(node_dict[key].radius))
            nodefile.write('\n')

            nodefile.write('Parent: {0} '.format(node_dict[key].parent))
            nodefile.write('Children: {0} '.format(node_dict[key].children))
            nodefile.write('\n')

            nodefile.write('Neighbors: {0} '.format(node_dict[key].neighbors))
            nodefile.write('\n')

            nodefile.write('Covers: {0} '.format(node_dict[key].covered_set))
            nodefile.write('\n')

            nodefile.write('Covered by: {0} '.format(node_dict[key].covered_by))
            nodefile.write('\n')

        nodefile.close()

    def load_image(self):
        """
        Performs the ImageHandler's image loading operations
        """

        print("\nLoading image {0}:".format(Config.filename))

        self.image_h = iH.ImageHandler(Config.filename)

        self.image_h.load_to_array()
        print("\n- Loaded filtered image to iH.array in {0}".format(self.print_timestamp()))
        print("- Array size: {0}x{1}".format(self.image_h.image_width, self.image_h.image_height))

    def build_trees(self):
        """
        Performs the TreeHandler's tree construction operations
        """

        print("\nConstructing nodes and edges:")

        self.tree_h = tH.TreeHandler()

        self.tree_h.load_nodes(self.image_h)
        print("\n- Constructed graph and node_dict in {0}".format(self.print_timestamp()))
        print("- Number of nodes found on first pass: {0}".format(self.tree_h.initial_nodecount))

        self.tree_h.find_best_node()
        print("\n- Found best approximation for click point in {0}".format(self.print_timestamp()))
        print("- Best approximation found for click point: ({0}, {1})".format(self.tree_h.best_node.x,
                                                                              self.tree_h.best_node.y))

        self.tree_h.find_edges()
        print("\n- Added and weighted edges in {0}".format(self.print_timestamp()))
        print("- Number of edges added: {0}".format(self.tree_h.graph.number_of_edges()))

        self.tree_h.build_tree(self.tree_h.best_node_key)
        print("\n- Constructed initial tree in {0}".format(self.print_timestamp()))

        self.tree_h.find_additional_trees()
        print("\n- Added additional trees in {0}".format(self.print_timestamp()))
        print("- Additional trees added: {0}".format(self.tree_h.tree_count))

    def prune_trees(self):
        """
        Performs the TreeHandler's tree pruning operations
        """

        print("\nPruning over-complete reconstruction:")

        self.tree_h.prune_dark_nodes()
        dark_removal_count = self.tree_h.initial_nodecount - self.tree_h.current_nodecount
        print("\n- Removed dark leaves in {0}".format(self.print_timestamp()))
        print("- Dark nodes removed: {0}".format(dark_removal_count))

        self.tree_h.set_radii()
        print("\n- Set radii in {0}".format(self.print_timestamp()))
        self.tree_h.set_covered_areas()
        print("- Set covering/covered_by relationships in {0}".format(self.print_timestamp()))

        # self.tree_h.prune_redundant_nodes()
        redundant_removal_count = self.tree_h.initial_nodecount - dark_removal_count - self.tree_h.current_nodecount
        print("\n- Removed redundant nodes in {0}".format(self.print_timestamp()))
        print("- Redundant nodes removed: {0}".format(redundant_removal_count))

        compression_percentage = round(100 * (1 - self.tree_h.current_nodecount / self.tree_h.initial_nodecount), 1)
        print("\n- Total nodes in final representation: {0}".format(self.tree_h.current_nodecount))
        print("- Compression: {0}%".format(compression_percentage))
