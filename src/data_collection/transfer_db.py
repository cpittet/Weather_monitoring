#!/bin/python3

# Last update : 19.03.2020, Cyrille Pittet

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
for sample_dir, dirs, data_file in os.walk('volume'):
    # Read the data
    with open(join('volume', join(sample_dir, 'data.json')) as f:
        data = json.load(f)

    points.append(data)

# Connect to the influx db
client = InfluxDBClient(host='192.168.1.124',
                        port=8086,
                        username='python_module',
                        password='pt3',
                        database='db',
                        timeout=10)

# Sends the data to the influxdb server
success = client.write_points(points)

client.close()

sensor = SenseHat()
sensor.set_rotation(90)

if success:
    # The transfer succeeded, remove the data samples from RP3 volume directory,
    # have to walk through the directories in volume, because rmtree also deletes
    # the root, i.e. the volume directory, but don't want that...
    for sample_dir, dirs, data_file in os.walk('volume'):
        shutil.rmtree(join('volume', sample_dir))

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
