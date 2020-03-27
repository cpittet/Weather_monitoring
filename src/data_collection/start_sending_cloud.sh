#!/bin/bash

# This script :
#   1) Set a cron job that sends the raw data to a machine in the cloud

# write out current crontab
crontab -l > mycron
# echo new cron into cron file
echo "2 * * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && python3 transfer_db_cloud.py" >> mycron

# install new cron file
crontab mycron
rm mycron
