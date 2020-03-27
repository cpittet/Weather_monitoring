# Weather monitoring (in construction)
Weather station using Raspberry Pi SenseHat sensor to collect data (temperature, humidity, pressure) and analyze / visualize them.

## Context
- 1x Raspberry Pi 3 B+ : runs a python scripts that collects the data every hour. Then the Raspberry send them to the InfluxDB server on the other Raspberry every 6 hours.

- 1x Raspberry Pi 4 B : runs an InfluxDB docker container which receives the data collected. It also runs a Grafana docker container to visualize those data.

## Structure of the project
Multiple files are useless at this point, this is in construction.
```
.
│   README.md
│      
│
└───src
│   │   
│   │   
│   │
│   └───data_collection
│   │   │   collect.py
│   │   │   trasnfer_db.py
│   │   │   docker-compose.yml
│   │   │   Dockerfile
│   │   │   send_data.sh
│   │   │   send_db.sh
│   │   │   start_collecting.sh
│   │   │   stop_collecting.sh
│   │   │   build_docker_image.sh
│   │
│   │
│   │
│   └───database
│   │   │   check_new_data.sh
│   │   │   docker-compose.yml
│   │   │   Dockerfile
│   │   │   influx_init.iql
│   │   │   start_db_server.sh
│   │   │   stop_db_server.sh
│   │   │   
│   │   │
│   │   └───influxdb
│   │
│   │
│   └───processing
│   │   │   clean.py
│   │   │   
│   │   │   
│   │   │   
│   │   │   
│   │   │   
│
└───data
```

## Sources of meteorological data
Source : MétéoSuisse, Bundesamt für Meteorologie und Klimatologie
Obtained via : https://opendata.swiss/en/dataset/automatische-wetterstationen-aktuelle-messwerte
