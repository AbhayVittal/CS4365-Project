import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point

def load_agg_data():
    return pd.read_csv("temp/merged_agg_data.csv")

def load_census_data():
    return pd.read_csv("temp/census_data.csv")

def load_geojson():
    return gpd.read_file("temp/block_spatial_data.geojson")

def get_crime_rates(crime_data):
    crime_data['crime_rate'] = crime_data['crime_count'] / crime_data['Tot_Population_ACS_18_22'] * 1000
    return crime_data

def merge_geo_data(geo_data, block_data):
    geo_data['geoid'] = geo_data['geoid'].astype(int)
    return geo_data.merge(block_data, on="geoid", how="left")

def map_crime_counts(geo_crimes):
    fig, ax = plt.subplots(figsize=(10, 10))
    geo_crimes.plot(column="crime_count", cmap='YlOrRd', ax=ax, legend=True, legend_kwds={'label': "Crime Count"})
    ax.set_title("Crime Counts in Austin, TX")
    plt.savefig("temp/crime_counts_map.png")
    plt.close()

def map_crime_rates(geo_crimes):
    fig, ax = plt.subplots(figsize=(10, 10))
    geo_crimes.plot(column="crime_rate", vmin=0, vmax=1000, cmap='YlOrRd', ax=ax, legend=True, legend_kwds={'label': "Crime Rate"})
    ax.set_title("Crime Rates Per 1000 People in Austin, TX")
    plt.savefig("temp/crime_rates_map.png")
    plt.close()

def map_neighborhood_disadvantages(geo_crimes):
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    geo_crimes.plot(column='pct_Prs_Blw_Pov_Lev_ACS_18_22', ax=axes[0], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of People Below Poverty Level"})
    axes[0].set_title("Percentage of People Below Poverty Level in Austin, TX")

    geo_crimes.plot(column='pct_Female_No_SP_ACS_18_22', ax=axes[1], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Female-Headed Households"})
    axes[1].set_title("Percentage of Female-Headed Households in Austin, TX")

    fig.suptitle("Measures of Neighborhood Disadvantages \n in Austin, TX (Figure 1)")

    plt.savefig("temp/neighborhood_disadvantages_map_1.png")
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    geo_crimes.plot(column='pct_Diff_HU_1yr_Ago_ACS_18_22', ax=axes[0], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Residential Turnover"})
    axes[0].set_title("Percentage of Residential Turnover in 1 Year in Austin, TX")

    geo_crimes.plot(column='pct_Vacant_Units_ACS_18_22', ax=axes[1], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Vacant Units"})
    axes[1].set_title("Percentage of Vacant Units in Austin, TX")

    fig.suptitle("Measures of Neighborhood Disadvantages \n in Austin, TX (Figure 2)")

    plt.savefig("temp/neighborhood_disadvantages_map_2.png")
    plt.close()

def map_economic_strain(geo_crimes):
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    geo_crimes.plot(column='pct_PUB_ASST_INC_ACS_18_22', ax=axes[0], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of People Receiving Public Assistance"})
    axes[0].set_title("Percentage of People Receiving Public Assistance in Austin, TX")

    geo_crimes.plot(column='Med_HHD_Inc_BG_ACS_18_22', ax=axes[1], cmap='YlOrRd', legend=True, legend_kwds={'label': "Median Household Income"})
    axes[1].set_title("Median Household Income in Austin, TX")

    fig.suptitle("Measures of Economic Strain \n in Austin, TX (Figure 3)")

    plt.savefig("temp/economic_strain_map.png")
    plt.close()

def map_interpersonal_stress(geo_crimes):
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    geo_crimes.plot(column='pct_Not_HS_Grad_ACS_18_22', ax=axes[0], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of People Not Graduating High School"})
    axes[0].set_title("Percentage of People Not Graduating High School in Austin, TX")

    geo_crimes.plot(column='pct_HHD_No_Internet_ACS_18_22', ax=axes[1], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Households Without Internet"})
    axes[1].set_title("Percentage of Households Without Internet in Austin, TX")

    fig.suptitle("Measures of Interpersonal Stress \n in Austin, TX (Figure 4)")

    plt.savefig("temp/interpersonal_stress_map.png")
    plt.close()


def map_household_structure(geo_crimes):
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    geo_crimes.plot(column='pct_NonFamily_HHD_ACS_18_22', ax=axes[0], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Non-Family Households"})
    axes[0].set_title("Percentage of Non-Family Households in Austin, TX")

    geo_crimes.plot(column='pct_Crowd_Occp_U_ACS_18_22', ax=axes[1], cmap='YlOrRd', legend=True, legend_kwds={'label': "Percentage of Crowded Occupied Units"})
    axes[1].set_title("Percentage of Crowded Occupied Units in Austin, TX")

    fig.suptitle("Housing and Household Structure Measures \n in Austin, TX")

    plt.savefig("temp/household_structure_map.png")
    plt.close()


def main():
    geo_data = load_geojson()
    print(len(geo_data))
    crime_data = load_agg_data()
    crime_data = get_crime_rates(crime_data)
    merged_data = merge_geo_data(geo_data, crime_data)
    merged_data.to_csv("temp/merged_geo_data.csv", index=False)
    map_crime_counts(merged_data)
    map_crime_rates(merged_data)

    map_neighborhood_disadvantages(merged_data)
    map_economic_strain(merged_data)
    map_interpersonal_stress(merged_data)
    map_household_structure(merged_data)

if __name__ == "__main__":
    main()