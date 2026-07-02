import pandas as pd


def load_preprocess_all_queried_data():
    """
    Load and preprocess all queried data from csv files.
    """
    crime_df = pd.read_csv("temp/crime_data_2024.csv")
    block_spatial_df = pd.read_csv("temp/block_spatial_data.csv")
    census_df = pd.read_csv("temp/census_data.csv")

    crime_df.drop(columns=[":id", ":version", ":created_at", ":updated_at"], inplace=True)
    block_spatial_df.drop(columns=[":id", ":version", ":created_at", ":updated_at"], inplace=True)

    crime_df["geoid"] = pd.to_numeric('48' + crime_df["census_block_group"].astype(str), errors='coerce')
    
    census_df.columns = census_df.iloc[0]
    census_df = census_df.iloc[1:].reset_index(drop=True)
    census_df["GIDBG"] = pd.to_numeric(census_df["GIDBG"], errors='coerce')
    all_dfs = {"crime_df": crime_df, "block_spatial_df": block_spatial_df, "census_df": census_df}
    return all_dfs


def agg_crimes_by_block_group_and_family_violence(df):
    """
    Aggregate crimes by block group.
    """
    result = df.pivot_table(index="geoid", columns="family_violence", aggfunc="size", fill_value=0)
    result.columns = ["No Family Violence", "Family Violence"]
    result = result.reset_index().rename(columns={"geoid": "geoid"})
    result["geoid"] = result["geoid"].astype(int)
    result["No Family Violence"] = pd.to_numeric(result["No Family Violence"], errors='coerce').fillna(0)
    result["Family Violence"] = pd.to_numeric(result["Family Violence"], errors='coerce').fillna(0)
    result["crime_count"] = result["No Family Violence"] + result["Family Violence"]
    return result

def join_agg_crimes_spatial_socioeconomic(agg_crime_df, block_spatial_df, census_df):
    # Join the aggregated crime data with spatial and socioeconomic data
    # merged_df = pd.merge(block_spatial_df, census_df, left_on="geoid", right_on="GIDBG", how="left")
    # merged_df = pd.merge(merged_df, agg_crime_df, on="geoid", how="left")
    merged_df = pd.merge(block_spatial_df, agg_crime_df, on="geoid", how="left")
    merged_df["No Family Violence"] = merged_df["No Family Violence"].fillna(0)
    merged_df["Family Violence"] = merged_df["Family Violence"].fillna(0)
    merged_df["crime_count"] = merged_df["crime_count"].fillna(0)
    merged_df = pd.merge(merged_df, census_df, left_on="geoid", right_on="GIDBG", how="left")
    return merged_df

def join_all_data(all_dfs):
    # Load the data
    crime_df = all_dfs["crime_df"]
    block_spatial_df = all_dfs["block_spatial_df"]
    census_df = all_dfs["census_df"]

    # Join the data
    merged_df = pd.merge(crime_df, block_spatial_df, on="geoid", how="left")
    merged_df = pd.merge(merged_df, census_df, left_on="geoid", right_on="GIDBG", how="left")

    # Save the merged data
    return merged_df

def main():
    all_dfs = load_preprocess_all_queried_data()

    merged_df = join_all_data(all_dfs)
    merged_df.to_csv("temp/merged_data.csv", index=False)

    crime_df = all_dfs["crime_df"]
    agg_crime_df = agg_crimes_by_block_group_and_family_violence(crime_df)
    agg_crime_df.to_csv("temp/agg_crime_data.csv", index=False)

    merged_agg_df = join_agg_crimes_spatial_socioeconomic(agg_crime_df, all_dfs["block_spatial_df"], all_dfs["census_df"])
    merged_agg_df.to_csv("temp/merged_agg_data.csv", index=False)

if __name__ == "__main__":
    main()