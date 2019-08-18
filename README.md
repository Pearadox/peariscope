# Peariscope

Computer vision project for FIRST Robotics Team #5414 [Pearadox](http://https://pearadox5414.weebly.com/).

## Peariscope Hardware

The Peariscope hardware consists of a Raspberry Pi with a MicroSD memory card, a night vision camera with infrared LEDs, a power supply, and an optional case.  Example hardware can be seen here:
[Peariscope Hardware](hardware/README.md)

## Peariscope OS

The Peariscope runs on a Raspberry Pi using the FRC Raspberry Pi image.

FRC Raspberry Pi documentation is available here:
[FRC Raspbery Pi](https://wpilib.screenstepslive.com/s/currentCS/m/85074/l/1027241-using-the-raspberry-pi-for-frc)

The pre-built FRC Raspberry Pi image is available here:
[FRC Raspberry Pi Image](https://github.com/wpilibsuite/FRCVision-pi-gen/releases)

## Getting Started

1. Download [FRCVision_image-2019.3.1.zip](https://github.com/wpilibsuite/FRCVision-pi-gen/releases/download/v2019.3.1/FRCVision_image-2019.3.1.zip) and use [Etcher](https://www.balena.io/etcher/) to image a MicroSD card.  
The MicroSD card needs to be at least 4 GB.  
2. Put the MicroSD card in the Pi and apply power.  
The initial boot may take as long as a minute, but later boots will be much faster (20 seconds or less).  
3. Connect the Pi ethernet to a LAN.  
Open a web browser and connect to http://frcvision.local/ if the Pi is plugged into the robot radio, or use the IP address of the Pi if it is not.  
Note the image boots up read-only by default, so it's necessary to click the "writable" button to make changes.  

## Peariscope Software

The Peariscope software is based on the FRC Vision [example](https://github.com/wpilibsuite/FRCVision-pi-gen/releases/download/v2019.3.1/example-python-2019.3.1.zip)
that performs simple streaming of multiple cameras and camera switching.
The Peariscope software also holds a custom computer vision algorithm that can be modified, depending on the needs of the team.

### Software Examples

The Peariscope computer vision software uses
[robotpy-score](https://robotpy.readthedocs.io/en/latest/vision/index.html)
from the
[RobotPy](https://robotpy.readthedocs.io/en/latest/index.html) project.

`multiCameraServer.py` is the original example from FRC that performs simple streaming of multiple cameras as well as camera switching, but contains no computer vision algorithms.

`trivial_camera_demo.py` is a simple example that captures video from a webcam and sends it to the FRC dashboard without any image processing.

`basic_camera_demo.py` is an example that captures video from a webcam and sends it to the FRC dashboard, as well as processing the video (by adding a red rectangle) and publishing the processed video as a second stream.

`peariscope.py` is the complete demonstration software that can be modified for future computer vision needs.

