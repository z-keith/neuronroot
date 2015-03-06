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

# Class import declarations

# Function import declarations

# Global variable declarations
filename = ""
sizeX = 0
sizeY = 0
seedX = 0
seedY = 0
start_time = 0
last_time = 0
initial_nodecount = 0

current_file = 293

def init():
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

def PrintTimeBenchmark():
    global last_time

    elapsed = time.time() - last_time
    minutes = int(elapsed / 60)
    seconds = str(round((elapsed % 60), 2))
    minutes = str(minutes)
    last_time = time.time()
    if minutes == "1":
        return minutes + " minute and " + seconds + " seconds."
    else:
        return minutes + " minutes and " + seconds + " seconds."

def PrintNodeFile(node_dict, filename):
    nodefile = open(filename, 'w')

    for key in node_dict:
        nodefile.write('ID: ' + str(key) + '\n')
        nodefile.write('X: ' + str(node_dict[key].X))
        nodefile.write(' Y: ' + str(node_dict[key].Y))
        nodefile.write(' I: ' + str(node_dict[key].Intensity) + '\n')
        nodefile.write('Parent: ' + str(node_dict[key].Parent))
        nodefile.write(' Children: ' + str(node_dict[key].Children) + '\n')

    nodefile.close()