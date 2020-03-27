#!/bin/python3

# This script :
#   1) Query the raw data that are not cleaned yet from the raw_data measurement
#   2) Fill the values that are 0 to :
#       a) humidity : average of previous and next point (if existent)
#       b) pressure : average of previous and next point (if existent)
#       c) temperature_humidity : average of previous and next point (if existent)
#       d) temperature : same value as temperature_humidity (if existent),
#                        because they seem to be always very close
#       e) temperature_pressure : average of previous and next point (if existent)

from influxdb import InfluxDBClient
import pandas as pd


# Queries the db and returns the generator of the points
# @param : q : string, the query clause
def query(q):
    results = client.query(query, epoch=s)
    return results.get_points()

# Take a generator of points and returns a tuple containing :
# 1) list containing 'temperature' data in ascending order (default in influxdb)
#    i.e. index 0 has the oldest timestamp
# 2) list containing 'temperature_humidity' data in ascending order
# 3) list containing 'temperature_pressure' data in ascending order
# 4) list containing 'humidity' data in ascending order
# 5) list containing 'pressure' data in ascending order
def result_to_np(points_generator):
    temp = []
    temp_p = []
    temp_h = []
    humidity = []
    pressure = []

    for point in points_generator:
        temp.append(point['temperature'])
        temp_p.append(point['temperature_pressure'])
        temp_h.append(point['temperature_humidity'])
        humidity.append(point['humidity'])
        pressure.append(point['pressure'])

    return (temp, temp_h, temp_p, humidity, pressure)



# Connect to influxdb
client = InfluxDBClient(host='192.168.1.124',
                        port=8086,
                        username='collector',
                        password='radis',
                        database='db',
                        timeout=10)

# Query what was the last cleaned data point
query = 'SELECT LAST(time) FROM "db"."raw_data"'
points = query(query)

# Get the number of points : https://stackoverflow.com/questions/393053/length-of-generator-output
size = sum(1 for _ in points)
if size == 0:
    # No data were cleaned yet, so we query all points in raw_data
    query = 'SELECT * FROM "db"."raw_data"'
else:
    for point in points:
        last_cleaned = point['time']
    # Query from the last_cleaned data
    query = 'SELECT * FROM "db"."raw_data" WHERE time > ' + last_cleaned

points = query(query)

temp, temp_h, temp_p, humidity, pressure = result_to_lists(points)
# Create the dict for the df
data = {'temperature':temp,
        'temperature_humidity':temp_h,
        'temperature_pressure':temp_p,
        'humidity':humidity,
        'pressure':pressure}

# Create panda dataframe
df = pd.DataFrame(data)

# Do the cleaning in parallel

client.close()
