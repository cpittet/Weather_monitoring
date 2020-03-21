#!/bin/python3

# This script :
#   1) Walks through all data samples in the volume directory and send them
#   2) If one of them fails to send, we keep it, otherwise, if it was succesful,
#      we remove it

import os
from os.path import join
import shutil
import json
from influxdb import InfluxDBClient
from sense_hat import SenseHat


# The list of samples to write to the db
points = []

# Loop over all the directories (data samples) in  the volume directory
for roots, dirs, files in os.walk('volume'):
    # Read the data
    for d in dirs:
        with open(join(join('volume', d), 'data.json')) as f:
            data = json.load(f)

        points.append(data)

print(points)


# Connect to the influx db
client = InfluxDBClient(host='192.168.1.124',
                        port=8086,
                        username='collector',
                        password='radis',
                        database='db',
                        timeout=10)

# Sends the data to the influxdb server
success = client.write_points(points)

client.close()

sensor = SenseHat()
sensor.set_rotation(270)

if success:
    # The transfer succeeded, remove the data samples from RP3 volume directory,
    # have to walk through the directories in volume, because rmtree also deletes
    # the root, i.e. the volume directory, but don't want that...
    for roots, dirs, file in os.walk('volume'):
        for d in dirs:
            shutil.rmtree(join('volume', d))

    # Also clear the LEDs on the senseHat, if there were a signal
    sensor.clear()
else:
    # Transfer crashed, display a red '!' on the
    x = [255, 0, 0]
    o = [0, 0, 0]
    error = [
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, o, o,
                    o, o, o, o, o, o, x, x,
                    o, o, o, o, o, o, x, x
                    ]
    sensor.set_pixels(error)
