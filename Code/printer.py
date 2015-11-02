# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       printer.py
#   author=     Zackery Keith
#   date=       Jul 2 2015
#   purpose=    Outputs diagnostic images of program results to image files
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PIL import Image, ImageDraw
import numpy as np
import random
import os

# noinspection PyUnresolvedReferences
import config


class Printer:
    array = None

    image_height = None
    image_width = None

    current_color = [255, 255, 255]
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
        self.array = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        for (y, x) in pixel_dict:
            self.array[y][x] = [60, 60, 60]

        output_image = Image.fromarray(self.array, 'RGB')
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

        output_image = Image.fromarray(self.array, 'RGB')
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

        self.current_color = [255, 255, 255]
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

        self.current_color = [255, 255, 255]

        image = Image.open("../Output/{0}-3-roots.tif".format(config.file_name[-3:]))
        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse((pixel.x-pixel.radius, pixel.y-pixel.radius, pixel.x+pixel.radius, pixel.y+pixel.radius), tuple(self.current_color), tuple(self.current_color))

        image.save('../Output/{0}-4-nodules.tif'.format(config.file_name[-3:]))

    def count_white_px(self, nodule_set):

        self.current_color = [255, 255, 255]

        image = Image.fromarray(np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8))

        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse((pixel.x-pixel.radius, pixel.y-pixel.radius, pixel.x+pixel.radius, pixel.y+pixel.radius), tuple(self.current_color), tuple(self.current_color))

        array = np.array(image)

        area_px = np.count_nonzero(array)

        area_cm = area_px*(config.cm_per_pixel**2)

        return area_cm

    def print_test_radii(self, pixel_dict):

        os.makedirs("../TestOutputs/", exist_ok=True)
        os.makedirs("../TestOutputs/{0}/".format(config.file_name[-3:]), exist_ok=True)

        case_set = set()

        while len(case_set) < config.testcase_count-4:
            case = random.choice(list(pixel_dict.keys()))
            if pixel_dict[case].radius > 2:
                case_set.add(case)
        while len(case_set) < config.testcase_count:
            case = random.choice(list(pixel_dict.keys()))
            case_set.add(case)

        for case in case_set:

            r = pixel_dict[case].radius
            x = pixel_dict[case].x
            y = pixel_dict[case].y

            test_array = np.zeros((2*r + 3, 2*r + 3, 3), dtype=np.uint8)

            for i in range(-r-1, r+2):
                for j in range(-r-1, r+2):
                    if i==j==0:
                        test_array[r+1+j][r+1+i] = [255,0,0]
                    elif (y+j, x+i) in pixel_dict:
                        test_array[j+(r+1)][i+(r+1)] = [255,255,255]

            output_image = Image.fromarray(test_array, 'RGB')
            print("{0}_{1}.png : r={2}".format(x, y, r))
            output_image.save('../TestOutputs/{0}/{1}_{2}.png'.format(config.file_name[-3:], x, y))




