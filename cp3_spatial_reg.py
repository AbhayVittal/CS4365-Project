
from contextlib import contextmanager
import sys
import libpysal as lp
import spreg
import matplotlib.pyplot as plt
import geopandas as gpd

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

def get_spatial_models(geo_data, weights, attributes):
    geo_data = geo_data.set_index('geoid')
    geo_data[attributes] = geo_data[attributes].fillna(0)  # Fill NaN values with 0 for blocks with no population
    y = geo_data['crime_rate'].values.reshape(-1, 1)
    X = geo_data[attributes].values
    lag_model = spreg.ML_Lag(y, X, w=weights, name_y='crime_rate', name_x=attributes)
    error_model = spreg.ML_Error(y, X, w=weights, name_y='crime_rate', name_x=attributes)
    return lag_model, error_model

def map_spatial_predictions(geo_data, lag_model, error_model):
    geo_data = geo_data.set_index('geoid')
    geo_data['lag_pred'] = lag_model.predy.flatten()
    geo_data['error_pred'] = error_model.predy.flatten()
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    vmin = min(geo_data['lag_pred'].min(), geo_data['error_pred'].min())
    vmax = max(geo_data['lag_pred'].max(), geo_data['error_pred'].max())

    geo_data.plot(column='lag_pred', cmap='Reds', ax=axes[0], legend=True, vmin=vmin, vmax=vmax, legend_kwds={'label': "Predicted Crime Rate (Lag Model)"})
    axes[0].set_title("Spatial Lag Model (SAR) Predictions")
    axes[0].axis('off')

    geo_data.plot(column='error_pred', cmap='Reds', ax=axes[1], legend=True, vmin=vmin, vmax=vmax, legend_kwds={'label': "Predicted Crime Rate (Error Model)"})
    axes[1].set_title("Spatial Error Model (SEM) Predictions")
    axes[1].axis('off')

    fig.suptitle("Spatial Predictions of Crime Rates in Austin, TX", fontsize=16)
    plt.tight_layout()
    plt.savefig("temp/spatial_predictions.png")

def get_separate_spatial_models(geo_data, weights, attributes):
    separated_models = {}
    geo_data = geo_data.set_index('geoid')
    geo_data[attributes] = geo_data[attributes].fillna(0)  # Fill NaN values with 0 for blocks with no population
    for col in ['crime_rate_family_violence', 'crime_rate_no_family_violence']:
        y = geo_data[col].values.reshape(-1, 1)
        X = geo_data[attributes].values
        lag_model = spreg.ML_Lag(y, X, w=weights, name_y=col, name_x=attributes)
        error_model = spreg.ML_Error(y, X, w=weights, name_y=col, name_x=attributes)
        separated_models[col] = {'lag_model': lag_model, 'error_model': error_model}
    return separated_models

def map_separate_spatial_predictions(geo_data, separated_models):
    geo_data = geo_data.set_index('geoid')

    for col in ['crime_rate_family_violence', 'crime_rate_no_family_violence']:
        fig, axes = plt.subplots(1, 2, figsize=(20, 10))
        lag_model = separated_models[col]['lag_model']
        error_model = separated_models[col]['error_model']
        geo_data[f'{col}_lag_pred'] = lag_model.predy.flatten()
        geo_data[f'{col}_error_pred'] = error_model.predy.flatten()

        vmin = min(geo_data[f'{col}_lag_pred'].min(), geo_data[f'{col}_error_pred'].min())
        vmax = max(geo_data[f'{col}_lag_pred'].max(), geo_data[f'{col}_error_pred'].max())

        geo_data.plot(column=f'{col}_lag_pred', cmap='Reds', ax=axes[0], legend=True, vmin=vmin, vmax=vmax, legend_kwds={'label': f"Predicted {col.replace('_', ' ').title()} (Lag Model)"})
        axes[0].set_title(f"Spatial Lag Model (SAR) Predictions for {col.replace('_', ' ').title()}")
        axes[0].axis('off')

        geo_data.plot(column=f'{col}_error_pred', cmap='Reds', ax=axes[1], legend=True, vmin=vmin, vmax=vmax, legend_kwds={'label': f"Predicted {col.replace('_', ' ').title()} (Error Model)"})
        axes[1].set_title(f"Spatial Error Model (SEM) Predictions for {col.replace('_', ' ').title()}")
        axes[1].axis('off')
        fig.suptitle("Spatial Predictions of Crime Rates in Austin, TX", fontsize=16)
        plt.tight_layout()
        plt.savefig(f"temp/spatial_predictions_{col}.png")



def main():
    with tee_stdout("temp/spatial_reg_output.txt"):
        geo_data = load_geojson()
        w = get_spatial_weights(geo_data)
        attributes = ['pct_Prs_Blw_Pov_Lev_ACS_18_22', 'pct_Female_No_SP_ACS_18_22', 'pct_Diff_HU_1yr_Ago_ACS_18_22', 'pct_Vacant_Units_ACS_18_22', 
                      'pct_PUB_ASST_INC_ACS_18_22', 'Med_HHD_Inc_BG_ACS_18_22', 'pct_Not_HS_Grad_ACS_18_22', 'pct_HHD_No_Internet_ACS_18_22',
                      'pct_NonFamily_HHD_ACS_18_22', 'pct_Crowd_Occp_U_ACS_18_22']
        lag_model, error_model = get_spatial_models(geo_data, w, attributes)
        print("Spatial Lag Model Summary:")
        print(lag_model.summary)
        print("\nSpatial Error Model Summary:")
        print(error_model.summary)
        map_spatial_predictions(geo_data, lag_model, error_model)
        separated_models = get_separate_spatial_models(geo_data, w, attributes)
        for col in ['crime_rate_family_violence', 'crime_rate_no_family_violence']:
            print(f"\nSpatial Lag Model Summary for {col.replace('_', ' ').title()}:")
            print(separated_models[col]['lag_model'].summary)
            print(f"\nSpatial Error Model Summary for {col.replace('_', ' ').title()}:")
            print(separated_models[col]['error_model'].summary)
        map_separate_spatial_predictions(geo_data, separated_models)

if __name__ == "__main__":
    main()