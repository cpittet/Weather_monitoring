#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script :
#   1) Try to send all the folders present in the volume directory.
#      If the data sample directory is correctly sent, we delete it
#   2) If there was an error, then we return code 1 else we return 0 as success

# Loop over the folders and send them
# https://stackoverflow.com/questions/11304895/how-do-i-copy-a-folder-from-remote-to-local-using-scp
# https://stackoverflow.com/questions/5267597/best-way-to-programmatically-check-for-a-failed-scp-in-a-shell-script
for d in ./volume/*/ ;
do
    scp -r $d pi@192.168.1.124:/home/pi/RaspberryProjects/weather_monitoring/Weather_monitoring/data
    if [ $? -eq 0 ];
    then
        # It was successful, so remove data sample directory
        rm -r $d
    else
        # It did not succeed
        echo 1
    fi
done
