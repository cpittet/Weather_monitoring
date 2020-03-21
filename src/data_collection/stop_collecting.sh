#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Stops the cron jobs on the hosts (see start_collection.sh 3) and 4)),
#      so there won't be data collection anymore.
#   //2) Stops the running container without removing it nor removing the volume


# Stops the cron jobs
crontab -l 2>/dev/null | grep -v 'python3 collect.py' | crontab -
crontab -l 2>/dev/null | grep -v './send_db.sh' | crontab -

# Stops the running container
# docker-compose stop
