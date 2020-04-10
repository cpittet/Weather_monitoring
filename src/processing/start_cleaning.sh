#!/bin/bash

# This script :
#   1) Sets a cron job to execute the task clean.py everyday at 0030,
#      which clean and adjust the raw data

# write out current crontab
crontab -l > mycron
# echo new cron into cron file
echo "30 23 * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/processing && python3 clean.py" >> mycron

# install new cron file
crontab mycron
rm mycron
