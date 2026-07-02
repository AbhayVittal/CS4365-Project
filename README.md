# CS4365-Project
## Setup
Before executing any of the scripts, API keys for the City of Austin (Socrata) and US Census Data Portal API keys must be created and put in a ```.env``` file. Use the following as a template:

```bash
SOCRATA_API_KEY="your_API_key_here"
CENSUS_API_KEY="your_API_key_here"
```
Additionally, install the required python dependencies using:
```bash
pip install -r requirements.txt
```

## Running the Project
Run the following python scripts in order:
```bash
cp2_data_retrieval.py
cp2_merge_data.py
cp2_eda.py
cp2_esda.py
```

Currently, all generated datasets, plots, and maps will be placed in the created ```temp``` folder, but that will be updated in a future checkpoint.