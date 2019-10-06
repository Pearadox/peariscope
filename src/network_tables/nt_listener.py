#!/usr/bin/env python3

import time
import logging
from networktables import NetworkTables

def connectionListener(connected, info):
    print("{}; Connected={}".format(info, connected))

def valueChanged(table, key, value, isNew):
    print("{}; key: {}; value: {}; isNew: {}".format(table, key, value, isNew))

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='192.168.1.21')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

nt = NetworkTables.getTable("Peariscope")
nt.addEntryListener(valueChanged)

while True:
    time.sleep(1)
