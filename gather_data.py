import pandas as pd
from pathlib import Path
from isd_get_data import GetIsdData


# Reading the list of airports given the office code (gr or gl)
input_path = './data/input'
office = 'gr'

with open(f'{input_path}/{office}.txt', 'r') as file:
    airports_list = [x.strip() for x in file.readlines()]
    file.close()

# Matching the given airports with the ISD codes in isd_all_stations.csv
isd_stations = pd.read_csv(f'{input_path}/isd_all_stations.csv', index_col=False)
airports_df = isd_stations[isd_stations['ICAO'].isin(airports_list)].sort_values(by='END', ascending=True)

# Download data
raw_data_path = './data/isd/raw'  # Specify where the raw data will be stored
ready_data_path = './data/isd/ready'  # Specify where the extracted data will be stored

# Make sure the given paths exist
Path(raw_data_path).mkdir(parents=True, exist_ok=True)
Path(ready_data_path).mkdir(parents=True, exist_ok=True)

# Instantiate the class containing the functions to download and edit files
isd_downloader = GetIsdData(airports_df, raw_data_path)
isd_downloader.download_isd_data()  # This will download the files if they do not exist in the directory ./data/isd/raw

# Unify raw files in a dictionary of airports (keys) and all years of data concatenated into a single dataframe (values)
airports_dict = isd_downloader.unify_files()

# Extract information from the preprocessed file
extracted_data = {}
for airport, data in airports_dict.items():  #
    print(f'Extracting data for {airport}....')
    extracted_data[airport] = isd_downloader.extract_data(data)  # Extract information from raw data and store in a dict
    extracted_data[airport].to_csv(f'{ready_data_path}/{airport}_isd_data.csv')  # Store in a ready-to-use csv
