cmake_minimum_required(VERSION 3.5)

project(AutomaticSurfacePointPlacement)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/AutomaticSurfacePointPlacement")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS " Abigael Schonewille (PerkLab)")
set(EXTENSION_DESCRIPTION "An extension created for use in the ultrasound registration for skull base surgeries project. 

This extension allows a loaded deep learning algorithm to segment out the placement of the skull in a sequence of ultrasound images and then creates a new markups node of surface points on the skull with a minimum distance. 

The created markups node with surface points is intended for ICP registration of the ultrasound images to a 3D model of the skull. 
")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/AutomaticSurfacePointPlacement.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/AutomaticSurfacePointPlacement/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(AutomaticSurfacePointPlacement)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
