#!/bin/python3
import pandas as pd
import editdistance
import operator
import sys
import json

def map_blizzards_to_zones():
    """Attempt blizzard zones to ISD zones, so we can map points"""

    ## Create a state map from the ISD stations
    zone_map = dict()
    stations = pd.read_csv("stations.csv")

    for i, station in stations.iterrows():
        if station.STATE not in zone_map:
            zone_map[station.STATE] = set()
        zone_map[station.STATE].add(station.ZONE.strip("'"))

    zone_map2 = dict()
    for key, val in zone_map.items():
        zone_map2[key] = sorted(list(val))

    with open("zone_map.json", 'w') as fptr:
        json.dump(zone_map2, fptr, indent=4)
    ## now that we have the ISD zones, attempt to match them all 
    ## to the storm event database.
    blizz_map = dict()
    blizzards = pd.read_csv("blizzards_2009.csv")

    for i, row in blizzards.iterrows():
        matched = match_storm_to_zone(zone_map, row)
        print(i)



def match_storm_to_zone(zone_map, storm):

    manual_map = {
        "NE|DIXON": ("NE", "Wayne"),
        "NE|DAKOTA": ("IA", "Sioux"),
        "SD|MOODY": ("SD", "Brookings"),
        "SD|UNION": ("IA", "Sioux"),
        "MN|LINCOLN": ("MN", "Wadena"),
        "SD|SANBORN": ("SD", "Davison"),
        "SD|GREGORY": ("SD", "Tripp"),
        "SD|CHARLES MIX": ("SD", "Davison"),
        "SD|LINCOLN": ("SD", "Minnehaha"),
        "SD|DOUGLAS": ("SD", "Davison"),
        "SD|KINGSBURY": ("SD", "Beadle"),
        "SD|MINER": ("SD", "Davison"),
        "SD|JERAULD": ("SD", "Beadle"),
        "SD|HANSON": ("SD", "Davison"),
        "SD|MCCOOK": ("SD", "Davison"),
        "SD|HUTCHINSON": ("SD", "Davison"),
        "SD|AURORA": ("SD", "Brookings"),
        "NM|SOUTHWEST CHAVES COUNTY": ("NM", "Chaves County Plains"),
    }

    key = f"{storm.state_text}|{storm.zone}"
    if key in manual_map:
        return manual_map[key]

    zones = zone_map[storm.state_text]

    if storm.zone.title() in zones:
        return storm.zone.title()

    if (key in ("SD|CLAY", "SD|BRULE", "NM|EASTERN LINCOLN COUNTY")):
        return 'FAIL'
    
    print(storm)
    return find_closest_matches(5, storm.zone.title(), zones)


def find_closest_matches(n, name, zones):
    matches = list()
    for zone in list(zones):
        matches.append((zone, editdistance.eval(name, zone)))

    print("**********")
    print(name)
    print("**********")
    matches = sorted(matches, key=operator.itemgetter(1), reverse=False)
    for x in sorted(matches):
        print(x)
    sys.exit(1)
    return matches[:n]

if __name__ == '__main__':
    map_blizzards_to_zones()


