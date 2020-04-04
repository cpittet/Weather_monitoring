#!/bin/python3

# This module :
#   1) format a pandas Dataframe, containing 2 columns (temperature and humidity)
#   2) In particular, it interpolates the given data to output a pandas
#      Dataframe with data for every hour

import pandas as pd
import numpy as np

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# Round the time value of the given date time value to the lower whole minute
def round_time(time):
    return time[:-4] + '00Z'

# Rounds the each element of the time column in the given DataFrame
def round_time_columns(df):
    for i in range(0, len(df.index)):
        df['time'].values[i] = round_time(df['time'].values[i])

# Returns the date as an int formated as follows : YYYYMMDD, so that we can
# directly compare the int to see if a date is before another or not
def get_date(time):
    return int(time[:4])*(10**4) + int(time[5:7])*(10**2) + int(time[8:10])

# Returns the hour min sec as an int formated as follows : hhmmss, so that we
# can directly compare the int to see if a hour is before another or not
def get_hour(time):
    return int(time[11:13])*(10**4) + int(time[14:16])*(10**2) + int(time[17:19])

# Returns the complete date and time as an int formated as follows :
# YYYYMMDDhhmmss, so that we can directly compare the int to check if a datetime
# is before another or not
def get_time(time):
    return get_date(time)*(10**6) + get_hour(time)

# Test if time t1 is smaller, i.e. before time t2, returns True if yes,
# otherwise False
def before(t1, t2):
    return get_time(t1) < get_time(t2)

# Test if time t1 is equat to time t2, returns True if yes,
# otherwise False
def equal(t1, t2):
    return get_time(t1) == get_time(t2)

# Returns the value at index i in the column 'time' of the given dataframe
def get_index(df, i, col='time'):
    if (i >= 0 and i < len(df.index)):
        return df[col].values[i]


# Format the values of the given column col from the src_df dataframe and write
# the results into the corresponding column col in the dst_df dataframe.
# It puts a Nan when the required data in src_df is not present
def make_formated_column(dst_df, src_df, col):
    # At the begining, check if there are the required values,
    # while the dst time is before the first src time, we put nan into dst
    i = 0
    while(before(get_index(dst_df, i), get_index(src_df, 0))
          and i < len(dst_df.index)):
        dst_df[col].values[i] = np.nan
        i += 1

    # The index for the src_df array
    s = 0
    # Now we reach the first equal or "after" time
    while(i < len(dst_df.index) and s < len(src_df.index)):
        # Seek the last src sample that have a time less or equal to the needed
        # dst_df sample time to fill at index i
        while(before(get_index(src_df, s), get_index(dst_df, i))
              and s < len(src_df.index)):
            s += 1

        # Reached the src sample that has a time equal or superior to the dst
        # sample we need to fill
        if (equal(get_index(src_df, s), get_index(dst_df, i))):
            dst_df[col].values[i] = src_df[col].values[s]
        else:
            # Then it means the src sample at index s is the first after the
            # dst sample we need to fill, so we interpolate between the src
            # sample at index s-1 and the one at index s
            start = get_hour(get_index(src_df, s-1))
            end = get_hour(get_index(src_df, s))
            y1 = get_index(src_df, s-1, col=col)
            y2 = get_index(src_df, s, col=col)

            point = get_hour(get_index(dst_df, i)) - start
            dst_df[col].values[i] = (y2 - y1) / (end - start) * point

        i += 1



# Format the given columns in the list columns from the src_df dataframe
# into dst_df dataframe, writing Nan values where
# the corresponding needed value is missing in the src_df. Passed by value of
# a "pointer" to the df so no need to return the result
def format_dataframe(dst_df, src_df, columns):
    round_time_columns(src_df)
    for col in columns:
        make_formated_column(dst_df, src_df, col)
