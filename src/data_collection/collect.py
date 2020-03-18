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
from pathlib import Path
from datetime import date
from sense_hat import SenseHat

sensor = SenseHat()

# Display the letter 'M' (for measuring) in green on white background
sensor.show_letter('M', [0, 255, 0], [255, 255, 255])

# Temperature in Celsius
temperature = sensor.get_temperature()
temperature_from_pressure = sensor.get_temperature_from_pressure();
temperature_from_humidity = sensor.get_temperature_from_humidity();

# Relative percentage of humidity
humidity = sensor.get_humidity()

# Pressure in Millibars
pressure = sensor.get_pressure()

data = {'temperature' : temperature,
        'temperature_pressure' : temperature_from_pressure,
        'temperature_humidity' : temperature_from_humidity,
        'humidity' : humidity,
        'pressure' : pressure}

# Get the date and time
time = date.now().strftime("%Y%m%d%H%M")

# Creates the directory
Path("/usr/src/script/data/"+time.mkdir(exist_ok=True)

# Writes the data in the file data.json
with open('data/'+time+'data.json', 'w') as write_file:
    json.dump(data, write_file)