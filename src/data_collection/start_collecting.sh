#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Create (if not here) a directory 'volume' used to store the data
#      temporarily

# Creates the volume directory of the host if it does not exist
mkdir -p volume

# Check if the directory volume is empty or not.
# If not, send the data to the other Raspi.
# src : https://stackoverflow.com/questions/20456666/bash-checking-if-folder-has-contents
if find "./volume" -mindepth 1 -quit 2>/dev/null | grep -q .; then
    # Not empty, so we send all data remaining
    ./send_data.sh

    # If send_data.sh returns 0, then the data were well sent,
    # so we can delete them. If 1 is returned, then an error occured,
    # so we keep them
    if [ $? -eq 0 ];
    then
        # Clear the volume folder
        rm -r ./volume/*
    fi
fi

# Starts the container
# docker-compose up -d

# Executes the python script inside the container that collects the data
#docker-compose exec -d data_collector python3 name.py

# Execute the bash script on the host, which sends the new data to the other Raspi
#./send_data.sh


# Data are collected every hour at 00 min
# they are sent every 6 hours (so 6 data samples), on the 30 min :
# at 0030, 0630, 1230, 1830. See crontab guru for format

# Add the collect.py task to the crontab
cmd1="00 * * * * cd ~/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && python3 collect.py"
(crontab -l 2>/dev/null; echo $cmd1) | crontab -


# Add the send_data.sh task to the crontab.
cmd2="30 */6  * * * cd ~/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && ./send_data.sh"
(crontab -l 2>/dev/null; echo $cmd2) | crontab -
