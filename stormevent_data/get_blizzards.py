#!/bin/python3
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

state_map = \
{
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY",
    "DISTRICT OF COLUMBIA": "DC",
    "AMERICAN SAMOA": "AS",
    "GUAM": "GU",
    "NORTHERN MARIANA ISLANDS": "MP",
    "PUERTO RICO": "PR",
    "UNITED STATES MINOR OUTLYING ISLANDS": "UM",
    "VIRGIN ISLANDS, U.S.": "VI",
}

ugc_data = pd.read_csv("ugc_areas.csv")

def get_data():
    stmt = f"""
        select 
            year,
            begin_yearmonth,
            begin_day,
            begin_time,
            end_yearmonth,
            end_day,
            end_time,
            episode_id,
            event_id,
            state,
            cz_name,
            cz_timezone,
            event_type
        from stormevent_details
        where
            event_type = 'Blizzard'
            and year = '2009'
            and state != 'ALASKA'
    """
    data = cursor.execute(stmt)

    with open("blizzards_2009.csv", 'w') as fptr:
        fptr.write("year,begin_time,end_time,episode_id,event_id,"
                   "state_text,zone,event_type,short_ugcs\n")

        for entry in data:
            year, begin_yearmonth, begin_day, begin_time, end_yearmonth, \
            end_day, end_time, episode_id, event_id, state, cz_name, \
            cz_timezone, event_type = entry

            state = state_map[state]
            tmp = ugc_data[ugc_data.state == state]
            tmp = tmp[tmp.name == cz_name]
            regions = list(tmp.short_ugc)
            
            print(f"{year}-{str(begin_yearmonth)[-2:]}-{begin_day} {begin_time:04d}")
            local_dt = datetime.strptime(
                f"{year}-{str(begin_yearmonth)[-2:]}-{begin_day} {begin_time:04d}",
                "%Y-%m-%d %H%M").replace(tzinfo=\
                        timezone(timedelta(hours=int(cz_timezone.split('-')[-1]))))
            # Convert to UTC
            utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
            print(utc_dt)
            print("***")
            begin_time = utc_dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            local_dt = datetime.strptime(
                    f"{year}-{str(end_yearmonth)[-2:]}-{end_day} {end_time:04d}",
                "%Y-%m-%d %H%M").replace(tzinfo=\
                        timezone(timedelta(hours=int(cz_timezone.split('-')[-1]))))
            # Convert to UTC
            utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
            end_time = utc_dt.strftime("%Y-%m-%d %H:%M %Z")
            
            fptr.write(f"{year},{begin_time},{end_time},{episode_id},{event_id}"
                       f",{state},\"{cz_name}\",{event_type},{'|'.join(regions)}\n")

if __name__ == '__main__':
    get_data()
