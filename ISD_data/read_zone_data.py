#!/bin/python3
import geopandas as gpd
import xarray as xr
from shapely.geometry import Point
from multiprocessing import Pool
import json
import random

gd = gpd.read_file("../forecast_zones/z_18mr25.shp")

station_hash = dict()
def add_zone_data():
    ## ouptut file
    out_fptr = open("processed_2009_with_zones.csv", 'w')

    with open("processed_2009.csv", 'r') as fptr:
        for i, line in enumerate(fptr):
            line = line.strip()
            ## write the headers
            if i == 0:
                out_fptr.write(line+',state,zone\n')
                continue
            
            ## otherwise get the zone
            lat, lon = line.split(',')[7:9]
            station = line.split(',')[9]

            ## hash the location
            if station != '99999' and station in station_hash:
                zone_str = station_hash[station]
            else:
                zone_str = zones_contain_point((float(lon), float(lat)))
                if station != '99999':
                    station_hash[station] = zone_str

            out_fptr.write(line+','+zone_str+'\n')

    out_fptr.close()
    ## write out the stations
    station_data = list()
    for key, val in station_hash.items():
        station_data.append(val+","+key+"\n")

    with open("stations.csv", 'w') as fptr:
        fptr.write("STATE,ZONE,STATION_CALL_ID\n")
        for line in sorted(station_data):
            fptr.write(line+'\n')

def zones_contain_point(point):
    point = Point(point)
    zones = list()
    
    for index, row in gd.iterrows():
        zone_name = f"{row['STATE']},'{row['NAME']}'"
        if row.geometry.contains(point):
            return zone_name

    return "STATE_NOT_FOUND,'ZONE_NOT_FOUND'"

if __name__ == '__main__':
    add_zone_data()
