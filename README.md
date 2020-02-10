# SkullRegistration
Tracked ultrasound based registration for skull base surgeries performed in the prone position.

## Supported Hardware
- Telemed L12-5 ultrasound
- OptiTrack trackers
- NDI Polaris trackers

## Use Instructions

#### Installation
- Download and install an "OptiTrack-Telemed-win32" PLUS toolkit version
- Install the following extensions from the Slicer extension manager:
    - SlicerIGT
    - SlicerOpenIGTLink
- Add the ./extensions/AutomaticSurfacePointPlacement and ./extensions/USRegistration paths in the root of this directory to the Slicer additional module paths list.

#### User Instructions
- Start PLUS with the appropriate config file for your hardware setup.
- Wait to ensure PLUS launches with no errors.
- Open Slicer, and navigate to the USRegistration extension (under Registration --> US Skull --> Registration).
- Click on the "Start USRegistration" button.
- Follow the panels in the extension from top to bottom to perform a registration.

## Known Issues
- OptiTrack configs haven't been tested with the latest versions of the source code

## Data Storage
- Testing data: p drive: /home/shared/data/SkullRegistration/
- Data for deep learning: p drive: /home/shared/data/BoneContouring/

## Contributors
- Grace Underwood
- [Abigael Schonewille](https://github.com/ASchonewille)
- [Tamas Ungi](https://github.com/ungi)
- [Andras Lasso](https://github.com/lassoan)
- [Mark Asselin](https://github.com/markasselin)
