#!/bin/bash

# Last update : 18.03.2020, Cyrille Pittet

# This script :
#   1) Start the database influxdb container

# Creates the directory for back up if not yet present
mkdir -p backup_db

# Starts the container
docker-compose up -d
