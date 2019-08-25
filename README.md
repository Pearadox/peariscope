# Peariscope

Peariscope is a computer vision project for FIRST Robotics Team #5414 [Pearadox](http://https://pearadox5414.weebly.com/) that implements robot _pearception_ to assist with robot navigation and manipulation.

## Peariscope Hardware

The Peariscope hardware consists of a Raspberry Pi with a MicroSD memory card, a night vision camera with a _pear_ of infrared LEDs, a power supply, and an optional case.  Example hardware can be seen here:
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

## Connecting to the Pi

If the Pi is plugged into the robot radio, we can connect to http://frcvision.local/ using a web browser.
Otherwise, we can connect to the IP address of the Pi.
Note the Pi boots up read-only by default, so it's necessary to click the "writable" button to make changes.  

We can also use [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to login to the pi via SSH.  
- The login id is: *pi*
- The password is: *raspberry*
- The Pi boots up read-only by default, so it's necessary to use the `rw` command to be able to make changes.
- The `ro` command sets the Pi back to read-only mode, to protect its memory card from damage during power loss.

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

## Illumination

Visible light is electromagetic radiation in the range of wavelengths that is visible to the _human_ eye.
The visible light spectrum typically ranges from 700 nanomenters (lower frequency) to 400 nanometers (higher frequency).
Each individual wavelength corresponds to a specific color that our eye perceives.

The infrared light spectrum has longer wavelengths and extends from the red edge of the visible spectrum (700nm) to a wavelength of 1 mm.
Night vision cameras are sensitive to wavelengths in the IR spectrum and are commonly used for security applications,
because their _invisible_ light allows them to observe humans and animals without detection.

Commonly available infrared lights (_illuminators_) typically emit light with a 850 nm wavelength,
simply beacause most day/night cameras with removable IR cut filters have great sensitivity to this wavelength.
A faint red glow can be observed when using these lights.

### Safety

Infrared light, in sufficient concentrations, can cause damage to the human eye, however, to date, light-emitting Diodes (LEDs) have not been found
to cause any damage.

from [Sciencing.com](https://sciencing.com/infrared-light-effect-eyes-6142267.html)

>All infrared, visible or ultraviolet electromagnetic radiation can cause injury to the eye in sufficient concentrations, but this is very rare. The infrared light needs to be extremely intense to cause harm. It is important to take precautions, because infrared light is invisible, meaning your eyes won't take the protective measures like blinking or closing when a high-intensity beam of infrared radiation shines into them. In extreme cases, if the eyes absorb too much infrared light, they can be irreversibly damaged. Infrared lamps and incandescent bulbs are not powerful enough to cause such harm. But it's best if you don't stare directly at them for too long. Staring at any light source, including the sun, for too long can cause damage to the eyes, particularly in young people.

