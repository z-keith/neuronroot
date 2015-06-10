# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       ImageHandler
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Object that holds and manipulates input and output images
#               and associated arrays
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PIL import Image
import numpy as np

import Config


class ImageHandler:

    # Filename to use in loading and printing
    file_name = None

    # Array containing the current representation of the image (thresholded, pruned, whatever)
    array = None

    # Final dimensions of the scaled image
    image_height = None
    image_width = None

    # Proportion of the mean image intensity to set the threshold at
    threshold_multiplier = 1.0

    # Current color and direction of change in color for gradient printing
    current_color = [255, 255, 255, 255]
    current_ascending = [False, False, False]

    def __init__(self, filename):
        """
        Initializes an ImageHandler object
        :param filename: Filename to be used for this object
        """

        self.file_name = filename

    def load_to_array(self):
        """
        Main image loading function. Loads, resizes, and filters an image.
        :return: numpy array of floats 0-255 representing brightness at that location
        """

        image = Image.open("TestImages/{0}.tif".format(self.file_name))

        # scale image
        scaling_ratio = (Config.image_scaled_height / float(image.size[1]))
        if scaling_ratio < 1:
            scaled_width = int(float(image.size[0])*scaling_ratio)
            image = image.resize((scaled_width, Config.image_scaled_height))

        self.image_height = image.size[1]
        self.image_width = image.size[0]

        # make array from image
        self.array = np.array(image)
        self.filter_image()

    def filter_image(self):
        """
        Threshold and filter an image array
        """

        # make image black and white
        self.array = np.dot(self.array[..., :3], [0.299, 0.587, 0.144])

        # threshold the image based on the mean brightness of the image
        global_threshold = self.array.mean() * self.threshold_multiplier
        self.array[self.array < global_threshold] = 0

        self.mask_ruler()

    def mask_ruler(self):
        """
        Set the values along the edges of the array and the ruler's area of the array to 0.
        """

        # Set a 1.5% margin around the edge of the image
        margin = int(self.image_height * 0.015)

        # Left edge
        for x in range(0, margin):
            for y in range(0, self.image_height):
                self.array[y, x] = 0

        # Right edge
        for x in range(self.image_width-margin, self.image_width):
            for y in range(0, self.image_height):
                self.array[y, x] = 0

        # Top edge
        for x in range(0, self.image_width):
            for y in range(0, margin):
                self.array[y, x] = 0

        # Bottom edge
        for x in range(0, self.image_width):
            for y in range(self.image_height - margin, self.image_height):
                self.array[y, x] = 0

        # Ruler (bottom 15% of image, left 60% of image)
        for x in range(0, int(0.6*self.image_width)):
            for y in range(int(0.85*self.image_height), self.image_height):
                self.array[y, x] = 0

    def initial_print(self, tree_handler):
        """
        Prints the pre-pruning tree as a faint background in the output image for comparison purposes
        :param tree_handler: a tree handler to print out
        """

        # initialize array
        self.array = np.zeros((self.image_height, self.image_width, 4), dtype=np.uint8)

        # set array to black
        for x in range(self.image_width):
            for y in range(self.image_height):
                self.array[y][x] = [0, 0, 0, 255]

        # set all locations containing a node to grey
        for key in tree_handler.node_dict:

            # Print as grey
            self.array[tree_handler.node_dict[key].y, tree_handler.node_dict[key].x] = [40, 40, 40, 255]

        outimage = Image.fromarray(self.array, 'RGBA')
        outimage.save('TestImages/{0}-skeleton.tif'.format(self.file_name))

    def skeleton_print(self, tree_handler):
        """
        Prints the final output image with a gradient (currently an arbitrary gradient to track the flow of connections)
        :param tree_handler: a tree handler to print out
        """

        # Start with the seed nodes of each tree
        current_set = tree_handler.all_seed_nodes
        # TODO: fix potential bug where best_node is pruned and this gets mad (This is already happening with 002)

        while True:
            next_set = set()

            # Print the current set of nodes in the current color
            for node in current_set:
                self.array[node.y, node.x] = self.current_color
                for child in node.children:
                    if not child.removed:
                        next_set.add(child)

            # Update the print color
            if len(next_set) > 0:
                if self.current_ascending[0]:
                    self.current_color[0] += 1
                    if self.current_color[0] > 230:
                        self.current_ascending[0] = False
                else:
                    self.current_color[0] -= 1
                    if self.current_color[0] < 60:
                        self.current_ascending[0] = True

                if self.current_ascending[1]:
                    self.current_color[1] += 2
                    if self.current_color[1] > 230:
                        self.current_ascending[1] = False
                else:
                    self.current_color[1] -= 2
                    if self.current_color[1] < 60:
                        self.current_ascending[1] = True

                if self.current_ascending[2]:
                    self.current_color[2] += 3
                    if self.current_color[2] > 230:
                        self.current_ascending[2] = False
                else:
                    self.current_color[2] -= 3
                    if self.current_color[2] < 60:
                        self.current_ascending[2] = True

                # Set up for the next iteration
                current_set = next_set

            else:
                break

        # save image
        outimage = Image.fromarray(self.array, 'RGBA')
        outimage.save('TestImages/{0}-skeleton.tif'.format(self.file_name))

    def all_node_print(self, tree_handler):
        for node in tree_handler.node_dict.values():
            if not node.removed:
                self.array[node.y, node.x] = [255, 255, 255, 255]

        outimage = Image.fromarray(self.array, 'RGBA')
        outimage.save('TestImages/{0}-skeleton.jpg'.format(self.file_name))