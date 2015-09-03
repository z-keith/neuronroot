#neuronroot v0.9
An automated solution to root system image analysis

#to do:
- *Test method:* Build dictionary of {pixel: roots that cover it}. Look for odd results (any entry with len > 1 that isn't a branch node?)
- *Test method:* Print only pixels with branch points in red, pixels covered by more than one root in green, and those that meet both criteria in white. There shouldn't be any red or green....
- implement Smartroot-style cross detection / graph-cycle cross detection [0.9]
- initial nodule search method: absolute thresholding based on root average diameter [0.9]
- add statistical output [1.0]
- add user interface (display initial click seed point, click ruler, show text output, update to roots image, accept / retry / flag as terrible buttons, final statistical output [1.0]
- add automated nodule detection (via radius expansion detection) [???]

#known bugs/issues:
- program is not set up for automatically pulling from a directory
- program does not include user selection of seed point or scale

#changelog:
##v0.9
- Sorted most occasions where the program iterates through a dictionary or set, making the program have largely consistent outcomes. There's still variation in the root builder that I just can't find for some reason.
- Implemented branch-root scoring functions and total-length remaining function for root segment merging
- Implemented root combining
    - Doesn't work perfectly yet
- Fixed worst of suboptimal tree construction
- Added area whitelists/blacklists to accommodate different image formats

##v0.8
- Implemented basic root construction abilities (roots connect at endpoints to form skeleton - no root has a branch anywhere but at the beginning or end)
- Implemented average radius & total length output on individual and aggregate level
- Noticed that the result of prune_redundant_pixels is not fixed, even on the same file. Need to fix that (perhaps with a sorted list of pixels to iterate through, instead of the unsorted dictionary?)
- Implemented short-'root' removal and root printer. It works pretty well! I think it reveals some flaws in tree construction, though. Going to have to backtrack a bit and see what's going wrong, exactly.
- Doesn't look like there is any benefit to removing radius-0 pixels, as short-root removal handles it just fine
- Reorganized folders to separate input and output, and code from design tools
- prune_redundant_pixels removes a consistent number of pixels, and prioritizes removing lower-intensity pixels
- Similarly, the root creation and short-root pruning now have consistent outputs. These last two changes greatly increased reconstruction quality. 

##v0.7
- Program now checks for pixel->north->east sequences (etc) and replaces them with pixel->northeast connections. This eliminates the appearance of a 2-px wide skeleton for nearly diagonal roots.
- Tested removal of all 0-radius pixels from the representation - the results are promising on a large image, but it costs too much resolution on the scaled image.
    - Revisit this on a large image once short roots are removed (currently, large images have so many short roots that forming any conclusive opinion is impossible).
    - Remember that if you remove all 0-radius pixels, by default remove_internal_pixels will find no results because it starts from the set of pixels with radius 0. This can be addressed by starting from the set where r=1
- Reorganized code to remove redundant code, improve class organization, and better fit program flow
    - What I had been calling "trees" weren't really trees anymore, but an upcoming feature really does use trees. To avoid confusion, the pre-pruning masses of nodes are now called "areas" and the post-pruning structures retain the Tree name 
    - As what I had been calling "nodes" were part of what weren't really "trees", they have been renamed to "pixels".
    - Printing functions have been removed from the old ImageHandler class and moved to their own class, Printer. The ImageHandler class now no longer handles images in general, and has been renamed accordingly to ArrayBuilder
    - Pixel creation and setup functions have been removed from the old TreeHandler and moved to their own class, AreaBuilder. For consistency, the remainder of TreeHandler (the pruning and parent-child connection functions) are now part of TreeBuilder.
    - Comments and docstrings have been completely overhauled, as most of them referred to functionality that has since been updated
- Added an optional fast-print to the initial representation printer that cuts total program runtime by 30%, but only provides a transparent background with a black shadowed image. Not an important performance boost on scaled images, but about 30 seconds on the original.

##v0.6
- Implemented true deletion of nodes, replacing lazy deletion
- Added code to preserve general parent-child relationships when intermediate nodes are deleted
- Caught a bug in redundant-node pruning, cutting runtime from ~11 minutes to <10 seconds

##v0.5
- Complete rewrite to take advantage of new flowing reconstruction schema and (y,x) indexed dictionary
    - Instead of using Dijkstra's shortest path to connect nodes to a path, simply iterates outward from seed points
    - Then prunes the reconstruction by iteratively removing the outermost layer of nodes until all remaining nodes are part of single-pixel thick skeletal lines
    - Finally, uses a covered-node removal algorithm inspired by Peng et al to deal with imperfections in the reconstruction

##v0.3.1
- Implemented dark-leaf pruning, radius finder, and covered-set finder
- Improved dictionary schema (now uses (y,x) tuples as keys)
- Updated edge search to take advantage of new dictionary (reduces approx. runtime of edge search from 1:50 to 0:05)

##v0.3.0
- Revised tree construction for more complete reconstructions
- Added smooth gradient printing to more easily trace the parent-child connections

##v0.2.0:
- Added preliminary covered-leaf pruning
    - known bugs:
        - nodule trace goes straight through the nodule (maybe check all nodes, not just edge nodes?)

##v0.1.2:
- Added radius construction resources
- Added radius finder function, finally
- Nodes now keep a list of neighbors
- Added preliminary print-by-radius support (looks really weird)
- Fixed print-by-radius

##v0.1.1:
- Added additional input and output formats (notably .tif)
- Built native scaling function (can now input original full sized .tif)
- Adjusted initial node construction threshold to be more restrictive
- Adjusted remove_dark threshold to be more restrictive
- Set up global variable support and refactored spaghetti code
- Added color support for radius debugging purposes
- Added comments

##v0.1.0:
Initial git commit. Program currently can:

- Load an image (currently in gif format)
- Threshold and filter an image
- Create initial graph representation of image based on intensity of pixels
- Create weighted edges between adjacent pixels (higher weights caused by bigger differences)
- Find the node that best approximates user-selected seed location
- Build a tree structure with said node as the root
- Find other trees that are significantly large but are not the ruler (this finds scrap roots that are disconnected from the main root)
- Remove dark leaf nodes that were picked up in thresholding for tree-building but are too dark to actually be part of the structure