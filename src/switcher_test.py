#!/usr/bin/env python3
"""This helps test the switched cameras."""

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='192.168.1.21')
sd = NetworkTables.getTable("Peariscope")

while True:
    sd.putString("switch", "Pi")
    time.sleep(1)
    sd.putString("switch", "USB-1")
    time.sleep(1)
    sd.putString("switch", "USB-2")
    time.sleep(1)
