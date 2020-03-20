#!/bin/bash

# Last update : 18.03.2020, Cyrille Pittet

# This script :
#   1) Stop the database influxdb container
#   2) Stop the cron job for transfer.py
#   3) Run 1 time the transfer.py to ensure all data were added to the influxdb


# Stops the cron job
crontab -l 2>/dev/null | grep -v 'python3 transfer.py' | crontab -

# Add remaining data to the db
python3 transfer.py

# Stops the running container
docker-compose stop
