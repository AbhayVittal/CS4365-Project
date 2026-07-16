import sys
from contextlib import contextmanager

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import libpysal as lp
from splot.esda import  plot_moran, lisa_cluster
from esda.moran import Moran, Moran_Local
from spopt.region import Skater


@contextmanager
def tee_stdout(log_path):
    original_stdout = sys.stdout
    log_file = open(log_path, "w", encoding="utf-8")

    class Tee:
        def __init__(self, stdout, log_file):
            self.stdout = stdout
            self.log_file = log_file

        def write(self, data):
            self.stdout.write(data)
            self.log_file.write(data)

        def flush(self):
            self.stdout.flush()
            self.log_file.flush()

        def isatty(self):
            return False

    sys.stdout = Tee(original_stdout, log_file)
    try:
        yield
    finally:
        sys.stdout = original_stdout
        log_file.close()

def load_geojson():
    return gpd.read_file("temp/merged_geo_data.geojson")

def get_spatial_weights(geo_data):
    geo_data = geo_data.set_index('geoid')
    w = lp.weights.Queen.from_dataframe(geo_data)
    w.transform = 'R'
    return w

def morans_I(geo_data, weights):
    geo_data = geo_data.set_index('geoid')
    morans_df = pd.DataFrame(columns=['Variable', 'Moran_I', 'p_value'])
    for col in ['crime_rate', 'crime_rate_family_violence', 'crime_rate_no_family_violence']:
        y = geo_data[col].values
        mi = Moran(y, weights)
        fig, ax = plot_moran(mi, zstandard=True, aspect_equal=True)
        fig.suptitle(f"Moran's Index Scatterplot for {col.replace('_', ' ').title()} in Austin, TX", fontsize=16)
        plt.savefig(f"temp/morans_I_scatterplot_{col}.png")
        plt.close()
        morans_df.loc[len(morans_df)] = [col, mi.I, mi.p_sim]
    return morans_df

def lisa_cluster_analysis(geo_data, weights):
    geo_data = geo_data.set_index('geoid')
    for col in ['crime_rate', 'crime_rate_family_violence', 'crime_rate_no_family_violence']:
        y = geo_data[col].values
        lisa = Moran_Local(y, weights, transformation='R', permutations=999)
        fig, ax = plt.subplots(figsize=(10, 10))
        lisa_cluster(lisa, geo_data, p=0.05, ax=ax)
        ax.set_title(f"LISA Cluster Map for {col.replace('_', ' ').title()} in Austin, TX")
        plt.savefig(f"temp/lisa_cluster_map_{col}.png")
        plt.close()

def skater_clustering(geo_data, weights):
    attribute_list = {
        'neighborhood_disadvantages': ['pct_Prs_Blw_Pov_Lev_ACS_18_22', 'pct_Female_No_SP_ACS_18_22', 'pct_Diff_HU_1yr_Ago_ACS_18_22', 'pct_Vacant_Units_ACS_18_22'],
        'economic_strain': ['pct_PUB_ASST_INC_ACS_18_22', 'Med_HHD_Inc_BG_ACS_18_22'],
        'interpersonal_stress':['pct_Not_HS_Grad_ACS_18_22', 'pct_HHD_No_Internet_ACS_18_22'],
        'household_structure': ['pct_NonFamily_HHD_ACS_18_22', 'pct_Crowd_Occp_U_ACS_18_22']
    }
    geo_data = geo_data.set_index('geoid')
    for category, attributes in attribute_list.items():
        for attr in attributes:
            geo_data[attr] = geo_data[attr].fillna(0)
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        model = Skater(geo_data, weights, attributes, n_clusters=7)
        model.solve()
        geo_data[f'cluster_{category}_7'] = model.labels_
        print(f"Skater Clustering Results for {category.replace('_', ' ').title()} with 7 Clusters:")
        print(geo_data.groupby(f'cluster_{category}_7')[attributes].mean())
        geo_data.plot(column=f'cluster_{category}_7', cmap='Set3', legend=True, ax=ax)
        ax.set_title(f"Skater Clustering (7 Clusters) for {category.replace('_', ' ').replace(',', '\n').title()} in Austin, TX")
        ax.text(0.5, -0.05, f"Variables:\n{'\n'.join(attributes)}", transform=ax.transAxes, fontsize=10, va='top', ha='center')
        plt.tight_layout()
        plt.savefig(f"temp/skater_clustering_{category}.png")
        plt.close()

def skater_clustering_with_crime_rates(geo_data, weights):

    fig, axes = plt.subplots(1, 2, figsize=(20, 11))

    geo_data = geo_data.set_index('geoid')

    non_family_attributes = ['crime_rate_no_family_violence', 'pct_Prs_Blw_Pov_Lev_ACS_18_22', 'pct_Female_No_SP_ACS_18_22', 'pct_Diff_HU_1yr_Ago_ACS_18_22', 'pct_Vacant_Units_ACS_18_22', 'pct_PUB_ASST_INC_ACS_18_22', 'Med_HHD_Inc_BG_ACS_18_22']
    for attr in non_family_attributes:
        geo_data[attr] = geo_data[attr].fillna(0)
    model = Skater(geo_data, weights, non_family_attributes, n_clusters=7)
    model.solve()
    geo_data['cluster_non_family_crime_7'] = model.labels_
    print("Skater Clustering Results for Variables Associated with Non-Family Crime Rates with 7 Clusters:")
    print(geo_data.groupby('cluster_non_family_crime_7')[non_family_attributes].mean())
    geo_data.plot(column='cluster_non_family_crime_7', cmap='Set3', legend=True, ax=axes[0])
    axes[0].set_title("Skater Clustering Results for Variables Associated with Non-Family Crime Rates with 7 Clusters:")
    axes[0].text(0.5, -0.05, f"Variables:\n{'\n'.join(non_family_attributes)}", transform=axes[0].transAxes, fontsize=10, va='top', ha='center')

    family_attributes = ['crime_rate_family_violence', 'pct_Not_HS_Grad_ACS_18_22', 'pct_HHD_No_Internet_ACS_18_22', 'pct_NonFamily_HHD_ACS_18_22', 'pct_Crowd_Occp_U_ACS_18_22']
    for attr in family_attributes:
        geo_data[attr] = geo_data[attr].fillna(0)
    model = Skater(geo_data, weights, family_attributes, n_clusters=7)
    model.solve()
    geo_data['cluster_family_crime_7'] = model.labels_
    print("Skater Clustering Results for Variables Associated with Family Crime Rates with 7 Clusters:")
    print(geo_data.groupby('cluster_family_crime_7')[family_attributes].mean())
    geo_data.plot(column='cluster_family_crime_7', cmap='Set3', legend=True, ax=axes[1])
    axes[1].set_title("Skater Clustering Results for Variables Associated with Family Crime Rates with 7 Clusters:")
    axes[1].text(0.5, -0.05, f"Variables:\n{'\n'.join(family_attributes)}", transform=axes[1].transAxes, fontsize=10, va='top', ha='center')

    fig.suptitle("Skater Clustering Results for Variables Associated with Crime Rates in Austin, TX (7 Clusters)", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"temp/skater_clustering_crime_comparisons.png")
    plt.close()

def main():
    with tee_stdout("temp/spatial_ml_output.txt"):
        geo_data = load_geojson()
        w = get_spatial_weights(geo_data)
        morans_df = morans_I(geo_data, w)
        print(morans_df)
        lisa_cluster_analysis(geo_data, w)
        skater_clustering(geo_data, w)
        skater_clustering_with_crime_rates(geo_data, w)

if __name__ == "__main__":
    main()