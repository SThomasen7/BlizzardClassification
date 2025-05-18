#!/bin/python3
from matplotlib import pyplot as plt
import pandas as pd

def load_data():
    data = pd.read_csv("aggregated.csv")
    data = data[data.temp < 300]
    blizzard = data[data.has_blizzard == 1]
    snow = data[data.has_blizzard == 0]
    return snow, blizzard

def plot_data(snow, blizzard):

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(snow.wind_speed, snow.temp, 
                snow.visibility_distance, marker='x',
                color="grey", alpha=0.1)
    ax.scatter(blizzard.wind_speed, blizzard.temp, 
                blizzard.visibility_distance, marker='o', color="lightblue", alpha=1.0)

    ax.set_xlabel('Wind speed m/s')
    ax.set_ylabel('Temperature °C')
    ax.set_zlabel('Visibility Distance m')

    plt.show()
