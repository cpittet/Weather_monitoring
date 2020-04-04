#!/bin/python3

# This script :
#   1) Query the raw data that are not cleaned yet from the raw_data measurement
#   2) Correct the anormal values detected by mean of a convolution :
#       a) humidity : average of previous and next point (if existent)
#       b) pressure : average of previous and next point (if existent)
#       c) temperature_humidity : average of previous and next point (if existent)
#       d) temperature : same value as temperature_humidity (if existent),
#                        because they seem to be always very close
#       e) temperature_pressure : average of previous and next point (if existent)

import sys
from influxdb import InfluxDBClient, DataFrameClient
import pandas as pd
import numpy as np

# ------------------------------------------------------------------------------
# Constants
THRESHOLDS = {'temperature' : 5, 'humidity' : 7, 'pressure' : 1,
              'temperature_humidity' : 5,
              'temperature_pressure' : 5}
IP_RP4 = '192.168.1.124'
PORT = 8086
USER_NAME = 'collector'
PWD = 'radis'
DB_NAME = 'db'

# ------------------------------------------------------------------------------
# Functions


# Query the db and returns the generator of the points
# Note that the time is in UTC
def query_to_points(query, client):
    results = client.query(query)
    return results.get_points()

# Query the db for the convolution signal, from the specified sample
def query_convolution(client, from_time):
    query = ('SELECT * FROM "db"."autogen"."convol_signals" '
            +'WHERE time >= \'' + from_time + '\'')
    return query_to_points(query, client)

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
    # so no data have been cleaned yet
    return False

# Make the right query according to the data that were already cleaned or not
# and the given source tag value. Can pass directly the timestamp of last
# cleaned data (if you have it) to avoid seeking it again. When giving
# a fields argument you should put i in double quotes (e.g. '"temperature"')
# Returns (timestamp of last cleand sample, string of the query)
def query_data_to_clean(client, source, last_cleaned=0, update_last_cleaned=True, fields='*'):
    if (check_clean_measurement(client) and not(last_cleaned == 0 and not(update_last_cleaned))):
        # Measurement already exists

        if (update_last_cleaned):
            # Query what was the last cleaned data point
            query = 'SELECT LAST("temperature") FROM "db"."autogen"."convol_signals"'
            points = query_to_points(query, client)

            # Get the timestamp of the last cleaned sample, not nice ...
            for point in points:
                last_cleaned = point['time']

        # Query from the last_cleaned data, autogen is the retention policy
        query = ('SELECT ' + fields + ' FROM "db"."autogen"."data" WHERE "source" = \''
                 + source + '\' AND time > \'' + str(last_cleaned) + '\'')

        return (last_cleaned, query)

    else:
        # No data were cleaned yet, so we query all points in data
        return (0,
                ('SELECT ' + fields + ' FROM "db"."autogen"."data" WHERE "source" = \''
                + source + '\''))

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

# Clean the given column with the specified rules below (see function clean_data)
# The mode specify the techniques used to correct values : average or copy
def clean_column(dataframe, dataframe_convol, col, mode='average'):
    # Assignement is by reference, so no need to reassign it later
    values = dataframe[col].values
    convol = dataframe_convol[col].values

    # Detect the indexes where the corresponding threshold is exceeded
    anormal_index = np.argwhere(np.absolute(convol) > THRESHOLDS[col])

    if (mode == 'average'):
        for i in anormal_index:
            if (i > 0 and i < values.shape[0] - 1):
                # I.e. there exist previous and next values
                values[i] = (values[i-1] + values[i+1]) / 2.0
            elif (i > 0):
                # I.e. there is no next value
                values[i] = values[i-1]
            else:
                # I.e. there is no previous value
                values[i] = values[i+1]
    else:
        # I.e. copy method, only for temperature
        for i in anormal_index:
            values[i] = dataframe['temperature_humidity'].values[i]



# Correct the anormal values spotted by the convolution signal
# Correct (in order):
#   1) Humidity : average of previous and next values (if existent)
#   2) Pressure : average of previous and next values (if existent)
#   3) Temperature_humidity : average of previous and next values (if existent)
#   4) Temperature_pressure : average of previous and next values (if existent)
#   5) Temperature : same value as the temperature_humidity,
#                    because they seem very close. In worst case,
#                    it takes the corrected value of temperature_humidity
# It takes the dataframe to clean and the dataframe of the convolution in args
def clean_data(dataframe, dataframe_convol):
    columns = ['humidity', 'pressure',
               'temperature_humidity', 'temperature_pressure', 'temperature']
    for col in columns:
        if (col == 'temperature'):
            clean_column(dataframe, dataframe_convol, col, mode='copy')
        else:
            clean_column(dataframe, dataframe_convol, col, mode='average')


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Script
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

# Connect to influxdb
client = InfluxDBClient(host=IP_RP4,
                        port=PORT,
                        username=USER_NAME,
                        password=PWD,
                        database=DB_NAME,
                        timeout=10)

# String of the query to make to get the data to clean
last_cleaned_time, query = query_data_to_clean(client, 'sensehat')

# Make the query and get the generator of points
points = query_to_points(query, client)

# Create panda dataframe
df = pd.DataFrame(points)

# If there is no data to clean, exit
if (len(df.index) <= 0):
    client.close()
    sys.exit()


# ------------------------------------------------------------------------------
# Cleaning
# ------------------------------------------------------------------------------
# Do the convolutions

# First create a new dataframe which will contains the convolution signals
df_convol = pd.DataFrame()

# Indexes must have a datetime format in order to be directly written to influxdb
df_convol['Datetime'] = pd.to_datetime(df['time'])
df_convol = df_convol.set_index('Datetime')

# Convolve the entire dataframe
convolve_dataframe(df, df_convol)

# Connect to DB with a DataFrameClient
df_client = DataFrameClient(host=IP_RP4,
                            port=PORT,
                            username=USER_NAME,
                            password=PWD,
                            database=DB_NAME,
                            timeout=10)

# Write the convolved signals to the influxdb server
if (len(df_convol.index) > 0):
    df_client.write_points(df_convol, 'convol_signals')

# ------------------------------------------------------------------------------
# Correct the anormal values

# The result dataframe is now the original df
# !!! Normally, elements at the same index in dataframe df and df_convol
# correspond to the same timestamp (as this script is exectued in its
# completeness via a cron job, so both index the same time range). However,
# if e.g. only the convolution is done and later the cleaning, then they won't
# have the same indexing. To avoid this, we query again the db for the correct
# time range, so we don't have problems with indexing
from_time = df['time'].values[0]
df_convol = pd.DataFrame(query_convolution(client, from_time))

print(df)
print(df_convol)
# Clean the data
clean_data(df, df_convol)
print(df)

# ------------------------------------------------------------------------------
# Now fetch the meteo suisse data and adjust,
# we don't want to again search for last sample in the convolution signal
# as we just wrote the new convolved samples
last_cleaned_time, query = query_data_to_clean(client,
                                               source='meteosuisse',
                                               last_cleaned=last_cleaned_time,
                                               update_last_cleaned=False,
                                               fields='"temperature", "humidity"')
points_ms = query_to_points(query, client)
df_ms = pd.DataFrame(points_ms)

print(df_ms)

# Close the connections to the influxdb server
df_client.close()
client.close()
