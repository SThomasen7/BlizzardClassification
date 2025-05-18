#!/bin/bash

# index.html is the contents of url
#url=https://www.ncei.noaa.gov/pub/data/noaa/

# there is data ranging from 1901 to 2025
#for i in {1901..1901}; do
  #echo $url$i/
  #curl $url$i/ > temp.html
  #files=$(grep -Eo '\b[A-Za-z0-9._-]*.gz\b' temp.html | sort -u)
#
  #mkdir -p data/$i
  #for file in $files; do
    #wget $url$i/$file -O data/$i/$file
    #gunzip data/$i/$file
  #done
#done

wget -N -r -e robots=off --accept-regex='/202[2-5]/' --no-parent --force-html -A.gz https://www.ncei.noaa.gov/pub/data/noaa/
