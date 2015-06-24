#neuronroot

#to do:
- implement average radius & total length output
- check for node->north->east sequences (etc) and replace them with node->northeast connections
- investigate the possibility of auto-removing all radius-0 nodes as the last step
- investigate the possibility of true deletion of nodes at all stages instead of lazy deletion
- check for unnecessary algorithmic complexity in redundant-node function - it's very, very slow
- implement smartroot-style cross detection / graph-cycle cross detection
- add statistical output
- add user interface

#v0.5
- Complete rewrite to take advantage of new flowing reconstruction schema and (y,x) indexed dictionary
    - Instead of using Dijkstra's shortest path to connect nodes to a path, simply iterates outward from seed points
    - Then prunes the reconstruction by iteratively removing the outermost layer of nodes until all remaining nodes are part of single-pixel thick skeletal lines
    - Finally, uses a covered-node removal algorithm inspired by Peng et al to deal with imperfections in the reconstruction

#v0.3.1
- Implemented dark-leaf pruning, radius finder, and covered-set finder
- Improved dictionary schema (now uses (y,x) tuples as keys)
- Updated edge search to take advantage of new dictionary (reduces approx. runtime of edge search from 1:50 to 0:05)

#v0.3.0
- Revised tree construction for more complete reconstructions
- Added smooth gradient printing to more easily trace the parent-child connections

#v0.2.0:
- Added preliminary covered-leaf pruning
    - known bugs:
        - nodule trace goes straight through the nodule (maybe check all nodes, not just edge nodes?)

#v0.1.2:
- Added radius construction resources
- Added radius finder function, finally
- Nodes now keep a list of neighbors
- Added preliminary print-by-radius support (looks really weird)
- Fixed print-by-radius

#v0.1.1:
- Added additional input and output formats (notably .tif)
- Built native scaling function (can now input original full sized .tifs)
- Adjusted initial node construction threshold to be more restrictive
- Adjusted remove_dark threshold to be more restrictive
- Set up global variable support and refactored spaghetti code
- Added color support for radius debugging purposes
- Added comments

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