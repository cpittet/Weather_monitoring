#!/bin/bash

# Last update : 19.03.2020, Cyrille Pittet

# This script build the docker image for the Dockerfile in that directory

docker build -t "data_collector:Dockerfile" .
