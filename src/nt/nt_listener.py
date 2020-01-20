#!/usr/bin/env python3

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

def valueChanged(table, key, value, is_new):
    print('{}; key: {}; value: {}; is_new: {}'.format(table, key, value, is_new))

NetworkTables.initialize(server='10.54.14.20')
sd = NetworkTables.getTable('Peariscope')
sd.addEntryListener(valueChanged)

while True:
    time.sleep(1)
