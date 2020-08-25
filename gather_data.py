import pandas as pd
from pathlib import Path
from isd_get_data import GetIsdData


# Reading the list of airports given the office code (gr or gl)
INPUT_DATA_PATH = './data'

with open(f'airports.txt', 'r') as file:
    airports_list = [x.strip() for x in file.readlines()]

for station in airports_list:
    # Matching the given airports with the ISD codes in isd_all_stations.csv
    isd_stations = pd.read_csv(f'{INPUT_DATA_PATH}/isd_all_stations.csv', index_col=False)
    use_station = isd_stations[isd_stations['ICAO'] == station]

    # Create the paths and make sure the given paths exist
    raw_data_path = f'{INPUT_DATA_PATH}/raw/{station}'  # Specify where the raw data will be stored
    Path(f'{INPUT_DATA_PATH}/raw/{station}').mkdir(parents=True, exist_ok=True)

    # Download data
    # Instantiate the class containing the functions to download and edit files
    isd_downloader = GetIsdData(use_station, raw_data_path)
    # This will download the files if they do not exist in the directory ./data/isd/raw
    isd_downloader.download_isd_data()

    # Unify raw files in a dictionary of airports (keys) and
    # all years of data concatenated into a single dataframe (values)
    airports_data = isd_downloader.unify_files()

    ready_data_path = f'{INPUT_DATA_PATH}/ready'  # Specify where the extracted data will be stored
    Path(f'{INPUT_DATA_PATH}/ready').mkdir(parents=True, exist_ok=True)
    print(f'Processing {station} data')
    isd_data = isd_downloader.extract_data(airports_data)
    isd_data.to_csv(f'{ready_data_path}/{station}_isd_data.csv')

print('Done!')
