#!/bin/python3

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Walks through all data samples in the volume directory and send them
#   2) If one of them fails to send, we keep it, otherwise, if it was succesful,
#      we remove it

import os
from os.path import join
import json
from influxdb import InfluxDBClient

# The list of samples to write to the db
samples = []

# Loop over all the directories (data samples) in  the volume directory
for sample_dir, dirs, data_file in os.walk('volume'):
    # Read the data
    with open(join('volume', join(sample_dir, 'data.json')) as f:
        data = json.load(f)

    samples.append(data)



# Connect to the influx db
client = InfluxDBClient(host='192.168.1.124',
                        port=8086,
                        username='admin',
                        password='radis',
                        database='dbname',
                        timeout=10)
