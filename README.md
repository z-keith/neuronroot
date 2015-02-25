# neuronroot

#to do:
    - Add size of image, image filename, seed location as global variables
    
#v0.1.1:    
    - Added additional input and output formats (notably .tif)
    - Built native scaling function (can now input original full sized .tifs)
    - Adjusted initial node construction threshold to be more restrictive
    - Adjusted remove_dark threshold to be more restrictive

#v0.1.0:
Initial git commit. Program currently can:

    - Load an image (currently in gif format)
    - Threshold and filter an image
    - Create initial graph representation of image based on intensity of pixels
    - Create weighted edges between adjacent pixels (higher weights caused by 
    bigger differences)
    - Find the node that best approximates user-selected seed location
    - Build a tree structure with said node as the root
    - Find other trees that are significantly large but are not the ruler 
    (this finds scrap roots that are disconnected from the main root)
    - Remove dark leaf nodes that were picked up in thresholding for tree-building
    but are too dark to actually be part of the structure
    