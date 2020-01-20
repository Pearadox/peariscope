#!/usr/bin/env python3

import os
import sys
import board
import neopixel

if os.geteuid() != 0:
    print("usage: sudo", sys.argv[0])
    sys.exit(1)

NUMPIXELS = 16
pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)
for i in range(NUMPIXELS):
    pixels[i] = (0, 255, 0)
