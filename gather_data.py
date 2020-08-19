import pandas as pd
from pathlib import Path
from isd_get_data import GetIsdData


# Reading the list of airports given the office code (gr or gl)
input_path = './data/input'
offices = ['cma_gr', 'cma_gl']

for office in offices:
    with open(f'{input_path}/{office}.txt', 'r') as file:
        airports_list = [x.strip() for x in file.readlines()]
        file.close()

    # Matching the given airports with the ISD codes in isd_all_stations.csv
    isd_stations = pd.read_csv(f'{input_path}/isd_all_stations.csv', index_col=False)
    use_stations = isd_stations[isd_stations['ICAO'].isin(airports_list)].sort_values(by='END', ascending=True)[2:]

    # Download data
    raw_data_path = f'{input_path}/isd/raw/{office}'  # Specify where the raw data will be stored
    ready_data_path = f'{input_path}/isd/ready/{office}'  # Specify where the extracted data will be stored

    # Make sure the given paths exist
    Path(f'{input_path}/isd/raw/{office}').mkdir(parents=True, exist_ok=True)
    Path(f'{input_path}/isd/ready/{office}').mkdir(parents=True, exist_ok=True)

    # Instantiate the class containing the functions to download and edit files
    isd_downloader = GetIsdData(use_stations, raw_data_path)
    # This will download the files if they do not exist in the directory ./data/isd/raw
    isd_downloader.download_isd_data()

    # Unify raw files in a dictionary of airports (keys) and
    # all years of data concatenated into a single dataframe (values)
    airports_dict = isd_downloader.unify_files()

    # Extract information from the preprocessed file
    extracted_data = {}
    for airport, data in airports_dict.items():  #
        print(f'Extracting data for {airport}....')
        # Extract information from raw data and store in a dict
        extracted_data[airport] = isd_downloader.extract_data(data)
        # Store in a ready-to-use csv
        extracted_data[airport].to_csv(f'{ready_data_path}/{airport}_isd_data.csv')
