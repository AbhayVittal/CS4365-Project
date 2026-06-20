import pandas as pd

def join_all_data():
    # Load the data
    crime_df = pd.read_csv("temp/crime_data_2024.csv")
    block_spatial_df = pd.read_csv("temp/block_spatial_data.csv")
    census_df = pd.read_csv("temp/census_data.csv")

    # Preprocess crime data
    crime_df["geoid"] = "48" + crime_df["census_block_group"]

    # Join the data
    merged_df = pd.merge(crime_df, block_spatial_df, on="geoid", how="left")
    merged_df = pd.merge(merged_df, census_df, left_on="geoid", right_on="GEO_ID", how="left")

    # Save the merged data
    merged_df.to_csv("temp/merged_data.csv", index=False)