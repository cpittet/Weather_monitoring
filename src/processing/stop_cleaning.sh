#!/bin/bash

# This script :
#   1) Stops the cron job that executes the task clean.py


# Stops the cron job
crontab -l 2>/dev/null | grep -v 'python3 clean.py' | crontab -
