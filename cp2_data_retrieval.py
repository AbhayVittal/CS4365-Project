import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv

CRIME_DATA_URL = "https://data.austintexas.gov/api/v3/views/fdj4-gpfu/query.json"

BLOCK_SPATIAL_DATA_URL = "https://data.austintexas.gov/api/v3/views/dwa9-qvcr/query.json"

CENSUS_DATA_URL = "https://api.census.gov/data/2024/pdb/blockgroup"

def get_crime_data():
    """
    Retrieve Austin crime data from 2024.
    """
    payload = {
        "query": "SELECT * WHERE occ_date BETWEEN '2024-01-01T00:00:00' AND '2024-12-31T23:59:59'"
    }
    load_dotenv()
    api_key = os.getenv("SOCRATA_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "X-App-Token": api_key
    }
    response = requests.post(CRIME_DATA_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise ValueError(f"Failed to retrieve crime data: {response.status_code} - {response.text}")

def get_block_spatial_data():
    """
    Retrieve block spatial data for Austin.
    """
    payload = {
        "query": "SELECT *"
    }
    load_dotenv()
    api_key = os.getenv("SOCRATA_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "X-App-Token": api_key
    }
    response = requests.post(BLOCK_SPATIAL_DATA_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise ValueError(f"Failed to retrieve block spatial data: {response.status_code} - {response.text}")

def get_census_data():
    """
    Retrieve census data for Austin.
    """
    load_dotenv()
    api_key = os.getenv("CENSUS_API_KEY")
    columns = ["GEO_ID","GIDBG","State","County","County_name","Tract","LAND_AREA","Tot_Population_ACS_18_22","Median_Age_ACS_18_22","pct_Not_HS_Grad_ACS_18_22","pct_College_ACS_18_22","pct_Pov_Univ_ACS_18_22","pct_Prs_Blw_Pov_Lev_ACS_18_22","pct_No_Health_Ins_ACS_18_22","pct_Diff_HU_1yr_Ago_ACS_18_22","Tot_Prns_in_HHD_ACS_18_22","avg_Tot_Prns_in_HHD_ACS_18_22","pct_Pop_NoCompDevic_ACS_18_22","pct_HHD_NoCompDevic_ACS_18_22","pct_HHD_No_Internet_ACS_18_22","pct_Not_MrdCple_HHD_ACS_18_22","pct_NonFamily_HHD_ACS_18_22","pct_Female_No_SP_ACS_18_22","pct_Sngl_Prns_HHD_ACS_18_22","pct_PUB_ASST_INC_ACS_18_22","Med_HHD_Inc_BG_ACS_18_22","pct_Tot_Occp_Units_ACS_18_22","pct_Vacant_Units_ACS_18_22","pct_Renter_Occp_HU_ACS_18_22","pct_Owner_Occp_HU_ACS_18_22","pct_Single_Unit_ACS_18_22","pct_MLT_U2_9_STRC_ACS_18_22","pct_MLT_U10p_ACS_18_22","pct_Mobile_Homes_ACS_18_22","pct_Crowd_Occp_U_ACS_18_22","pct_Recent_Built_HU_ACS_18_22",]
    geography = ["state:48", "county:453,491,209", "tract:*"]
    full_url = f"https://api.census.gov/data/2024/pdb/blockgroup?get={','.join(columns)}&for=block%20group:*&in={'&in='.join(geography)}&key={api_key}"

    response = requests.get(full_url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise ValueError(f"Failed to retrieve census data: {response.status_code} - {response.text}")

def main():
    df = get_crime_data()
    df.to_csv("temp/crime_data_2024.csv", index=False)
    df = get_block_spatial_data()
    df.to_csv("temp/block_spatial_data.csv", index=False)
    df = get_census_data()
    df.to_csv("temp/census_data.csv", index=False)

if __name__ == "__main__":
    main()