#!/bin/python3
import netCDF4 as n4
import xarray as xr
from pathlib import Path
import re
import pandas as pd

data_dir = "data_raw/"

def get_data(filename):
    """Read the netCDF file data"""
    #nc = n4.Dataset(filename, mode='r')
    #data = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
    #nc.close()
    return xr.open_dataset(filename)
    

def get_all_data():
    data = dict()
    for file in Path(data_dir).glob("**/*"):
        print(file)
        date = re.search(r'[0-9]{10}', str(file))[0]
        data[date] = get_data(file)
    return data


def validate(data):
    ## validate that the longitude and latitude data is consistent
    ## for all of the data
    data_0 = list(data.values())[0]

    for entry in data.values():
        if (entry.coords["lon"].data-data_0.coords["lon"].data).all():
            print(entry)
        if (entry.coords["lat"].data-data_0.coords["lat"].data).all():
            print(entry)

    ## seems like the latitude and longitude data is consistent.


def get_all_data_combined(year):
    data = list()

    for file in sorted(Path(data_dir).glob(f"**/*_{year}*")):
        print(file)
        time = pd.to_datetime(re.search(r'[0-9]{10}', str(file))[0], format="%Y%m%d%H")
        this_data = get_data(file)
        this_data = this_data.expand_dims(time=[time])
        this_data = this_data.assign_coords(time=[time])
        data.append(this_data)
    combined = xr.concat(data, dim='time')
    return combined


def get_all_data_combined2():
    dates = list()
    for file in sorted(Path(data_dir).glob("**/*")):
        time = pd.to_datetime(re.search(r'[0-9]{10}', str(file))[0], format="%Y%m%d%H")
        dates.append(time)

    # Open lazily using xarray + dask
    def preprocess(ds, time):
        return ds.expand_dims(time=[time]).assign_coords(time=[time])

    files = list(sorted(Path(data_dir).glob("**/*")))
    datasets = [
        preprocess(xr.open_dataset(f, chunks={}), t)
        for f, t in zip(files, dates)
    ]

    # Concatenate along time
    combined = xr.concat(datasets, dim="time")
    return combined

