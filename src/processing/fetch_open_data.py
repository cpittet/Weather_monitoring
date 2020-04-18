#!/bin/python3

# This script :
#   1) Fetch open data via
#      https://opendata.swiss/en/dataset/automatische-wetterstationen-aktuelle-messwerte
# -> Source: MétéoSuisse, Bundesamt für Meteorologie und Klimatologie
#      we want the temperature, humidity
#   2) Send them directly to the influxdb server

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://requests.readthedocs.io/en/master/user/quickstart/#make-a-request
# https://www.pluralsight.com/guides/extracting-data-html-beautifulsoup

import pandas as pd
from influxdb import InfluxDBClient


# ------------------------------------------------------------------------------
# Constants
IP_RP4 = '192.168.1.124'
PORT = 8086
USER_NAME = 'collector'
PWD = 'radis'
DB_NAME = 'db'

# ------------------------------------------------------------------------------

# Source : MétéoSuisse, Bundesamt für Meteorologie und Klimatologie
# obtained via https://opendata.swiss/en/dataset/automatische-wetterstationen-aktuelle-messwerte
URL = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'

# Directly fetch the csv file containing the data,
# and put it into a panda dataframe
# it is ';' separator in the file and we want to drop the first 2 rows
df = pd.read_csv(URL, sep=';', skiprows=2)


# Read the temperature
temp = df.loc[df['stn'] == 'MAS', 'tre200s0'].values[0]
if temp != '-':
    temp = float(temp)
else:
    temp = float("inf")

# Read the humidity
humidity = df.loc[df['stn'] == 'MAS', 'ure200s0'].values[0]
if humidity != '-':
    humidity = float(humidity)
else:
    humidity = float(-10)

# Read the time when the data where measured, have to substract 1h
# due to the time format in influxdb
time = str(df.loc[df['stn'] == 'MAS', 'time'].values[0])
timestamp = time[:4]+'-'+time[4:6]+'-'+time[6:8]+'T'+str((int(time[8:10]) - 1)%24)+':'+time[10:]+'Z'

# Format the data as a point in json
point = [{
    'measurement': 'data',
    'tags': {
        'source': 'meteosuisse'
    },
    'time': timestamp,
    'fields': {
        'temperature': temp,
        'temperature_pressure': float(0),
        'temperature_humidity': float(0),
        'humidity': humidity,
        'pressure': float(0)
    }
}]

# Connect to the influxdb server
client = InfluxDBClient(host=IP_RP4,
                        port=PORT,
                        username=USER_NAME,
                        password=PWD,
                        database=DB_NAME,
                        timeout=10)

# Write the point to the server
client.write_points(point)

client.close()
