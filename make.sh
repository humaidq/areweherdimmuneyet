#!/bin/sh
python main.py gen
minify index.html > public/index.html
minify chart.svg > public/chart.svg
scp -P 2202 public/* root@duisk:/var/www/herd/
