#!/bin/bash

# Last update : 18.03.2020, Cyrille Pittet

# This script :
#   1) Start the database influxdb container

# Creates the directory for volumes if not yet present
mkdir -p grafana-volume
mkdir -p influxdb-data-volume

# Starts the container
docker-compose up -d
