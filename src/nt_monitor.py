#!/usr/bin/env python3
"""This is a NetworkTables client that monitors values."""

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='192.168.1.21')
sd = NetworkTables.getTable("Peariscope")

while True:
    print("fps:", sd.getNumber("fps", "N/A"))
    time.sleep(1)
