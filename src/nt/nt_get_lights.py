#!/usr/bin/env python3

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server="localhost")
nt = NetworkTables.getTable("Peariscope")
time.sleep(1)

led_red = int(nt.getNumber("led_red", -1))
led_grn = int(nt.getNumber("led_grn", -1))
led_blu = int(nt.getNumber("led_blu", -1))

print("led_red", led_red, "led_grn", led_grn, "led_blu", led_blu)
