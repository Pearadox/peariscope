#!/usr/bin/env python3

import os
import sys
import board
import neopixel
import time
import signal

def handler(signal_received, frame):
    # Turn off the lights and exit when ctrl-C is pressed
    for i in range(NUMPIXELS):
        pixels[i] = (0, 0, 0)
    sys.exit(0)

if os.geteuid() != 0:
    print("usage: sudo", sys.argv[0])
    sys.exit(1)

NUMPIXELS = 16
pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)
signal.signal(signal.SIGINT, handler)

while True:
    for i in range(NUMPIXELS-1, -1, -1):
        pixels[i] = (255, 0, 0) # Red
        time.sleep(1/NUMPIXELS)
        pixels[i] = (0, 255, 0) # Green
