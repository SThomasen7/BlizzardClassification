#!/bin/python3
"""
Make sample the non snowfall data and use the blizzard
data to make a train-test-split sampled dataset.
"""

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random


def load_data():
    data = pd.read_csv("data/aggregated_fix.csv")
    
    blizzard_data = data[data.has_blizzard == 1]
    snow_data = data[data.has_blizzard == 0]

    return blizzard_data, snow_data

def group_blizzard_data(blizzard):
    """I want to treat each event as a separate entity, grouped by station and event_id"""
    events = list(set(blizzard.blizzard_event_id))
    stations = list(set(blizzard.call_letter_id))
    ## there are 279 events
    ## and 200 stations

    ## I'm going to identify the blizzards as event, station tuples
    out = dict()
    for event in events:
        for station in stations:
            key = f"{station}|{event}"

            blizzard_data = blizzard[blizzard.call_letter_id == station]
            blizzard_data = blizzard_data[blizzard_data.blizzard_event_id == event]

            if len(blizzard_data) > 0:
                out[key] = blizzard_data

    ## there are 300 blizzards
    return out
            
def get_length_distribution(blizzards):
    """
    Get the duration of each blizzard and then check the that 
    there are no large gaps in the data, let's say greater than 3 hours
    """
    all_deltas = list()
    discard = list()
    ## sanity check that there are no big gaps in data
    max_deltas = list()
    for key in blizzards.keys():
        #print(key)
        max_delta = 0
        if len(blizzards[key]) < 2:
            discard.append(key)
            continue
        prev = None
        for i, row in blizzards[key].sort_values('time').iterrows():
            if prev is None:
                prev = row.time
                continue
            delta = make_datetime(row.time) - make_datetime(prev)
            delta_hours = delta.total_seconds() / 3600
            max_delta = max(max_delta, delta_hours)
            #if delta_hours > 12.0:
                #print(f"!!! Exceeded time difference: {key}")
            prev = row.time


        total_delta = make_datetime(max(blizzards[key].time))-\
                        make_datetime(min(blizzards[key].time))
        total_delta = total_delta.total_seconds()/3600
        if(total_delta < 2):
            discard.append(key)
            continue
        all_deltas.append(total_delta)
        max_deltas.append(max_delta)
    return all_deltas, discard

def make_datetime(timestr):
    return datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')

def get_distr(blizzards):
    all_deltas, discard = get_length_distribution(blizzards)
    #plt.hist(all_deltas)

    #plt.xlabel("time")
    #plt.ylabel("frequency")
    #plt.title("Histogram of blizzard lengths")
    out = dict()
    for key in blizzards:
        if key in discard:
            continue
        out[key] = blizzards[key]
    #plt.show()
    return all_deltas, out

def sample_non_blizzard(blizzard, snow):
    deltas, blizzard = get_distr(blizzard)
    call_letter_ids = list(set(snow.call_letter_id))

    random.shuffle(call_letter_ids)

    snow_data = dict()
    ## keep sampling until we have as many snow events as blizzards
    station_id = 0
    while len(snow_data) < len(blizzard):
        station = call_letter_ids[station_id]
        station_id += 1
        station_data = snow[snow.call_letter_id == station].sort_values('time')

        if len(station_data) < 300:
            continue

        start_idx = random.randint(0, len(station_data) - 300)
        start_time = make_datetime(station_data.iloc[start_idx].time)
        end_idx = start_idx+1
        
        delta = make_datetime(station_data.iloc[end_idx].time) - start_time
        delta = delta.total_seconds() / 3600

        while delta <= deltas[len(snow_data)]:
            end_idx+=1
            delta = make_datetime(station_data.iloc[end_idx].time) - start_time
            delta = delta.total_seconds() / 3600

        snow_data[station] = station_data.iloc[start_idx:end_idx]
        #print(len(snow_data))
    return blizzard, snow_data

##############################################################################
def get_prepared_data():
    blizzard, snow = load_data()
    blizzard = group_blizzard_data(blizzard)
    blizzard, snow = sample_non_blizzard(blizzard, snow)
    return blizzard, snow

def make_train_test_split(snow, blizzard):
    """Split the storms, 70% to train, 30% to test"""
    data = list()
    for value in snow.values():
        data.append((value, 0))
    for value in blizzard.values():
        data.append((value, 1))

    random.shuffle(data)

    split_index = int(len(data)*0.7)

    train = data[:split_index]
    test = data[split_index:]

    train_x = list()
    train_y = list()

    test_x = list()
    test_y = list()

    for x, y in train:
        train_x.append(x)
        train_y.append(y)

    for x, y in test:
        test_x.append(x)
        test_y.append(y)

    return train_x, train_y, test_x, test_y
