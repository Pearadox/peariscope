#!/usr/bin/env python3

import os
import sys
import board
import neopixel

def usage():
    print("usage: sudo", sys.argv[0], "red grn blu")
    print("  red: the red intensity (0 to 255)")
    print("  grn: the green intensity (0 to 255)")
    print("  blu: the blue intensity (0 to 255)")

if os.geteuid() != 0:
    usage()
    sys.exit(1)

if len(sys.argv) != 4:
    usage()
    sys.exit(1)

NUMPIXELS = 16
pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)
red = int(round(float(sys.argv[1])))
grn = int(round(float(sys.argv[2])))
blu = int(round(float(sys.argv[3])))
for i in range(NUMPIXELS):
    pixels[i] = (red, grn, blu)
