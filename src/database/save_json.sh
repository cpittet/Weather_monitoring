influx -host 192.168.1.124 -port 8086 -database db -format json -precision rfc3339 -execute "select * from \"clean_sh_data\"" > clean_dataset.json
