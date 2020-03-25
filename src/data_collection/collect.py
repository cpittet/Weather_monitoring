#!/bin/python3

# Last update : 18.03.2020, Cyrille Pittet

# This script :
#   1) Collect the temperature, the pressure and the humidity
#      from the SenseHat sensor. While it is measuring, it displays
#      a shape on the LED matrix
#   2) It creates a directory with the following format name 'YYYYMMDDHHmm'
#   3) It writes the measured data into that directory
#      as a dictionnary using json format

import json
import time
from pathlib import Path
from datetime import datetime
from sense_hat import SenseHat

sensor = SenseHat()
sensor.set_rotation(270)

# Display the letter 'M' (for measuring) in green on white background
sensor.clear()
sensor.show_letter('M', [0, 255, 0])

# Temperature in Celsius
temperature = float(sensor.get_temperature())
temperature_from_pressure = float(sensor.get_temperature_from_pressure())
temperature_from_humidity = float(sensor.get_temperature_from_humidity())

# Relative percentage of humidity
humidity = float(sensor.get_humidity())

# Pressure in Millibars
pressure = float(sensor.get_pressure())

# Get the current time of the measurement
timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

data = {
        'measurement': 'data',
        'tags': {
            'source': 'sensehat'
        },
        'time': timestamp,
        'fields': {
            'temperature': temperature,
            'temperature_pressure': temperature_from_pressure,
            'temperature_humidity': temperature_from_humidity,
            'humidity': humidity,
            'pressure': pressure
        }
}

# Get the date and time
cur_time = datetime.now().strftime("%Y%m%d%H%M")

# Creates the directory
Path("volume/"+cur_time).mkdir(exist_ok=True)

# Writes the data in the file data.json
with open('volume/'+cur_time+'/data.json', 'w') as write_file:
    json.dump(data, write_file)

time.sleep(5)

sensor.clear()
