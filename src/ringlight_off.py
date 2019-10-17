#!/usr/bin/env python3

import board
import neopixel

NUMPIXELS = 16

pixels = neopixel.NeoPixel(board.D18, NUMPIXELS)
pixels.fill((0, 0, 0)) # RGB -- black/off

