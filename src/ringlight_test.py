#!/usr/bin/env python3

import board
import neopixel
import time

NUMPIXELS = 16

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)

# Turn off pixels
pixels.fill(BLACK)

while True:
    for i in range(NUMPIXELS-1, -1, -1):
        pixels[i] = RED
        time.sleep(1/NUMPIXELS)
        pixels[i] = GREEN 
