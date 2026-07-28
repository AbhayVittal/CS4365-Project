import numpy as np
import libpysal as lp
import matplotlib.pyplot as plt
import geopandas as gpd
import joblib

def load_geojson():
    return gpd.read_file("data/merged_geo_data.geojson")

def get_spatial_weights(geo_data):
    geo_data = geo_data.set_index('geoid')
    w = lp.weights.Queen.from_dataframe(geo_data)
    w.transform = 'R'
    return w

def load_spatial_models():
    lag_model, error_model = joblib.load('results/spatial_models_crime_rate.pkl')
    all_models = joblib.load('results/separated_spatial_models.pkl')
    all_models['crime_rate'] = {'lag_model': lag_model, 'error_model': error_model}
    return all_models

def extract_spatial_lag_parameters(lag_model):
    rho = lag_model.rho
    betas = lag_model.betas.flatten()
    return rho, betas

def map_scenarios(geo_data, weights, rho, betas, attributes, predictor):
    w_full, _ = weights.full()
    n = w_full.shape[0]
    I_matrix = np.eye(n)
    spatial_multiplier = np.linalg.inv(I_matrix - rho * w_full)

    geo_data = geo_data.set_index('geoid')
    geo_data[attributes] = geo_data[attributes].fillna(0)  # Fill NaN values with 0 for blocks with no population
    geo_data_s1 = geo_data.copy()
    geo_data_s2 = geo_data.copy()

    geo_data_s1['pct_Prs_Blw_Pov_Lev_ACS_18_22'] -= 2.5
    geo_data_s1['Med_HHD_Inc_BG_ACS_18_22'] *= 1.03

    X_s1 = np.column_stack([np.ones(len(geo_data_s1)), geo_data_s1[attributes].values])
    geo_data_s1[f'{predictor}_s1'] = spatial_multiplier @ X_s1 @ betas[:-1]

    geo_data_s2['pct_Prs_Blw_Pov_Lev_ACS_18_22'] += 2.5
    geo_data_s2['Med_HHD_Inc_BG_ACS_18_22'] *= 0.97

    X_s2 = np.column_stack([np.ones(len(geo_data_s2)), geo_data_s2[attributes].values])
    geo_data_s2[f'{predictor}_s2'] = spatial_multiplier @ X_s2 @ betas[:-1]
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    vmin = min(geo_data_s1[f'{predictor}_s1'].min(), geo_data_s2[f'{predictor}_s2'].min())
    vmax = max(geo_data_s1[f'{predictor}_s1'].max(), geo_data_s2[f'{predictor}_s2'].max())

    geo_data_s1.plot(column=f'{predictor}_s1', cmap='Reds', vmin=vmin, vmax=vmax, legend=True, ax=axes[0])
    axes[0].set_title("Predicted Crime Rate under Scenario 1", fontsize=16)
    geo_data_s2.plot(column=f'{predictor}_s2', cmap='Reds', vmin=vmin, vmax=vmax, legend=True, ax=axes[1])
    axes[1].set_title("Predicted Crime Rate under Scenario 2", fontsize=16)
    
    fig.suptitle(f"{predictor.title().replace('_', ' ')} under Different Scenarios in Austin, TX", fontsize=20)
    plt.tight_layout()
    plt.savefig(f"maps/{predictor}_scenarios.png")
    plt.close()

    
    geo_data[f'{predictor}_net_difference'] = geo_data_s2[f'{predictor}_s2'] - geo_data_s1[f'{predictor}_s1']
    fig, ax = plt.subplots(figsize=(10, 10))
    geo_data.plot(column=f'{predictor}_net_difference', cmap='coolwarm', legend=True, ax=ax)
    ax.set_title(f"Net Difference in {predictor.title().replace('_', ' ')} between\nScenario 2 and Scenario 1 in Austin, TX", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"maps/{predictor}_net_difference.png")


def main():
    geo_data = load_geojson()
    w = get_spatial_weights(geo_data)
    all_models = load_spatial_models()
    print(all_models['crime_rate']['lag_model'].summary)

    attributes = ['pct_Prs_Blw_Pov_Lev_ACS_18_22', 'pct_Female_No_SP_ACS_18_22', 'pct_Diff_HU_1yr_Ago_ACS_18_22', 'pct_Vacant_Units_ACS_18_22', 
                  'pct_PUB_ASST_INC_ACS_18_22', 'Med_HHD_Inc_BG_ACS_18_22', 'pct_Not_HS_Grad_ACS_18_22', 'pct_HHD_No_Internet_ACS_18_22',
                  'pct_NonFamily_HHD_ACS_18_22', 'pct_Crowd_Occp_U_ACS_18_22'] 
    for key, model in all_models.items():
        rho, betas = extract_spatial_lag_parameters(model['lag_model'])
        map_scenarios(geo_data, w, rho, betas, attributes, f"predicted_{key}")

    map_scenarios(geo_data, w, rho, betas, attributes, 'predicted_crime_rate')


if __name__ == "__main__":
    main()