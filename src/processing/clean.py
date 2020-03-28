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

from influxdb import InfluxDBClient, DataFrameClient
import pandas as pd
import numpy as np


# Queries the db and returns the generator of the points
# Note that the time is in UTC
def query_to_points(query):
    results = client.query(query)
    return results.get_points()

# Take a generator of points and returns a tuple containing :
# 1) list containing 'temperature' data in ascending order of time
#    (default in influxdb) i.e. index 0 has the oldest timestamp
# 2) list containing 'temperature_humidity' data in ascending order
# 3) list containing 'temperature_pressure' data in ascending order
# 4) list containing 'humidity' data in ascending order
# 5) list containing 'pressure' data in ascending order
def result_to_lists(points_generator):
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

# Check if the measurement 'clean_data' exists in the influxdb server
# in database 'db'. If not, then no data have been cleaned yet and
# return False, otherwise, some data have been cleand and return True
def check_clean_measurement(client):
    meas = client.get_list_measurements()
    for m in meas:
        if (m.get('name') == 'convol_signals'):
            return True

    # The clean_data measurement was not found,
    # so no data have been cleand yet
    return False

# Make the right query according to the data that were already cleaned or not
def query_data_to_clean(client):
    if (check_clean_measurement(client)):
        # Measurement alread exists
        # Query what was the last cleaned data point
        query = 'SELECT LAST("temperature") FROM "db"."autogen"."convol_signals"'
        points = query_to_points(query)

        # Get the timestamp of the last cleaned sample, not nice ...
        for point in points:
            last_cleaned = point['time']

        # Query from the last_cleaned data, autogen is the retention policy
        return 'SELECT * FROM "db"."autogen"."data" WHERE "source" = \'sensehat\' AND time > \'' + last_cleaned + '\''

    else:
        # No data were cleaned yet, so we query all points in data
        return 'SELECT * FROM "db"."autogen"."data" WHERE "source" = \'sensehat\''

# Make a convolution on the given column in the dataframe
# with the given filter. Return the result, i.e. an np.array
# the default filter is doing a difference current value - previous value
def convolve_col(col_name,  dataframe, filter=[0, 1, -1]):
    return np.convolve(dataframe[col_name].values, filter, 'same')

# Convolve the entire dataframe (columns by columns) with given filter
# and store the convolved signals into the given dest_df, keeping
# the same columns names. It also sets the 1st element of each column to 0
# as the convolution is just the identity for the 1st element
# with the default filter
def convolve_dataframe(dataframe, dest_df, filter=[0, 1, -1]):
    if (len(dataframe.index) >= 3):
        for col in dataframe.columns:
            if (col != 'time'):
                conv = convolve_col(col, dataframe=dataframe, filter=filter)
                conv[0] = 0
                dest_df[col] = conv



# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

# Connect to influxdb
client = InfluxDBClient(host='192.168.1.124',
                        port=8086,
                        username='collector',
                        password='radis',
                        database='db',
                        timeout=10)

# String of the query to make to get the data to clean
query = query_data_to_clean(client)

# Make the query and get the generator of points
points = query_to_points(query)

# Create panda dataframe
df = pd.DataFrame(points)

# Do the cleaning

# First create a new dataframe which will contains the convolution signals
df_convol = pd.DataFrame()
# Indexes must have a datetime format in order to be directly written to influxdb
df_convol['Datetime'] = pd.to_datetime(df['time'])
df_convol = df_convol.set_index('Datetime')

# Convolve the entire dataframe
convolve_dataframe(df, df_convol)

# Write the convolved signals to the influxdb server
# Connect to DB with a DataFrameClient
df_client = DataFrameClient(host='192.168.1.124',
                            port=8086,
                            username='collector',
                            password='radis',
                            database='db',
                            timeout=10)

if (len(df_convol.index) > 0):
    df_client.write_points(df_convol, 'convol_signals')




# Close the connections to the influxdb server
df_client.close()
client.close()
