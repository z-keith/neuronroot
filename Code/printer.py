# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       printer.py
#   author=     Zackery Keith
#   date=       Jul 2 2015
#   purpose=    Outputs diagnostic images of program results to image files
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PIL import Image, ImageDraw
import numpy as np

# noinspection PyUnresolvedReferences
import config


class Printer:
    array = None

    image_height = None
    image_width = None

    current_color = [255, 255, 255, 255]
    current_ascending = [False, False, False]

    def __init__(self, size):
        self.image_height, self.image_width = size

    def print_original_image(self, pixel_dict):
        """
        Creates a representation of the Pixel objects contained in pixel_dict
        :param pixel_dict: A dictionary of form {(y, x): Pixel} to be printed
        :return: Nothing. Upon successful run, self.array contains a dark outline for error checking purposes and the
        same array will be printed to the Output folder with -grey appended to the filename
        """
        self.array = np.zeros((self.image_height, self.image_width, 4), dtype=np.uint8)

        # Set to True for slow print with black background, or False for quick transparent print.
        slow_print = True

        if slow_print:
            for x in range(self.image_width):
                for y in range(self.image_height):
                    if (y, x) in pixel_dict:
                        self.array[y][x] = [40, 40, 40, 255]
                    else:
                        self.array[y][x] = [0, 0, 0, 255]
        else:
            for pixel in pixel_dict.values():
                self.array[pixel.y, pixel.x] = [0, 0, 0, 255]

        output_image = Image.fromarray(self.array, 'RGBA')
        output_image.save('../Output/{0}-1-grey.tif'.format(config.file_name[-3:]))

    def print_skeletal_outline(self, seed_pixel_set):
        """
        Prints a representation of the parent-child connections in a set of trees, colorized with a gradient for easy
        visual tracing and error checking.
        :param seed_pixel_set: The set of seed pixels to start drawing from.
        :return: Nothing. Upon successful completion, the image can be found in the output folder, with "-skeleton"
        appended to the original filename.
        """
        current_set = seed_pixel_set

        while current_set:
            next_set = set()

            for pixel in current_set:
                self.array[pixel.y, pixel.x] = self.current_color
                for child in pixel.children:
                    next_set.add(child)

            self.increment_current_color(1)

            current_set = next_set

        output_image = Image.fromarray(self.array, 'RGBA')
        output_image.save('../Output/{0}-2-skeleton.tif'.format(config.file_name[-3:]))

    def increment_current_color(self, multiplier):
        """
        Increments the print color for skeleton printing and root printing
        :param multiplier: A positive integer representing the rate at which colors should change
        :return: Nothing.
        """
        # Change red field (changes half as fast as green, by default)
        if self.current_ascending[0]:
            self.current_color[0] += (1 * multiplier)
            if self.current_color[0] > 230:
                self.current_ascending[0] = False
        else:
            self.current_color[0] -= (1 * multiplier)
            if self.current_color[0] < 100:
                self.current_ascending[0] = True

        # Change green field
        if self.current_ascending[1]:
            self.current_color[1] += (2 * multiplier)
            if self.current_color[1] > 230:
                self.current_ascending[1] = False
        else:
            self.current_color[1] -= (2 * multiplier)
            if self.current_color[1] < 100:
                self.current_ascending[1] = True

        # Change blue field (changes twice as fast as green, by default)
        if self.current_ascending[2]:
            self.current_color[2] += (4 * multiplier)
            if self.current_color[2] > 230:
                self.current_ascending[2] = False
        else:
            self.current_color[2] -= (4 * multiplier)
            if self.current_color[2] < 100:
                self.current_ascending[2] = True

    def print_by_root(self, all_seed_roots):
        """
        Prints a representation of the root connections flowing from the roots in all_seed_roots
        :param all_seed_roots: An iterable containing Root objects to print from
        :return: Nothing. Upon successful completion, the image can be found in the Output folder with -roots appended
        to the filename
        """

        self.current_color = [255, 255, 255, 255]
        self.current_ascending = [False, False, False]

        image = Image.open("../Output/{0}-1-grey.tif".format(config.file_name[-3:]))
        drawer = ImageDraw.Draw(image)

        current_roots = all_seed_roots

        while current_roots:

            next_roots = set()

            for root in current_roots:

                for i in range(len(root.pixel_list)):

                    if i > 0:

                        current_xy = (root.pixel_list[i].x, root.pixel_list[i].y)
                        previous_xy = (root.pixel_list[i - 1].x, root.pixel_list[i - 1].y)
                        drawer.line([previous_xy, current_xy], tuple(self.current_color))

                    else:

                        current_xy = (root.pixel_list[i].x, root.pixel_list[i].y)
                        drawer.point(current_xy, tuple(self.current_color))

                for branch_tuple in root.branch_list:
                    next_roots.add(branch_tuple[1])

                self.increment_current_color(20)

            current_roots = next_roots

        image.save('../Output/{0}-3-roots.tif'.format(config.file_name[-3:]))

    def print_by_nodule(self, nodule_set):
        """

        :param nodule_set:
        :return:
        """

        self.current_color = [255, 255, 255, 255]

        image = Image.open("../Output/{0}-3-roots.tif".format(config.file_name[-3:]))
        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse((pixel.x-pixel.radius, pixel.y-pixel.radius, pixel.x+pixel.radius, pixel.y+pixel.radius), tuple(self.current_color), tuple(self.current_color))

        image.save('../Output/{0}-4-nodules.tif'.format(config.file_name[-3:]))