import pandas as pd
from pathlib import Path
from isd_get_data import GetIsdData


# Reading the list of airports given the office code (gr or gl)
INPUT_DATA_PATH = './src/data/input'
start_year = 2011
end_year = 2020
# offices = ['cma_gr', 'cma_gl']
offices = ['example']

for office in offices:
    with open(f'{INPUT_DATA_PATH}/{office}.txt', 'r') as file:
        airports_list = [x.strip() for x in file.readlines()]

    # Matching the given airports with the ISD codes in isd_all_stations.csv
    isd_stations = pd.read_csv(f'{INPUT_DATA_PATH}/isd_all_stations.csv', index_col=False)
    use_stations = isd_stations[isd_stations['ICAO'].isin(airports_list)].sort_values(by='END', ascending=True)#[2:]

    # Create the paths and make sure the given paths exist
    raw_data_path = f'{INPUT_DATA_PATH}/isd/raw/{office}'  # Specify where the raw data will be stored
    ready_data_path = f'{INPUT_DATA_PATH}/isd/ready/{office}'  # Specify where the extracted data will be stored

    Path(f'{INPUT_DATA_PATH}/isd/raw/{office}').mkdir(parents=True, exist_ok=True)
    Path(f'{INPUT_DATA_PATH}/isd/ready/{office}').mkdir(parents=True, exist_ok=True)

    # Download data
    # Instantiate the class containing the functions to download and edit files
    isd_downloader = GetIsdData(use_stations, raw_data_path, start_year, end_year)
    # This will download the files if they do not exist in the directory ./data/isd/raw
    isd_downloader.download_isd_data()

    # Unify raw files in a dictionary of airports (keys) and
    # all years of data concatenated into a single dataframe (values)
    airports_dict = isd_downloader.unify_files()

    # Extract information from the preprocessed file
    extracted_data = {}
    for airport, data in airports_dict.items():  #
        print(f'Extracting data for {airport}....')
        # Extract information from raw data
        isd_data = isd_downloader.extract_data(data)
        # try:
        #     isd_data = isd_downloader.extract_data(data)
        # except (KeyError, TypeError):
        #     continue
        # Store in a ready-to-use csv
        isd_data.to_csv(f'{ready_data_path}/{airport}_isd_data.csv')
