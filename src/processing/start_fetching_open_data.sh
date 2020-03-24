#!/bin/bash

# This script :
#   1) Set a cron job for fetching open data

# write out current crontab
crontab -l > mycron
# echo new cron into cron file
echo "30 */6 * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/processing && python3 fetch_open_data.py" >> mycron

# install new cron file
crontab mycron
rm mycron
