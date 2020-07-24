#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Create (if not here) a directory 'volume' used to store the data
#      temporarily

# Creates the volume directory of the host if it does not exist
mkdir -p volume

# Data are collected every half hour at **00 and **30
# They are sent every hour to the db at **05

# Add the collect.py task to the crontab

# https://stackoverflow.com/questions/878600/how-to-create-a-cron-job-using-bash-automatically-without-the-interactive-editor
# write out current crontab
crontab -l > mycron
# echo new cron into cron file
echo "*/30 * * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && python3 collect.py" >> mycron

# Add the send_db.sh task to the crontab.
echo "5, 35 * * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && python3 transfer_db.py" >> mycron

# install new cron file
crontab mycron
rm mycron
