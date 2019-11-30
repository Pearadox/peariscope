#!/usr/bin/env python3

import sys
import board
import neopixel

NUMPIXELS = 16
pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)

if len(sys.argv) == 4:
    red = int(round(float(sys.argv[1])))
    grn = int(round(float(sys.argv[2])))
    blu = int(round(float(sys.argv[3])))
    pixels.fill((red, grn, blu))
else:
    pixels.fill((0, 255, 0)) # Green
