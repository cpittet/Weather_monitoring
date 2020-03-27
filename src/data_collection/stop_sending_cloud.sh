#!/bin/bash

# This script :
#   1) Stop the cron job that send the data in the cloud

# Stops the cron job
crontab -l 2>/dev/null | grep -v 'python3 transfer_db_cloud.py' | crontab -
