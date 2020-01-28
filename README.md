# Peariscope

Peariscope is a computer vision project for FIRST Robotics Team #5414 [Pearadox](https://pearadox5414.weebly.com/)
that implements robotic _pearception_ to assist with robot navigation and manipulation.  

## Hardware

The Peariscope hardware consists of a Raspberry Pi with a MicroSD memory card, a plastic case,
a camera module (with a case and flex cable), a LED ring light, a level shifter chip, and a power supply.  

Example hardware can be seen here: [Peariscope Hardware](hardware/README.md)

## Operating System

The Peariscope runs on a Raspberry Pi using the FRC Raspberry Pi image.  

FRC Raspberry Pi documentation is available here:
[FRC Raspbery Pi](https://wpilib.screenstepslive.com/s/currentCS/m/85074/l/1027241-using-the-raspberry-pi-for-frc)  

The pre-built FRC Raspberry Pi image is available here:
[FRC Raspberry Pi Image](https://github.com/wpilibsuite/FRCVision-pi-gen/releases)  

## Getting Started

1. Download [FRCVision_image-2019.3.1.zip](https://github.com/wpilibsuite/FRCVision-pi-gen/releases/download/v2019.3.1/FRCVision_image-2019.3.1.zip)
and use [Etcher](https://www.balena.io/etcher/) to image a MicroSD card.  
The MicroSD card needs to be at least 4 GB.  
2. Put the MicroSD card in the Pi and apply power.  
The initial boot may take as long as a minute, but later boots will be much faster (20 seconds or less).  
3. Connect the Pi Ethernet to a LAN.  

## Connecting to the Pi

If the Pi is plugged into the robot radio, we can connect to http://frcvision.local/ using a web browser.
Otherwise, we can connect to the IP address of the Pi.
Note the Pi boots up read-only by default, so it's necessary to click the "writable" button to make changes.  

We can also use [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to login to the Pi via SSH.  
- The login id is: *pi*
- The password is: *raspberry*
- The Pi boots up read-only by default, so it's necessary to use the `rw` command to be able to make changes.
- The `ro` command sets the Pi back to read-only mode, to protect its memory card from damage during power loss.

## Software

The Peariscope software is based on the FRC Vision [Example](https://github.com/wpilibsuite/FRCVision-pi-gen/releases/download/v2019.3.1/example-python-2019.3.1.zip)
that performs simple streaming of multiple cameras and camera switching.
The Peariscope software also holds a custom computer vision algorithm that can be modified, depending on the needs of the team.

The Peariscope computer vision software uses [robotpy-score](https://robotpy.readthedocs.io/en/latest/vision/index.html)
from the [RobotPy](https://robotpy.readthedocs.io/en/latest/index.html) project.

Module `pearistart.py` is based on `multiCameraServer.py` from the FRC examples but is modified to start up `peariscope.py`
which is the custom software that can be modified for the needs of the team.

## Illumination

The Peariscope ring light has 16 individually controllable LEDs.

From the `/home/pi/peariscope/src` folder:  
`sudo ./ringlight_on.py` enables all the lights to a specified color.  
`sudo ./ringlight_off.py` disables all the lights (sets them to black).  

