#!/usr/bin/env python3

import board
import neopixel
import time

NUMPIXELS = 16

BLK = (0, 0, 0)
WHT = (255, 255, 255)
RED = (255, 0, 0)
GRN = (0, 255, 0)
BLU = (0, 0, 255)

pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)

# Turn off pixels
pixels.fill(BLK)

while True:
    for i in range(NUMPIXELS-1, -1, -1):
        pixels[i] = BLK
        time.sleep(1/NUMPIXELS)
        pixels[i] = GRN 
