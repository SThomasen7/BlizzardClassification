#!/bin/python3
import re
from pathlib import Path
import sys
sys.path.append("../NOHRSC_data")
import preprocess_data as ppd
import math
snowfall_data = ppd.get_all_data_combined('2009')

## A script to parse out the data I care about and store in a CSV,
## filter out data points that do not pass all quality checks.

def read_file(filename):
    data = list() 
    with open(filename, 'r') as fptr:
        for line in fptr:
            accept, info = parse_line(line)
            ## if the data is not valid skip
            if not accept:
                continue
            
            ## store the data
            data.append(info)
    return data
            
## a function that will help me be more accurate in
## parsing fields from the line
def get_subsection(string, i, j):
    return string[i-1:j]

## All of these codes are outlined in the the ISD document:
## here: https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf
def parse_line(line):
    usaf_master_station_catalog_id = get_subsection(line, 5, 10)
    station_ncei_wban_id = get_subsection(line, 11, 15)
    year = int(get_subsection(line, 16, 19))
    month = int(get_subsection(line, 20, 21))

    if month < 10 and month > 4:
        return False, None
    day = int(get_subsection(line, 22, 23))
    hour = int(get_subsection(line, 24, 25))
    minute = int(get_subsection(line, 26, 27))

    ## check if coords are present:
    if get_subsection(line,29,34) == '+99999' or get_subsection(line,35,41) == '+999999':
        return False, None

    latitude = float(get_subsection(line, 29, 34))/1000
    longitude = float(get_subsection(line, 35, 41))/1000

    ## check if there was snowfall in this 24 hour period
    ## 2009-01-01T12:00:00
    snow_accumulation = float(snowfall_data.sel(time=f"{year}-{month}-{day}T{hour}:{minute}:00", 
        lat=latitude, lon=longitude, method='nearest').Data.values)

    if snow_accumulation <= 0 or math.isnan(snow_accumulation) or snow_accumulation == None:
        return False, None

    call_letter_identifier = get_subsection(line, 52, 56)

    ## wind information
    wind_angle = int(get_subsection(line, 61, 63))
    if wind_angle == 999:
        return False, None

    wind_quality = get_subsection(line, 64, 64)
    if wind_quality not in ['0', '1', '4', '5', '9', 'A', 'C', 'I', 'M', 'P', 'R', 'U']:
        return False, None

    wind_obsv_code = get_subsection(line, 65, 65)

    wind_speed = int(get_subsection(line, 66, 69))

    if wind_speed == 9999 or wind_speed != 0 and wind_obsv_code == 9:
        return False, None

    wind_speed = wind_speed / 10

    wind_quality = get_subsection(line, 70, 70)
    if wind_quality not in ['0', '1', '4', '5', '9', 'A', 'C', 'I', 'M', 'P', 'R', 'U']:
        return False, None
    
    visibility_distance = int(get_subsection(line, 79, 84))
    visibility_quality = get_subsection(line, 85, 85)

    if visibility_distance == 999999 or \
            visibility_quality not in ['0', '1', '4', '5', '9', 'A', 'C', 'I', 'M', 'P', 'R', 'U']:
        return False, None

    temp = int(get_subsection(line, 88, 92))
    temp_quality = get_subsection(line, 93, 93)
    if temp == '9999' or \
            temp_quality not in ['0', '1', '4', '5', '9', 'A', 'C', 'I', 'M', 'P', 'R', 'U']:
        return False, None
    temp = temp / 10

    ## get snow info:
    additional_info = line[104:]
    snow_depth = 9999
    snow_condition = 9
    snow_water_equivalent = 999999
    snow_water_equivalent_condition = 9
    if snow_info := re.search(
            r'ADD.*AJ1[0-9]{4}[123456E9][0145AUPIMCR][0-9]{6}[29][123456E9]',
            additional_info):


        info = snow_info[0]
        info = "AJ1"+info.split("AJ1")[-1]
        #print(info)
        snow_depth = int(get_subsection(info, 4, 7))
        snow_condition = int(get_subsection(info, 8, 8))
        snow_water_equivalent = int(get_subsection(info, 10, 15))/10
        snow_water_equvalent_condition = int(get_subsection(info, 16, 16))

    return True, [
            usaf_master_station_catalog_id,
            station_ncei_wban_id,
            year,
            month,
            day,
            hour,
            minute,
            latitude,
            longitude,
            call_letter_identifier,
            wind_angle,
            wind_obsv_code,
            wind_speed,
            visibility_distance,
            temp,
            snow_accumulation,
            snow_depth,
            snow_condition,
            snow_water_equivalent,
            snow_water_equivalent_condition
            ]

def load_data():
    year = 2009

    while year <= 2009:
        outfile = f"processed_{year}.csv"
        with open(outfile, 'w') as fptr:

            ## write headers
            fptr.write(
                "usaf_master_station_catalog_id,station_ncei_wban_id,year,month,day,"
                "hour,minute,latitude,longitude,call_letter_identifier,wind_angle,"
                "wind_obsv_code,wind_speed,visibility_distance,temp,snow_accumulation,snow_depth,"
                "snow_condition,snow_water_equivalent,snow_water_equivalent_condition\n"
            )

            ## for each station file
            for entry in Path(str(year)).glob('**/*'):
                print(f"Processing: {entry}")
                data = read_file(entry)
                
                for entry in data:
                    fptr.write(','.join([str(x) for x in entry])+'\n')


        year += 1

if __name__ == '__main__':
    load_data()
