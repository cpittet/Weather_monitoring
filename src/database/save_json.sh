#!/bin/bash

# Query all the clean data points, older that the specified date (e.g. 2016-07-31T20:07:00Z) and save it here as clean_dataset.json

echo "Querying the data ..."

influx -host 192.168.1.124 -port 8086 -database db -format json -precision rfc3339 -execute "select * from \"clean_sh_data\"" > clean_dataset.json

echo "The data can be found in clean_dataset.json"
