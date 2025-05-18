#!/bin/bash

# index.html is the contents of url
url=https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/

## get all of the unique file names
files=$(grep -Eo '\b[A-Za-z0-9._-]*.csv.gz\b' index.html | sort -u)

for file in $files; do
  wget $url$file -O data/$file
  gunzip data/$file
done

