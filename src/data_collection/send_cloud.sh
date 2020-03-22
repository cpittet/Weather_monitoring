#!/bin/bash

# This script add as cron job the task transfer_db_cloud.py
# which sends the collected data to the influxdb server on
# a cloud machine


# write out current crontab
crontab -l > mycron
# echo new cron into cron file
# Add the send_db.sh task to the crontab.
echo "2 * * * * cd /home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/src/data_collection && python3 transfer_db_cloud.py" >> mycron

# install new cron file
crontab mycron
rm mycron

