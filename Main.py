# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       Main
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Calls and manipulates the controller to perform an iteration of
#               the analysis algorithm
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import Controller


def main():
    """
    Function called on program initialization
    """

    # initialize the Controller object
    controller = Controller.Controller()

    # load the image file into an ImageHandler
    controller.load_image()

    # construct a graph and associated node_dict in a TreeHandler
    controller.build_trees()

    # print the initial representation of the output
    controller.image_h.initial_print(controller.tree_h)
    print("\nPrinted initial representation in {0}".format(controller.print_timestamp()))

    # prune the initial representation down to a skeleton
    controller.prune_trees()

    # print the skeleton representation of the output
    controller.image_h.skeleton_print(controller.tree_h)
    print("\nPrinted skeleton representation in {0}".format(controller.print_timestamp()))

    # complete!
    print("\n#################################################################")
    print("# Program complete! Total runtime: {0} #".format(controller.print_total_time()))
    print("#################################################################")

main()