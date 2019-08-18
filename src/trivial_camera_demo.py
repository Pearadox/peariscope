#!/usr/bin/env python3
"""Captures video from a webcam and sends it to the FRC dashboard without any image processing."""

from cscore import CameraServer
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize networktables as as server
NetworkTables.initialize()

cs = CameraServer.getInstance()
cs.enableLogging()
cs.startAutomaticCapture(name="Camera", path="/dev/video0")
cs.waitForever()
