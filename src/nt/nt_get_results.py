#!/usr/bin/env python3

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server="localhost")
nt = NetworkTables.getTable("Peariscope")
time.sleep(1)

while True:
    print("x_list", nt.getNumberArray("x_list", "?"), "y_list", nt.getNumberArray("y_list", "?"))
    time.sleep(1)
