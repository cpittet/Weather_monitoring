# Weather monitoring (in construction)
Weather station using Raspberry Pi SenseHat sensor to collect data (temperature, humidity, pressure) and analyze / visualize them.

## Context
- 1x Raspberry Pi 3 B+ : runs a docker container which runs a python scripts that collects the data every hour. Then the Raspberry send them to the second Raspberry every 6 hours.

- 1x Raspberry Pi 4 B : runs an InfluxDB docker container which receives the data collected.

## Structure of the project

```
.
│   README.md
│      
│
└───src
    │   
    │   
    │
    └───data_collection
        │   collect.py
        │   docker-compose.yml
        │   Dockerfile
        │   send_data.sh
        │   start_collecting.sh
        │   stop_collecting.sh
```
