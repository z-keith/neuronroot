from PIL import Image, ImageDraw
import numpy as np
import random
import os


class Printer:
    array = None

    updated_image_path = None
    image_height = None
    image_width = None

    current_color = [255, 255, 255]
    current_ascending = [False, False, False]

    def __init__(self, path, shape):
        self.updated_image_path = path
        self.image_height = shape[0]
        self.image_width = shape[1]

    def print_original_image(self, pixel_dict):
        """
        Creates a representation of the Pixel objects contained in pixel_dict
        :param pixel_dict: A dictionary of form {(y, x): Pixel} to be printed
        :return: Nothing. Upon successful run, self.array contains a dark outline for error checking purposes and the
        same array will be printed to the Output folder with -analysis appended to the filename
        """

        self.array = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        for (y, x) in pixel_dict:
            self.array[y][x] = [20, 20, 20]

        output_image = Image.fromarray(self.array, 'RGB')
        output_image.save(self.updated_image_path)

    def print_skeletal_outline(self, seed_pixel_set):
        """
        Prints a representation of the parent-child connections in a set of trees, colorized with a gradient for easy
        visual tracing and error checking.
        :param seed_pixel_set: The set of seed pixels to start drawing from.
        :return: Nothing. Upon successful completion, the image can be found in the output folder, with "-analysis"
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
        output_image.save(self.updated_image_path)

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

        image = Image.open(self.updated_image_path)
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

        image.save(self.updated_image_path)

    def print_by_nodule(self, nodule_set):
        """

        :param nodule_set:
        :return:
        """

        self.current_color = [255, 255, 255]

        image = Image.open(self.updated_image_path)
        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse(
                (pixel.x - pixel.radius, pixel.y - pixel.radius, pixel.x + pixel.radius, pixel.y + pixel.radius),
                tuple(self.current_color), tuple(self.current_color))

        image.save(self.updated_image_path)

    def count_white_px(self, nodule_set):

        self.current_color = [255, 255, 255]

        image = Image.fromarray(np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8))

        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse(
                (pixel.x - pixel.radius, pixel.y - pixel.radius, pixel.x + pixel.radius, pixel.y + pixel.radius),
                tuple(self.current_color), tuple(self.current_color))

        array = np.array(image)

        area_px = np.count_nonzero(array)

        return area_px

    def count_nodules_old(self, nodule_set):

        self.current_color = [255, 255, 255]

        image = Image.fromarray(np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8))

        drawer = ImageDraw.Draw(image)

        for pixel in nodule_set:
            drawer.ellipse(
                (pixel.x - pixel.radius, pixel.y - pixel.radius, pixel.x + pixel.radius, pixel.y + pixel.radius),
                tuple(self.current_color), tuple(self.current_color))

        array = np.array(image)

        count = 0
        locations = list()

        for x in range(array.shape[1]):
            for y in range(array.shape[0]):
                if array[y][x][0] == [255]:
                    locations.append((y, x))

        while locations:
            count += 1
            current = set()
            current.add(locations[0])
            while True:
                next_locations = set()
                for i in current:
                    locations.remove(i)
                for i in current:
                    for x in [-1, 0, 1]:
                        for y in [-1, 0, 1]:
                            if (i[0] + y, i[1] + x) in locations and x ** 2 + y ** 2:
                                next_locations.add((i[0] + y, i[1] + x))
                if len(next_locations):
                    current = next_locations
                else:
                    break

        return count

    def count_nodules(self, nodule_set):
        self.current_color = [255, 255, 255]
        image = Image.fromarray(np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8))
        drawer = ImageDraw.Draw(image)
        for pixel in nodule_set:
            drawer.ellipse(
                (pixel.x - pixel.radius, pixel.y - pixel.radius, pixel.x + pixel.radius, pixel.y + pixel.radius),
                tuple(self.current_color), tuple(self.current_color))
        array = np.array(image)
        array = np.dot(array[..., :3], [0.299, 0.587, 0.144])

        # problem block begins

        count = 0
        locations = set()
        for y in range(0, array.shape[0]):
            for x in range(0, array.shape[1]):
                if array[y][x]:
                    locations.add((y, x))

        # problem block ends

        while locations:
            count += 1
            current = set()
            for i in locations:
                current.add(i)
                break
            while True:
                next_locations = set()
                for i in current:
                    locations.remove(i)
                for i in current:
                    for x in [-1, 0, 1]:
                        for y in [-1, 0, 1]:
                            if (i[0] + y, i[1] + x) in locations and x ** 2 + y ** 2:
                                next_locations.add((i[0] + y, i[1] + x))
                if len(next_locations):
                    current = next_locations
                else:
                    break

        return count

    def print_test_radii(self, count, name, pixel_dict):

        os.makedirs("../TestOutputs", exist_ok=True)
        os.makedirs("../TestOutputs/" + str(name), exist_ok=True)

        case_set = set()

        while len(case_set) < count * .5 and len(case_set) < len(pixel_dict):
            case = random.choice(list(pixel_dict.keys()))
            if pixel_dict[case].radius > 2:
                case_set.add(case)
        while len(case_set) < count and len(case_set) < len(pixel_dict):
            case = random.choice(list(pixel_dict.keys()))
            case_set.add(case)

        for case in case_set:

            r = pixel_dict[case].radius
            x = pixel_dict[case].x
            y = pixel_dict[case].y

            test_array = np.zeros((2 * r + 3, 2 * r + 3, 3), dtype=np.uint8)

            for i in range(-r - 1, r + 2):
                for j in range(-r - 1, r + 2):
                    if i == j == 0:
                        test_array[r + 1 + j][r + 1 + i] = [255, 0, 0]
                    elif (y + j, x + i) in pixel_dict:
                        test_array[j + (r + 1)][i + (r + 1)] = [255, 255, 255]

            output_image = Image.fromarray(test_array, 'RGB')
            output_image.save('../TestOutputs/{0}/{1}_{2}.png'.format(name, x, y))
