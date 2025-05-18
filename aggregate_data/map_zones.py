#!/bin/python3
import pandas as pd
import requests
import time
import json
from datetime import datetime

from shapely import Polygon, MultiPolygon, Point

isd_data = pd.read_csv("processed_2009_with_zones.csv")
event_data = pd.read_csv("blizzards_2009.csv")

def make_call_points():
    """Make a mapping to the call letter identifier to the location"""

    cid_map = dict()
    for i, row in isd_data.iterrows():
        cid = row.call_letter_identifier
        lat = row.latitude
        lon = row.longitude

        if cid not in cid_map:
            cid_map[cid] = (lat, lon)

    return cid_map


def map_county_to_polygon():
    endpoint = "https://api.weather.gov/zones/county/"

    ugc_map = dict()
    for i, entry in event_data.iterrows():
        ugcs = str(entry.short_ugcs)

        for ugc in ugcs.split('|'):
            if ugc.split('-')[-1][0] == 'Z':
                continue
            ugc = ugc.replace('-', '')
            if ugc in ugc_map:
                continue

            try:
                response = requests.get(endpoint+ugc)
                geometry = response.json()["geometry"]
                shape = None
                if geometry["type"] == 'Polygon':
                    shape = Polygon(geometry["coordinates"][0])
                else:
                    shape = MultiPolygon(geometry["coordinates"][0])
                
                ugc_map[ugc] = shape
                time.sleep(1)

            except Exception as e:
                print(e)
    return ugc_map

def map_call_to_county(call_points, county_map):

    final_map = dict()

    for call_letter, point in call_points.items():
        for ugc, shape in county_map.items():
            if shape.contains(Point((point[1], point[0]))):
                if call_letter not in final_map:
                    final_map[call_letter] = list()
                final_map[call_letter].append(ugc)
    return final_map



def map_station_to_blizzards(county_mapping):

    county_to_blizzard = dict()
    for i, row in event_data.iterrows():

        key = None
        ugcs = str(row.short_ugcs)

        for ugc in ugcs.split('|'):
            if ugc.split('-')[-1][0] == 'Z':
                continue
            key = ugc.replace('-', '')
        
        if key not in county_to_blizzard:
            county_to_blizzard[key] = list()
        county_to_blizzard[key].append(row)

    #used_blizzards = list()
    call_to_blizzard = dict()
    for call, county in county_mapping.items():
        county = county[0]

        call_to_blizzard[call] = county_to_blizzard[county]

    return call_to_blizzard



def write_out_aggregated(blizzards):

    fptr = open("aggregated.csv", 'w')
    fptr.write("usaf_master_station_catalog_id,station_ncei_wban_id,call_letter_id,"
            "time,latitude,longitude,wind_angle,wind_obsv_code,wind_speed,temp,visibility_distance,"
            "snow_accumulation,snow_depth,snow_condition,snow_water_equivalent,"
            "blizzard_episode_id,blizzard_event_id,has_blizzard\n")

    for i, row in isd_data.iterrows():

        station_time = f"{row.year}-{row.month}-{row.day} {row.hour:02d}{row.minute:02d}"
        station_dt = datetime.strptime(station_time, "%Y-%m-%d %H%M")

        out = ""
        out += str(row.usaf_master_station_catalog_id)
        out += ","+str(row.station_ncei_wban_id)
        out += ","+str(row.call_letter_identifier)
        out += ","+str(station_dt)
        out += ","+str(row.latitude)
        out += ","+str(row.longitude)
        out += ","+str(row.wind_angle)
        out += ","+str(row.wind_obsv_code)
        out += ","+str(row.wind_speed)
        out += ","+str(row.temp)
        out += ","+str(row.visibility_distance)
        out += ","+str(row.snow_accumulation)
        out += ","+str(row.snow_depth)
        out += ","+str(row.snow_condition)
        out += ","+str(row.snow_water_equivalent)

        has_blizzard = False
        if row.call_letter_identifier in blizzards:
            c_blizzards = blizzards[row.call_letter_identifier]
            for blizzard in c_blizzards:
                begin = datetime.strptime(blizzard.begin_time, "%Y-%m-%d %H:%M:%S %Z")
                end = datetime.strptime(blizzard.end_time, "%Y-%m-%d %H:%M %Z")

                if begin <= station_dt and station_dt <= end:
                    out += f",{blizzard.episode_id},{blizzard.event_id},1\n"
                    has_blizzard = True
                    break
        
        if not has_blizzard:
            out += ",0,0,0\n"

        fptr.write(out)

    fptr.close()


