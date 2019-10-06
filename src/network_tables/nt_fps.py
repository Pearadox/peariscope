#!/usr/bin/env python3

import time
import logging
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='192.168.1.21')
nt = NetworkTables.getTable("Peariscope")

while True:
    print("fps:", nt.getNumber("fps", "N/A"))
    time.sleep(1)
