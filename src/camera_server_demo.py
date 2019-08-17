#!/usr/bin/env python3
"""Captures video from a webcam and sends it to the FRC dashboard after processing."""

from cscore import CameraServer
from networktables import NetworkTables
import logging
import numpy as np
import cv2

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize networktables as as server
NetworkTables.initialize()

cs = CameraServer.getInstance()
cs.enableLogging()
camera = cs.startAutomaticCapture(name="Camera", path="/dev/video0")
camera.setResolution(640, 480)

# Capture images from the camera
cvSink = cs.getVideo()

# Send images back to the Dashboard
outputStream = cs.putVideo("Processed", 640, 480)

# Preallocate space for new images
img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)

while True:
    # Grab a frame from the camera and put it in the source image
    time, img = cvSink.grabFrame(img)

    # If there is an error then notify the output and skip the iteration
    if time == 0:
        outputStream.notifyError(cvSink.getError())
        continue

    # Operate on the image
    RED = (0, 0, 255)
    cv2.rectangle(img, (100, 100), (400, 400), RED, 3)

    # Give the output stream a new image to display
    outputStream.putFrame(img)

