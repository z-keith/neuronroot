# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       main.py
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    main file for neuron-based root trace program
#   references= Peng et al, http://bioinformatics.oxfordjournals.org/content/27/13/i239.full.pdf
#               Lobet et aL, http://www.plantphysiol.org/content/157/1/29.full.pdf
#               van der Walt et al, http://dx.doi.org/10.7717/peerj.453
#               networkX citation here
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import time
import os

# Class import declarations
from cRoot import Root, Node

# Function import declarations
from fImageHandlers import LoadImage, PrepImage, PrintRepresentation
from fBuildOCR2 import ConstructOCR, PrintTimeBenchmark
from fPruneOCR import PruneOCR
from fTraceRoots import *
from fDeclareNodules import *

# Main function

def main():
    #initialize timer
    start_time = time.time()
    last_time = time.time()

    #load and clean up the image

    os.environ["FILENAME"] = "2014-06-24-Tri-293"
    #os.environ["FILENAME"] = "2014-06-26-Tri-329"

    imgpath = "TestImages/" + os.environ["FILENAME"] + ".tif"
    imgarray = LoadImage(imgpath)
    imgarray = PrepImage(imgarray)

    os.environ["YSIZE"] = str(imgarray.shape[0])
    os.environ["XSIZE"] = str(imgarray.shape[1])

    #set seedpoint (293)
    os.environ["SEED_XLOC"] = "1146"
    os.environ["SEED_YLOC"] = "80"

    #set seedpoint (329)
    #os.environ["SEED_XLOC"] = "901"
    #os.environ["SEED_YLOC"] = "432"

    print("\nCompleted load and threshold in " + PrintTimeBenchmark(last_time) + "\n")
    last_time = time.time()

    #build over-complete representation
    print("Building initial reconstruction.\n")
    node_dict = ConstructOCR(imgarray)
    nodefile = open('nodefile.txt', 'w')
    for key in node_dict:
        nodefile.write('ID: ' + str(key) + '\n')
        nodefile.write('X: ' + str(node_dict[key].X))
        nodefile.write(' Y: ' + str(node_dict[key].Y))
        nodefile.write(' I: ' + str(node_dict[key].Intensity) + '\n')
        nodefile.write('Parent: ' + str(node_dict[key].Parent))
        nodefile.write(' Children: ' + str(node_dict[key].Children) + '\n')

    print("\nCompleted OCR in " + PrintTimeBenchmark(last_time) + "\n")
    last_time = time.time()
    
    #prune dark/excess nodes
    print("Cleaning up reconstruction.\n")
    clean_dict = PruneOCR(node_dict)
    nodefile = open('nodefile_clean.txt', 'w')
    for key in clean_dict:
        nodefile.write('ID: ' + str(key) + '\n')
        nodefile.write('X: ' + str(clean_dict[key].X))
        nodefile.write(' Y: ' + str(clean_dict[key].Y))
        nodefile.write(' I: ' + str(clean_dict[key].Intensity) + '\n')
        nodefile.write('Parent: ' + str(clean_dict[key].Parent))
        nodefile.write(' Children: ' + str(clean_dict[key].Children) + '\n')

    print("\nPruned OCR in " + PrintTimeBenchmark(last_time) + "\n")
    last_time = time.time()

    #build root structure
    print("Building root objects.\n")

    print("Root objects built in " + PrintTimeBenchmark(last_time) + "\n")
    last_time = time.time()
    
    print("Total root length: " + "pixels.")

    #calculate total runtime
    elapsed = time.time() - start_time
    minutes = int(elapsed / 60)
    seconds = str(round((elapsed % 60), 2))
    minutes = str(minutes)
    print("Complete!\nTotal runtime: " + minutes + " minutes and " + seconds + " seconds.")

    PrintRepresentation(node_dict, int(os.environ["XSIZE"]), int(os.environ["YSIZE"]))

# Run statement
main()