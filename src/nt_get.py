#!/usr/bin/env python3

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server="192.168.1.21")
nt = NetworkTables.getTable("Peariscope")

count = 0
while True:
    time.sleep(1)
    count += 1
    led_red = int(nt.getNumber("led_red", "N/A"))
    led_grn = int(nt.getNumber("led_grn", "N/A"))
    led_blu = int(nt.getNumber("led_blu", "N/A"))
    print("count", count, "led_red", led_red, "led_grn", led_grn, "led_blu", led_blu)
