# Peariscope

Computer vision project for FIRST Robotics Team #5414 Pearadox.

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
