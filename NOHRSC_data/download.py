#!/bin/python3
from datetime import datetime, timedelta
import os
import random
import time
import subprocess
import re

## thanks to the help of chatgpt for helping me 
## come up with this function
def generate_timestamps(start_str, end_str):
    # Parse the input strings into datetime objects
    start = datetime.strptime(start_str, "%Y%m%d%H")
    end = datetime.strptime(end_str, "%Y%m%d%H")

    current = start
    while current <= end:
        yield current.strftime("%Y%m%d%H")
        current += timedelta(hours=24)

def download_all():
    for timestr in generate_timestamps('2008100112', '2025050912'):
        filename = f"sfav2_CONUS_24h_{timestr}.nc"
        url = f"https://www.nohrsc.noaa.gov/snowfall/data/{timestr[:6]}/{filename}"
        cmd = f"wget {url} -O raw_data/{filename}"
        time_delay = random.randint(5, 20)/10
        #os.system(f"echo {cmd}\necho Sleeping for {time_delay} seconds")
        os.system(cmd)
        time.sleep(time_delay)

    
def redownload_empty():
    empty = subprocess.check_output(
                "find . -maxdepth 2 -type f -name '*.nc' -empty",
                shell=True
            ).decode("utf-8").split('\n')
    for file in empty:
        if not file: continue
        filename = file.split('/')[-1]
        timestr = re.search(r'[0-9]{10}', file)[0]
        url = f"https://www.nohrsc.noaa.gov/snowfall/data/{timestr[:6]}/{filename}"
        cmd = f"wget {url} -O {file}"
        time_delay = random.randint(5, 20)/10
        #print(cmd)
        os.system(cmd)
        time.sleep(time_delay)

        ## download the file

if __name__ == '__main__':
    #download_all()
    redownload_empty()

## warning the following files were missing:
#./data_raw/sfav2_CONUS_24h_2021092712.nc
#./data_raw/sfav2_CONUS_24h_2021092212.nc
#./data_raw/sfav2_CONUS_24h_2021091712.nc
#./data_raw/sfav2_CONUS_24h_2021091512.nc
#./data_raw/sfav2_CONUS_24h_2021092012.nc
#./data_raw/sfav2_CONUS_24h_2021092412.nc
#./data_raw/sfav2_CONUS_24h_2021091912.nc
#./data_raw/sfav2_CONUS_24h_2021091812.nc
#./data_raw/sfav2_CONUS_24h_2021092612.nc
#./data_raw/sfav2_CONUS_24h_2021091612.nc
#./data_raw/sfav2_CONUS_24h_2021092912.nc
#./data_raw/sfav2_CONUS_24h_2021092112.nc
#./data_raw/sfav2_CONUS_24h_2021092312.nc
#./data_raw/sfav2_CONUS_24h_2021092812.nc
#./data_raw/sfav2_CONUS_24h_2021092512.nc
