#!/usr/bin/env python3

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server="10.54.14.20")
nt = NetworkTables.getTable("Peariscope")
time.sleep(1)

while True:
    led_red = int(nt.getNumber("led_red", "N/A"))
    led_grn = int(nt.getNumber("led_grn", "N/A"))
    led_blu = int(nt.getNumber("led_blu", "N/A"))
    print("led_red", led_red, "led_grn", led_grn, "led_blu", led_blu)
    time.sleep(1)
