# Peariscope Software

Peariscope computer vision software uses
[robotpy-score](https://robotpy.readthedocs.io/en/latest/vision/index.html)
from the
[RobotPy](https://robotpy.readthedocs.io/en/latest/index.html) project.

`multiCameraServer.py` is the original example from FRC that performs simple streaming of multiple cameras as well as camera switching, but contains no computer vision algorithms.

`trivial_camera_demo.py` is a simple example that captures video from a webcam and sends it to the FRC dashboard without any image processing.

`basic_camera_demo.py` is an example that captures video from a webcam and sends it to the FRC dashboard, as well as processing the video (by adding a red rectangle) and publishing the processed video as a second stream.

`peariscope.py` is the complete demonstration software that can be modified for future computer vision needs.

