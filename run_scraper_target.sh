#!/bin/bash
cd /home/megatime/ScraperPrensa

find App/Results -type f -mtime +2 -name '*.jpg' -execdir rm -- '{}' +
find App/Results -type d -mtime +2 -execdir rm -rf {} +

mkdir -p logs

cp /usr/share/zoneinfo/Etc/GMT+4 /etc/localtime

docker run -v "$(pwd)/App:/App" scraper python main.py $1 > logs/$1_$(date +"%H").log