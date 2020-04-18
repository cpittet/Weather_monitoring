#!/bin/python3

# This module :
#   1) format a pandas Dataframe, containing 2 columns (temperature and humidity)
#   2) In particular, it interpolates the given data to output a pandas
#      Dataframe with data for every hour

import numpy as np

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

#
def get_date(time):
    """
    Returns the date as an int formated as follows : YYYYMMDD, so that we can
    directly compare the int to see if a date is before another or not
    :param time: string of the time
    :return: the time as an int formated as YYYYMMDD
    """
    return int(time[:4])*(10**4) + int(time[5:7])*(10**2) + int(time[8:10])


def get_hour(time):
    """
    Returns the hour min sec as an int formated as follows : hhmmss, so that we
    can directly compare the int to see if a hour is before another or not
    We don't read the seconds as we round them to 0 anyway
    :param time: string of the time
    :return: the hour as an int formated as hhmmss
    """
    return int(time[11:13])*(10**4) + int(time[14:16])*(10**2)


def get_time(time):
    """
    Returns the complete date and time as an int formated as follows :
    YYYYMMDDhhmmss, so that we can directly compare the int to check if a datetime
    is before another or not
    :param time: string of the time
    :return: the date and time as an int formated as YYYYMMDDhhmmss
    """
    return get_date(time)*(10**6) + get_hour(time)


def before(t1, t2):
    """
    Test if time t1 is smaller, i.e. before time t2, returns True if yes,
    otherwise False
    :param t1: the first time as a string
    :param t2: the second time as a string
    :return: True if t1 is before t2, False otherwise
    """
    return get_time(t1) < get_time(t2)


def equal(t1, t2):
    """
    Test if time t1 is equat to time t2, returns True if yes,
    otherwise False
    :param t1: the first time as a string
    :param t2: the second time as a string
    :return: True if both arguments indicates the same time
    """
    return get_time(t1) == get_time(t2)


def get_index(df_np, i):
    """
    Returns the value at index i in the column corresponding to the given numpy
    array corresponding to the dataframe
    :param df_np: numpy array representing a column of a pandas dataframe
    :param i: the index we want in this np array
    :return: the value at index i in the array
    """
    if 0 <= i < len(df_np):
        return str(df_np[i])


def get_delta_time(t1, t2):
    """
    Returns the time delta between the 2 times in minutes
    :param t1: the first time as a string
    :param t2: the second time as a string
    :return: the difference between t1 and t2
    """
    start = get_hour(t1)
    s_hour = start // (10**4)
    s_min = (start % (10**4)) // (10**2)
    end = get_hour(t2)
    e_hour = end // (10**4)
    e_min = (end % (10**4)) // (10**2)
    if get_date(t1) == get_date(t2):
        # They are on the same day
        time_delta = (e_hour - (s_hour + 1))*60 + e_min + (60 - s_min)
    else:
        time_delta = e_hour * 60 + e_min + (24 - (s_hour + 1))*60 + (60 - s_min)
    return time_delta


def make_formated_column(dst_df, src_df, col):
    """
    Format the values of the given column col from the src_df dataframe and write
    the results into the corresponding column col in the dst_df dataframe.
    It puts a Nan when the required data in src_df is not present
    :param dst_df: the destination pandas dataframe
    :param src_df: the source pandas dataframe
    :param col: the column in the src dataframe we want to format the values of
    """
    # At the begining, check if there are the required values,
    # while the dst time is before the first src time, we put nan into dst_df
    i = 0
    dst_time_np = dst_df['time'].to_numpy()
    src_time_np = src_df['time'].to_numpy()
    dst_np = dst_df[col].to_numpy()
    src_np = src_df[col].to_numpy()
    while(before(get_index(dst_time_np, i), get_index(src_time_np, 0))
          and i < len(dst_df.index)):
        dst_np[i] = np.nan
        i += 1

    # The index for the src_df array
    s = 0
    reached_end = False

    # Now we reach the first equal or superior time
    len_dst = len(dst_df.index)
    len_src = len(src_df.index)
    while i < len_dst and s < len_src:
        # Seek the last src sample that have a time less or equal to the needed
        # dst_df sample time to fill at index i
        while(not reached_end and
              before(get_index(src_time_np, s), get_index(dst_time_np, i))):
            s += 1
            if s >= len_src:
                reached_end = True

        if s < len_src:
            # Reached the src sample that has a time equal or superior to the dst
            # sample we need to fill
            if equal(get_index(src_time_np, s), get_index(dst_time_np, i)):
                dst_np[i] = src_np[s]
            else:
                # Then it means the src sample at index s is the first after the
                # dst sample we need to fill, so we interpolate between the src
                # sample at index s-1 and the one at index s

                # Time delta in minutes
                start = get_index(src_time_np, s-1)
                duration = get_delta_time(start,
                                          get_index(src_time_np, s))
                y1 = float(get_index(src_np, s-1))
                y2 = float(get_index(src_np, s))

                # Time delta from start to evaluation point
                at_evaluation = get_delta_time(start, get_index(dst_time_np, i))
                dst_np[i] = y1 + (y2 - y1) / duration * at_evaluation

            i += 1

    # If there are still values in the dst_df that we need to fill, but
    # we reached the end of the src_df, then we put Nan values
    while i < len_dst:
        dst_np[i] = np.nan
        i += 1


def format_dataframe(dst_df, src_df, columns):
    """
    Format the given columns in the list columns from the src_df dataframe
    into dst_df dataframe, writing Nan values where
    the corresponding needed value is missing in the src_df. Passed by value of
    a reference to the df so no need to return the result
    :param dst_df: the destination pandas dataframe
    :param src_df: the source pandas dataframe
    :param columns: the columns in the src dataframe we want to format the values of
    """
    for col in columns:
        make_formated_column(dst_df, src_df, col)
