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
import config

# Function import declarations
from fImageHandlers import LoadImage, PrintRepresentation
from fBuildOCR import ConstructOCR
from fPruneOCR import PruneOCR

# Main function

def main():
#set filename, seed point, and timestamps
    config.init()

#load and clean up the image
    print("\nLoading image {0}.".format(config.current_file))
    imgpath = "TestImages/" + config.filename + ".tif"
    imgarray = LoadImage(imgpath)

#update global variables
    config.sizeY = imgarray.shape[0]
    config.sizeX = imgarray.shape[1]

#build over-complete representation
    print("\nBuilding initial reconstruction.")
    node_dict = ConstructOCR(imgarray)
    # Uncomment the following to output the results of construction
    #config.PrintNodeFile(node_dict, config.filename + '-nodefile.txt')
    
#prune dark/excess nodes
    print("\nCleaning up reconstruction.")
    clean_dict = PruneOCR(node_dict)
    # Uncomment the following to output the results of pruning
    config.PrintNodeFile(clean_dict, config.filename + '-nodefile-clean.txt')

#build root structure
    print("\nBuilding root objects.")

#calculate total runtime
    elapsed = time.time() - config.start_time
    minutes = str(int(elapsed / 60))
    seconds = str(round((elapsed % 60), 2))
    print("\nComplete!\nTotal runtime: " + minutes + " minutes and " + seconds + " seconds.")

#save image
    PrintRepresentation(node_dict)

# Run statement
main()