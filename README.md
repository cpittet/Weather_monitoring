# Weather monitoring (in construction)
![Code Grade](https://www.code-inspector.com/project/6308/status/svg)

Weather station using Raspberry Pi SenseHat sensor to collect data (temperature, humidity, pressure) and analyze / visualize them.

## Context
- 1x Raspberry Pi 3 B+ : runs a python scripts that collects the data every hour. Then the Raspberry sends them to the InfluxDB (db for time series) server on the other Raspberry every hour.

- 1x Raspberry Pi 4 B : runs an InfluxDB docker container which receives the data collected. It also runs a Grafana docker container to visualize those data.

The measured data are not really accurate but it makes a good exercise to clean them.

## Data collection
The data are collected by a Raspberry SenseHat module located under a roof, outside.
A python script is executed every hour (->crontab), collecting the measures. Then few minutes after that, another script sends them to another Rapsberry Pi running a InfluxDB server in a docker container.

## Database and Visualization
An InfluxDB server (db for time series) runs along with a Grafana server in a docker container.

## Data cleaning
The measured data are processed once a day. The cleaning includes :
- detecting impossible measured values (e.g. 0 for pressure, or a too big difference between consecutive points in time). To achieve this, the time series are treated as a signal and simple convolution are applied to them. The finite difference filter is used to determine the difference between consecutive points.
- correct these aberrant values. Here I simply take the average between the neighboring values of the same signal.
- push these corrected data to a dedicated measurement in the InfluxDB database.

All this is done using pandas dataframes, numpy arrays. The scripts for the data cleaning are located in the processing folder.

## Structure of the project
Multiple files are useless at this point, this is in construction.
```
.
│   README.md
│      
│
└───src
│   │   
│   │   (credentials.txt, credentials to connect to the InfluxDB server,
│   │   to configure yourself)
│   │   
│   └───data_collection
│   │   │   collect.py
│   │   │   transfer_db.py
│   │   │   send_data.sh
│   │   │   start_collecting.sh
│   │   │   stop_collecting.sh
│   │
│   │
│   └───database
│   │   │   docker-compose.yml
│   │   │   start_db_server.sh
│   │   │   stop_db_server.sh
│   │   │   (gf_smtp.env, environment variables used for the Grafana docker container,
│   │   │   to configure yourself)
│   │   │   (inflx.env, environment variables used for the InfluxDB docker container,
│   │   │   to configure yourself)
│   │
│   │
│   └───processing
│   │   │   clean.py
│   │   │   fetch_open_data.py
│   │   │   format_OD.py
│   │   │   start_fetching_open_data.sh
│   │   │   stop_fetching_open_data.sh

```

## Sources of meteorological data
Source : MétéoSuisse, Bundesamt für Meteorologie und Klimatologie
Obtained via : https://opendata.swiss/en/dataset/automatische-wetterstationen-aktuelle-messwerte
