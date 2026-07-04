import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import libpysal as lp
import numpy as np
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster
from esda.moran import Moran, Moran_Local
from sklearn.preprocessing import StandardScaler
from spopt.region import AZP

def load_geojson():
    return gpd.read_file("temp/merged_geo_data.geojson")

def get_spatial_weights(geo_data):
    geo_data = geo_data.set_index('geoid')
    w = lp.weights.Queen.from_dataframe(geo_data)
    w.transform = 'R'
    return w

def morans_I(geo_data, weights):
    geo_data = geo_data.set_index('geoid')
    y = geo_data['crime_rate'].values
    mi = Moran(y, weights)
    fig, ax = plot_moran(mi, zstandard=True, aspect_equal=True)
    fig.suptitle("Moran's Index Scatterplot for Total Crime Rates in Austin, TX", fontsize=16)
    plt.savefig("temp/morans_I_scatterplot.png")
    plt.close()
    return mi.I, mi.p_sim

def lisa_cluster_analysis(geo_data, weights):
    geo_data = geo_data.set_index('geoid')
    y = geo_data['crime_rate'].values
    lisa = Moran_Local(y, weights, transformation='R', permutations=999)
    fig, ax = plt.subplots(figsize=(10, 10))
    lisa_cluster(lisa, geo_data, p=0.05, ax=ax)
    ax.set_title("LISA Cluster Map for Total Crime Rates in Austin, TX")
    plt.savefig("temp/lisa_cluster_map.png")
    plt.close()

def main():
    geo_data = load_geojson()
    w = get_spatial_weights(geo_data)
    morans_i, p_value = morans_I(geo_data, w)
    print(f"Moran's I: {morans_i}, p-value: {p_value}")
    lisa_cluster_analysis(geo_data, w)

if __name__ == "__main__":
    main()