cmake_minimum_required(VERSION 3.13.4)

project(SkullRegistration)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/SkullRegistration")
set(EXTENSION_CATEGORY "SkullRegistration")
set(EXTENSION_CONTRIBUTORS "Abigael Schonewille (PerkLab, Queen's University), Tamas Ungi (PerkLab, Queen's University), Mark Asselin (PerkLab, Queen's University)")
set(EXTENSION_DESCRIPTION "Extension for tracked ultrasound based skull registration, specifically targeting surgeries performed in the prone position.

This extension enables the use of a deep learning algorithm to segment the skull's surface in a sequence of ultrasound images. Markups are then created on this surface which are intended for ICP registration of the ultrasound images to a 3D model of the skull. 
")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SkullRegistration.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SkullRegistration/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(AutomaticSurfacePointPlacement)
add_subdirectory(USRegistration)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
