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
import format_OD

# ------------------------------------------------------------------------------
# Constants
TMP = 'temperature'
TMP_H = 'temperature_humidity'
TMP_P = 'temperature_pressure'
HUM = 'humidity'
PRES = 'pressure'

THRESHOLDS = {TMP: 5, HUM: 7, PRES: 1,
              TMP_H: 5,
              TMP_P: 5}

CREDENTIALS_FILE = '../credentials.txt'
# =================================================================
# Read the credentials in the file, omit the last char that is '\n'
# when using readline
with open(CREDENTIALS_FILE, 'r') as f:
    IP_RP4 = f.readline()[:-1]
    PORT = f.readline()[:-1]
    USER_NAME = f.readline()[:-1]
    PWD = f.readline()[:-1]
    DB_NAME = f.readline()[:-1]

# =================================================================

FORMATED_COLS = [TMP, HUM]
ADJUSTED_COLS = [TMP, HUM,
                 TMP_H, TMP_P]
CONVOL_COLS = [TMP, HUM, PRES,
               TMP_H, TMP_P]


# ------------------------------------------------------------------------------
# Functions


def query_to_points(query, client):
    """
    Query the db and returns the generator of the points
    Note that the time is in UTC
    :param query: string of the query to execute
    :param client: the influxdb client to query to
    :return: the result as a generator of points
    """
    try:
        results = client.query(query)
    except:
        client.close()
        return
    return results.get_points()


def query_convolution(client, from_time):
    """
    Query the db for the convolution signal, from the specified sample
    :param client: the influxdb client to query to
    :param from_time: string of the time we want to query data from
    :return: the result as a generator of points
    """
    query = ('SELECT * FROM "db"."autogen"."convol_signals" '
             + 'WHERE time >= \'' + from_time + '\'')
    return query_to_points(query, client)


def query_last_raw_values(last_cleaned_time, client):
    """
    Query the last values that were convolved (the actual values, not the last
    values of the convolutions).
    :param last_cleaned_time: int, the time of the last data that was cleaned
    :param client: the influxdb client to query to
    :return: If last_cleaned_time == 0, return None,
             otherwise return a Dataframe containing only the whole last row
    """
    if last_cleaned_time == '0':
        return None
    else:
        return pd.DataFrame(query_to_points(
            ('SELECT * FROM "db"."autogen"."data" '
             + 'WHERE "source" = \'sensehat\' AND time = \''
             + str(last_cleaned_time) + '\''),
            client))


def check_clean_measurement(client):
    """
    Check if the measurement 'clean_data' exists in the influxdb server
    in database 'db'. If not, then no data have been cleaned yet and
    return False, otherwise, some data have been cleaned and return True
    :param client: the influxdb client to query to
    :return: True if some data have already been cleaned, False otherwise
    """
    meas = client.get_list_measurements()
    for m in meas:
        if m.get('name') == 'convol_signals':
            return True

    # The clean_data measurement was not found,
    # so no data have been cleaned yet
    return False


def query_data_to_clean(client, source, last_cleaned='0', update_last_cleaned=True, fields='*'):
    """
    Make the right query according to the data that were already cleaned or not
    and the given source tag value. Can pass directly the timestamp of last
    cleaned data (if you have it) to avoid seeking it again. When giving
    a fields argument you should put i in double quotes (e.g. '"temperature"')
    :param client: the influxdb client to query to
    :param source: the tag source in the influxdb, i.e. either 'sense_hat' or 'meteosuisse'
    :param last_cleaned: int, the time of the last data that was cleaned
    :param update_last_cleaned: boolean : True if you want to seek the time of the last cleaned data
    :param fields: the fields we want to fetch
    :return: (timestamp of last cleaned sample, string of the query)
    """
    if check_clean_measurement(client) and not (last_cleaned == '0' and not update_last_cleaned):
        # Measurement already exists
        if update_last_cleaned:
            # Query what was the last cleaned data point
            query = 'SELECT LAST("temperature") FROM "db"."autogen"."convol_signals"'
            points = query_to_points(query, client)

            # Get the timestamp of the last cleaned sample, not nice ...
            for point in points:
                last_cleaned = point['time']

        # Query from the last_cleaned data, autogen is the retention policy
        query = ('SELECT ' + fields + ' FROM "db"."autogen"."data" WHERE "source" = \''
                 + source + '\' AND time > \'' + str(last_cleaned) + '\'')
        return last_cleaned, query
    else:
        # No data were cleaned yet, so we query all points in data
        return ('0',
                ('SELECT ' + fields + ' FROM "db"."autogen"."data" WHERE "source" = \''
                  + source + '\''))


def convolve_dataframe(src_df, dst_df, previous_row, filter=[0, 1, -1]):
    """
    Convolve the entire dataframe (columns by columns) with given filter
    and store the convolved signals into the given dest_df, keeping
    the same columns names. It also sets the 1st element of each column to 0
    as the convolution is just the identity for the 1st element
    with the default filter. Default filter is the finite differences filter,
    i.e. approximation of the derivative. previous_row is a Dataframe
    containing the last values (the whole last row) that were convolved
    (i.e. the temperature, etc, not the value of the convolution itself).
    This is to avoid a gap in the convolution between 2 calls
    :param dst_df: the destination pandas dataframe
    :param src_df: the source pandas dataframe
    :param previous_row: the measurement values of the last convolved data (see above)
    :param filter: the filter to use for the convolution
    """
    if len(src_df.index) >= 3:
        df_np = src_df[CONVOL_COLS].to_numpy()

        # Convolve all the columns except 'time' along their axis (axis 0)
        lambd = lambda col: np.convolve(col, filter, 'same')
        convol_np = np.apply_along_axis(lambd, axis=0, arr=df_np)

        if previous_row is None:
            convol_np[0, :] = 0
        else:
            # Set the first values of each columns in the convolutions to the
            # difference with the actual first value - actual last treated value
            # to avoid gap in the convolutions signals between 2 different calls
            convol_np[0, :] = df_np[0, :] - previous_row[CONVOL_COLS].to_numpy()[0]

        # Again, not yet found a way to set multiple columns at once
        # with multi-dimensional np array
        for i in range(len(CONVOL_COLS)):
            dst_df[CONVOL_COLS[i]] = convol_np[:, i]


def clean_column(dataframe, dataframe_convol, col, previous_row,
                 mode='average'):
    """
    Clean the given column with the specified rules below (see function clean_data)
    The mode specify the techniques used to correct values : average or copy
    previous_row is the same as for convolve_dataframe
    :param dataframe: the pandas dataframe containing the measurements values
    :param dataframe_convol: the pandas dataframe containing the convolutions values
    :param col: the column we want to clean in dataframe
    :param previous_row: the measurement values of the last convolved data (see above)
    :param mode: string, either 'average' to take the average between neighbors
                 to fill a missing value, or 'copy' to copy the value from
                 another measurement
    """
    values = dataframe[col].to_numpy()
    convol = dataframe_convol[col].to_numpy()

    # Detect the indexes where the corresponding threshold is exceeded
    anormal_index = np.argwhere(np.absolute(convol) > THRESHOLDS[col])

    if mode == 'average':
        for i in anormal_index:
            if 0 < i < values.shape[0] - 1:
                # I.e. there exist previous and next values
                values[i] = (values[i - 1] + values[i + 1]) / 2.0
            elif i > 0:
                # I.e. there is no next value, or we don't have it yet
                values[i] = values[i - 1]
            else:
                if previous_row is None:
                    # I.e. there is no previous value
                    values[i] = values[i + 1]
                else:
                    values[i] = (previous_row[col].to_numpy()[0] + values[i + 1]) / 2.0
    else:
        # I.e. copy method, only for temperature
        values[anormal_index] = dataframe[TMP_H].to_numpy()[anormal_index]
    dataframe[col] = values


def clean_data(dataframe, dataframe_convol, previous_row):
    """
    Correct the anormal values spotted by the convolution signal
    Correct (in order):
      1) Humidity : average of previous and next values (if existent)
      2) Pressure : average of previous and next values (if existent)
      3) Temperature_humidity : average of previous and next values (if existent)
      4) Temperature_pressure : average of previous and next values (if existent)
      5) Temperature : same value as the temperature_humidity,
                       because they seem very close. In worst case,
                       it takes the corrected value of temperature_humidity
    It takes the dataframe to clean and the dataframe of the convolution in args
    :param dataframe: the pandas dataframe containing the measurements values
    :param dataframe_convol: the pandas dataframe containing the convolutions values
    :param previous_row: the measurement values of the last convolved data (see above)
    """
    columns = [HUM, PRES,
               TMP_H, TMP_P, TMP]
    for col in columns:
        if col == TMP:
            clean_column(dataframe, dataframe_convol, col, previous_row, mode='copy')
        else:
            clean_column(dataframe, dataframe_convol, col, previous_row, mode='average')


def prepare_ms_df(src_df, time_column):
    """
    Make the meteo suisse dataframe dst_df containing the interpolated data for
    every hour using the module format_OD from the given src_df "raw" meteo
    suisse dataframe. The hours corresponds to the given 'time' column.
    :param src_df:
    :param time_column:
    :return: the formated dataframe dst_df
    """
    if len(src_df.index) == 0:
        return None

    # Add the needed columns to the newly created dst_df dataframe:
    # with the correct size : 'time', TMP, HUM
    dst_df = pd.DataFrame();
    dst_df['time'] = pd.to_datetime(time_column)
    len_dst = len(dst_df.index)
    dst_df[TMP] = np.empty(len_dst)
    dst_df[HUM] = np.empty(len_dst)

    # Format the dataframe
    format_OD.format_dataframe(dst_df, src_df, FORMATED_COLS)
    return dst_df


def avg_diff_df(form_ms_df, sensehat_clean_df):
    """
    Compute the average differences between the values in the sensehat_clean_df
    dataframe and the corresponding one in the form_ms_df formated meteo suisse
    data dataframe. It does not take into account the values for which there
    is a Nan in either dataframe. It is supposed that both columns have
    the same indexing and values at same index correspond to the same time
    :param form_ms_df:
    :param sensehat_clean_df:
    :return: dict : {'temperature' : avg_diff_temp,
             HUM : avg_diff_humidity}
    """
    avg_diffs = {TMP: 0, HUM: 0}

    # Careful with the order of the columns
    ms_matrix = form_ms_df[FORMATED_COLS].to_numpy()
    sh_matrix = sensehat_clean_df[FORMATED_COLS].to_numpy()

    # Directly do the difference by columns
    means = np.nanmean((sh_matrix - ms_matrix), axis=0)

    # Careful with the order of the columns
    avg_diffs[TMP] = means[0]
    avg_diffs[HUM] = means[1]
    avg_diffs[TMP_H] = avg_diffs[TMP]
    avg_diffs[TMP_P] = avg_diffs[TMP]
    return avg_diffs


def adjust_df(dst_df, adjustements):
    """
    Adjust the whole dataframe dst_df according to the adjustements dict,
    which specify the adjustement to do for each column in the formated df
    :param dst_df: the pandas dataframe to write to
    :param adjustements: dict : the adjustements to make
    """
    dst_np = dst_df[ADJUSTED_COLS].to_numpy()

    # Careful to put the columns in the same order
    adjust_np = np.array([adjustements[TMP], adjustements[HUM],
                          adjustements[TMP_H],
                          adjustements[TMP_P]])
    result_np = dst_np - adjust_np

    # Not yet found a way to set all the columns at once with a multi-dimensional
    # numpy array...
    for i in range(4):
        # Select the ith column in result_np
        dst_df[ADJUSTED_COLS[i]] = result_np[:, i]


def write_df(df_to_write, measurement, df_client):
    """
    Write the given dataframe to the measurement on the database corresponding to
    the influxdb client
    :param df_to_write: the pandas dataframe to write to the influxdb server
    :param measurement: string, the measurement to write the dataframe
                        into in the influxdb
    :param df_client: the influxdb client for writing directly from pandas dataframe
    """
    if len(df_to_write.index) > 0:
        df_client.write_points(df_to_write, measurement)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Script
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def main():
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
    if len(df.index) <= 0:
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
    previous_row = query_last_raw_values(last_cleaned_time, client)

    convolve_dataframe(df, dst_df=df_convol, previous_row=previous_row)

    # Connect to DB with a DataFrameClient
    df_client = DataFrameClient(host=IP_RP4,
                                port=PORT,
                                username=USER_NAME,
                                password=PWD,
                                database=DB_NAME,
                                timeout=10)

    # Write the convolved signals to the influxdb server
    write_df(df_convol, 'convol_signals', df_client)

    # ------------------------------------------------------------------------------
    # Correct the anormal values

    # The result dataframe is now the original df
    # !!! Normally, elements at the same index in dataframe df and df_convol
    # correspond to the same timestamp (as this script is exectued in its
    # completeness via a cron job, so both index the same time range). However,
    # if e.g. only the convolution is done and later the cleaning, then they won't
    # have the same indexing. To avoid this, we query again the db for the correct
    # time range, so we don't have problems with indexing
    from_time = df['time'].to_numpy()[0]
    df_convol = pd.DataFrame(query_convolution(client, from_time))

    # Clean the data
    clean_data(df, df_convol, previous_row)
    # Now the dataframe df is clean

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

    # Format the meteo suisse data dataframe
    form_df = prepare_ms_df(df_ms, df['time'])
    if form_df is not None:
        # Get the average differences for each columns
        # (i.e. sensehat data - meteo suisse data)
        avg_diffs = avg_diff_df(form_df, df)

        # Adjust the clean sensehat dataframe "df" with the average differences
        # for each column (in place)
        adjust_df(df, avg_diffs)

        # Now "df" is the sensehat data, cleaned and adjusted
        # Write the result to the measurement "clean_sh_data"
        # (just have to set the index to the time column to be able to write
        # directly to the influxdb database)
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        write_df(df, 'clean_sh_data', df_client)

    # Close the connections to the influxdb server
    df_client.close()
    client.close()


if __name__ == '__main__':
    main()