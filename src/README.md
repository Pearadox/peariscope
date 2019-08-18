# Peariscope Software

The following hardware was used to build a prototype unit and is available on Amazon.  

`multiCameraServer.py` is the original example from FRC that performs simple streaming of multiple cameras as well as camera switching, but contains no computer vision algorithms.

`camera_demo_1.py` is a simple example that captures video from a webcam and sends it to the FRC dashboard without any image processing.

`camera_demo_2.py` is an example that captures video from a webcam and sends it to the FRC dashboard, as well as processing the video (by adding a red rectangle) and publishing the processed video as a second stream.
