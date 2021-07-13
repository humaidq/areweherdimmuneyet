#!/bin/sh
wget \
	https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/United%20Arab%20Emirates.csv \
	-O data.csv


python3 main.py
minify index.html > public/index.html
minify chart.svg > public/chart.svg
scp -P 2202 public/* root@duisk:/var/www/herd/
