 #-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       config
#   author=     Zackery Keith
#   date=       Mar 6 2015
#   purpose=    System utilities (global variable storage, timestamps, graph
#               printing and other debug functions)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import time


# GLOBAL VARIABLES  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# change this to swap between test images (currently supports 293 and 329)
current_file = 293

# filename stub (the date and sample)
# used for opening an image and naming files made from it
filename = ""

# dimensions of the formatted image
sizeX = 0
sizeY = 0

# location of the initial seed point for tracing
seedX = 0
seedY = 0

# time tracking used throughout the program by PrintTimeBenchmark()
start_time = 0
last_time = 0

# number of nodes found in the over-complete reconstruction
initial_nodecount = 0

# number of nodes remaining after pruning
final_nodecount = 0


# FUNCTIONS # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def init():
    """
    Sets up global variables based on the current file
    :return: Nothing
    """
    global filename
    global seedX
    global seedY
    global start_time
    global last_time

    start_time = time.time()
    last_time = time.time()

    if current_file == 293:
        filename = "2014-06-24-Tri-293"
        seedX = 1146
        seedY = 80

    if current_file == 329:
        filename = "2014-06-26-Tri-329"
        seedX = 901
        seedY = 432

    # if current_file == <your key here>...


def PrintTimeBenchmark():
    """
    Builds a string representation of the time since this function was last called
    :return: string representation of elapsed time (example: " 3 minutes and 22.32 seconds.")
    """
    global last_time

    elapsed = time.time() - last_time
    minutes = int(elapsed / 60)
    seconds = round((elapsed % 60), 2)
    last_time = time.time()
    if minutes == "1":
        return "{0} minute and {1} seconds.".format(minutes, seconds)
    else:
        return "{0} minutes and {1} seconds.".format(minutes, seconds)


def PrintNodeFile(node_dict, filename):
    """
    Prints a node_dict as a .txt file for debugging use
    :param node_dict: dictionary of form {int: Node}
    :param filename: file name to save to
    """
    nodefile = open(filename, 'w')

    for key in node_dict:
        nodefile.write('ID: {0}'.format(key))
        nodefile.write('\n')
        nodefile.write('X: {0}'.format(node_dict[key].X))
        nodefile.write(' Y: {0}'.format(node_dict[key].Y))
        nodefile.write(' I: {0}'.format(node_dict[key].Intensity))
        nodefile.write('\n')
        nodefile.write('Parent: {0}'.format(node_dict[key].Parent))
        nodefile.write(' Children: {0}'.format(node_dict[key].Children))
        nodefile.write('\n')

    nodefile.close()