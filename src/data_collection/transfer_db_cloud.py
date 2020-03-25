#!/bin/python3

# This script :
#   1) Walks through all data samples in the volume directory and send them
#   2) If one of them fails to send, we keep it, otherwise, if it was succesful,
#      we remove it

import os
from os.path import join
import json
from influxdb import InfluxDBClient


# The list of samples to write to the db
points = []

# Loop over all the directories (data samples) in  the volume directory
for roots, dirs, files in os.walk('volume'):
    # Read the data
    for d in dirs:
        with open(join(join('volume', d), 'data.json')) as f:
            data = json.load(f)

        points.append(data)

# Connect to the influx db
client = InfluxDBClient(host='35.195.126.33',
                        port=8086,
                        username='admin',
                        password='_A83\|/bsT3-',
                        database='db',
                        timeout=10)

# Sends the data to the influxdb server
success = client.write_points(points, time_precision='ms')

client.close()

if success:
    # The transfer succeeded
    print('success')
