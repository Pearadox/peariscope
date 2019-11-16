#!/usr/bin/env python3

import sys
import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) == 4:
    NetworkTables.initialize(server="192.168.1.21")
    nt = NetworkTables.getTable("Peariscope")

    nt.putNumber("led_red", int(round(float(sys.argv[1]))))
    nt.putNumber("led_grn", int(round(float(sys.argv[2]))))
    nt.putNumber("led_blu", int(round(float(sys.argv[3]))))
    time.sleep(1)
else:
    print("Usage: {} <red> <grn> <blu>".format(sys.argv[0]))
    print("where <red> <grn> <blu> are values between 0 and 255")
