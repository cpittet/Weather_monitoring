#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script : stop the cron job of the task transfering data to the 
# influxdb server running on the cloud machine


# Stops the cron jobs
crontab -l 2>/dev/null | grep -v 'python3 transfer_db_cloud.py' | crontab -

