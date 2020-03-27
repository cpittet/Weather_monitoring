#!/bin/bash

# This script :
#   1) Stops the cron job for fetching open data

# Stops the cron jobs
crontab -l 2>/dev/null | grep -v 'python3 fetch_open_data.py' | crontab -
