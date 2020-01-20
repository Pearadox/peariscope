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
    results_x = nt.getNumberArray("x_list", "")
    results_y = nt.getNumberArray("y_list", "")
    num_results = len(results_x)
    print()
    print("I see", num_results, "reflectors")
    if num_results == 2:
        distance_x = abs(results_x[0] - results_x[1])
        distance_y = abs(results_y[0] - results_y[1])
        print("They are", distance_x, "pixels apart horizontally")
        print("They are", distance_y, "pixels apart vertically")
    time.sleep(1)
