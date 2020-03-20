#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Check in the data directory at the root of this project, if there
#      is new data that were received
#   2) If so, it tries to add them to the db. Otherwise do nothing
#   3) If they are successfully added to the db, it removes the data
#      from the data directory. Otherwise it keeps them there


# https://stackoverflow.com/questions/20456666/bash-checking-if-folder-has-contents
if find "./../../data" -mindepth 1 -quit 2>/dev/null | grep -q .;
then
    python3 transfer.py
fi
