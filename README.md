# Weather monitoring (in construction, code need to be refactored)
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
│   │   │   transfer_db.py
│   │   │   send_data.sh
│   │   │   start_collecting.sh
│   │   │   stop_collecting.sh
│   │
│   │
│   │
│   └───database
│   │   │   docker-compose.yml
│   │   │   start_db_server.sh
│   │   │   stop_db_server.sh
│   │   │   
│   │   │
│   │   └───influxdb
│   │
│   │
│   └───processing
│   │   │   clean.py
│   │   │   fetch_open_data.py
│   │   │   start_fetching_open_data.sh
│   │   │   stop_fetching_open_data.sh
│   │   │   

```

## Sources of meteorological data
Source : MétéoSuisse, Bundesamt für Meteorologie und Klimatologie
Obtained via : https://opendata.swiss/en/dataset/automatische-wetterstationen-aktuelle-messwerte
