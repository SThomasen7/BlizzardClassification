#!/bin/python3
"""
Plot the locations of the blizzards within the dataset
Tutorial that helped me with this: 
https://jcutrer.com/python/learn-geopandas-plotting-usmaps
"""
import pandas as pd
import geopandas
from matplotlib import pyplot as plt

def load_blizzard_data():
    data = pd.read_csv("../data/aggregated_fix.csv")
    return data[data.has_blizzard == 1]

def plot_states():
    fig = plt.figure(1, figsize=(25,15))
    ax = fig.add_subplot()
    states = geopandas.read_file('data/usa-states-census-2014.shp')
    states.apply(lambda x: ax.annotate(x.NAME, xy=x.geometry.centroid.coords[0],
        ha='center', fontsize=7), axis=1)
    states.boundary.plot(ax=ax, figsize=(12, 12))
    blizzards = load_blizzard_data()
    plt.scatter(blizzards.longitude, blizzards.latitude, marker='X', color='cadetblue')
    plt.show()

if __name__ == '__main__':
    plot_states()

