# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       array_builder.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Loads the input image and prepares it for analysis
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PIL import Image
from scipy import ndimage
import numpy as np

# noinspection PyUnresolvedReferences
import config


class ArrayBuilder:

    # File name stub to be loaded (in production version, will have to change to file path)
    file_name = None

    # Stores the thresholded, filtered, and masked image data for delivery to another function
    array = None

    # Image dimensions
    image_height = None
    image_width = None

    def __init__(self, filename):
        self.file_name = filename

    def load_to_array(self):
        """
        Loads and scales the image from the file name defined when this ArrayBuilder was initialized.
        :return: Nothing.
        """
        image = Image.open("../TestImages/{0}.tif".format(self.file_name))

        # Scale the image down, if necessary, to the height defined in config
        # The program can be made to run faster at the cost of precision by reducing config.image_scaled_height
        scaling_ratio = (config.image_scaled_height / float(image.size[1]))
        if scaling_ratio < 1:
            scaled_width = int(float(image.size[0])*scaling_ratio)
            image = image.resize((scaled_width, config.image_scaled_height))

        self.image_height = image.size[1]
        self.image_width = image.size[0]

        self.array = np.array(image)

    def filter_array(self):
        """
        Changes the array to represent a black and white image and thresholds it at a percentage of the global mean
        :return: Nothing.
        """
        self.array = np.dot(self.array[..., :3], [0.299, 0.587, 0.144])

        # Scale of the image mean intensity to threshold the image at (higher multipliers are less permissive)
        threshold_multiplier = 1.0

        global_threshold = self.array.mean() * threshold_multiplier
        self.array[self.array < global_threshold] = 0

        self.array = ndimage.filters.median_filter(self.array, size=(4, 4))

    def mask_ruler(self):
        """
        Automatically sets the margins of the image and the region containing the ruler to black, to prevent image
        artifacts from being detected as roots.
        :return: Nothing.
        """

        # Currently removes the 1.5% of the image closest to each edge.
        margin_ratio = 0.015
        margin = int(self.image_height * margin_ratio)

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
