#!/usr/bin/env python3
'''This NetworkTables client listens for changes in NetworkTables values.'''

import time
from networktables import NetworkTables
import logging

# To see messages from networktables, you must setup logging
logging.basicConfig()

def valueChanged(table, key, value, isNew):
    print("{}; key: {}; value: {}; isNew: {}".format(table, key, value, isNew))

NetworkTables.initialize(server='192.168.1.21')
sd = NetworkTables.getTable("Peariscope")
sd.addEntryListener(valueChanged)

while True:
    time.sleep(1)
