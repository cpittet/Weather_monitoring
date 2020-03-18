#!/bin/bash

# Last update : 18.03.2020, Cyrille Pittet

# This script :
#   1) Start the database influxdb container
#   2) Set a cron job for the task transfer.py, in order to
#      collect received data and add them to the influxdb

# Starts the container
docker-compose up -d

# Add the transfer.py task to the crontab
cmd1="45 */6 * * * cd ~/RaspberryProjects/weather_monitoring/Weather_monitoring/src/database && python3 transfer.py"
(crontab -l 2>/dev/null; echo $cmd1) | crontab -
