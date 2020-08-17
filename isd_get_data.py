import urllib.request
import pandas as pd
import os
import math
import re
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class GetIsdData:
    """
    Contain functions to gather data from ISD,
    organise the files in directories and
    extract information from them
    """

    def __init__(self, airports_df, path):
        self.station_codes = airports_df['CODE'].values  # Code goes into the link to download the files
        self.station_icao = airports_df['ICAO'].values  # ICAO identifier goes into file name
        self.PATH = path

    def download_isd_data(self):
        """
        Creates the link to download ISD files as well as the directories to put the files
        :return: Organizes the downloaded files into folders
        """
        for code, icao in zip(self.station_codes, self.station_icao):  # Looping over the given airports
            print(f'Downloading data for {icao}')
            Path(f'{self.PATH}/{icao}').mkdir(parents=True, exist_ok=True)  # Creating a folder for each airport
            for year in range(2011, 2020, 1):
                url = f'https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{code}.csv'
                filename = f'{self.PATH}/{icao}/{year}.csv'
                if not os.path.exists(filename):  # Only download if file does not exist
                    urllib.request.urlretrieve(url, filename)

    def unify_files(self):
        """
        Takes oll the raw downloaded files and unites them into one file
        :return: a dictionary with the airport ICAO as key and dataframes with all the years concatenated as values
        """
        dict_data = {}
        for code, icao in zip(self.station_codes, self.station_icao):
            csv_list = os.listdir(path=f'{self.PATH}/{icao}/')
            grouped = []
            for file in sorted(csv_list):
                df = pd.read_csv(f'{self.PATH}/{icao}/{file}', index_col='DATE')  # DATE column is used as index
                grouped.append(df)
            data = pd.concat(grouped, sort=False)  # Stores all data data into a dataframe
            data = data.set_index(data.index)  # Sets index to datetime format
            dict_data[icao] = data
        return dict_data

    def get_variable(self, df, column, column_list):
        """
        This function access the raw 'df' (pandas dataframe),
        uses a list with the 'column' name (str) to explore the variable column,
        receives a 'column_list' of the columns names and
        returns a dataframe with the extracted data for the variable indicated.
        """
        variable = pd.DataFrame(df[column], columns=[column])
        variable = variable[column].str.split(',', expand=True)
        variable.columns = column_list
        return variable

    def calculate_rh(self, temperature, dew):
        """
        Receives air temperature (t) and dew point (d) and returns relative humidity
        RH = 100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
        """
        rh_list = []
        for t, d in zip(temperature, dew):
            rh = 100 * ((math.exp((17.625 * d) / (243.04 + d))) / (math.exp((17.625 * t) / (243.04 + t))))
            rh_list.append(rh)
        return rh_list

    def extract_data(self, data):
        """
        Contains instructions based on ISD documentation to extract data into a usable format
        License: https://www.ncdc.noaa.gov/isd/data-access
        Documentation: https://www.ncei.noaa.gov/data/global-hourly/doc/isd-format-document.pdf
        """
        wind_cols = ['direction', 'quality', 'type_code', 'speed', 'speed_quality']
        wind = self.get_variable(data, 'WND', wind_cols)

        visibility_cols = ['visibility', 'quality', 'variability', 'quality_variability']
        visibility = self.get_variable(data, 'VIS', visibility_cols)

        phenomenon_cols = ['phenomenon', 'quality']
        phenomenon1 = self.get_variable(data, 'MW1', phenomenon_cols)
        phenomenon2 = self.get_variable(data, 'MW2', phenomenon_cols)
        # phenomenon3 = get_variable(data, 'MW3', phenomenon_cols)

        sky_cover_cols = ['coverage', 'quality', 'base_height', 'base_height_quality', 'cloud_type',
                          'cloud_type_quality']
        sky_cover1 = self.get_variable(data, 'GA1', sky_cover_cols)
        sky_cover2 = self.get_variable(data, 'GA2', sky_cover_cols)
        sky_cover3 = self.get_variable(data, 'GA3', sky_cover_cols)
        sky_cover4 = self.get_variable(data, 'GA4', sky_cover_cols)

        ceiling_cols = ['ceiling', 'quality', 'determination_code', 'cavok']
        ceiling = self.get_variable(data, 'CIG', ceiling_cols)

        temperature_cols = ['temperature', 'quality']
        temperature = self.get_variable(data, 'TMP', temperature_cols)

        dew_cols = ['dew', 'quality']
        dew = self.get_variable(data, 'DEW', dew_cols)

        # Concatenating all data into a base df containing the meteorological variables
        base_data = pd.concat([data['REM'], wind[['direction', 'speed']].astype(int),
                               visibility[['visibility']].astype(int),
                               phenomenon1[['phenomenon']], phenomenon2[['phenomenon']],
                               sky_cover1[['coverage']], sky_cover2[['coverage']],
                               sky_cover3[['coverage']], sky_cover4[['coverage']],
                               ceiling[['ceiling']].astype(int), ceiling[['cavok']],
                               temperature[['temperature']].fillna(9999).astype(int),
                               dew[['dew']].fillna(9999).astype(int)], axis=1)

        # Note that there were no information on sea level pressure, which will be extracted from REM column
        # Iterating over the METAR messages to extract the slp values
        metar = base_data['REM']
        pressure = []
        for code in metar:
            slp = str(re.findall(r"Q\d.+", code))
            pressure.append(
                slp[3:7])  # the values were put into the list pressure, which will be appended to the final data frame

        base_data['slp'] = pressure

        base_data.columns = ['REM', 'direction', 'speed', 'visibility',
                             'phenomenon_1', 'phenomenon_2',
                             'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4',
                             'ceiling', 'cavok', 'temperature', 'dew', 'slp']

        # Some corrections in the data...

        # Wind
        # According with the manual, wind direction as 999 can be missing or variable wind.
        # It can be calm too, as seen by the data (comparing them to METAR)...
        # When the wind is calm, let's set them to 0
        base_data['direction'][(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0
        base_data['speed'][(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0

        # When the wind is variable, let's set only the direction to 0
        base_data['direction'][(base_data['direction'] == 999) & (base_data['speed'] != 0)] = 0

        # According to the manual, speed_rate seen as 9999 means it is missing.
        # Or it is just a typo at the METAR. Let's just delete them...
        base_data['speed'][base_data['speed'] == 9999] = 0

        # Visibility
        # The manual says visibility values of 999999 means they are missing.
        # If CAVOK is Y, it means the visibility is greater than 10000 meters...
        # Also, values of visibility above 10,000m must not be considered as restrictive to the operations,
        # thus, let's just set them as unlimited...
        base_data['visibility'][(base_data['visibility'] > 9001) & (base_data['visibility'] < 999998)] = 10000
        base_data['visibility'][base_data['visibility'] == 999999] = 10000

       # Ceiling
        # According to the manual, ceiling regarded as 99999 means it's missing (from the METAR)
        # and 22000 means unlimited...
        # BUT... "ceiling values above 1600m (5000ft) are not considered ceiling" Lets just make them NaN...
        base_data['ceiling'] = base_data['ceiling'].astype(int)
        base_data['ceiling'][(base_data['ceiling'] > 1599)] = 5001

        # Coverage
        base_data.filter(regex='coverage').fillna(0)

        # Temperature
        # The manual says temperature/dew values above 9999 means they are missing...
        base_data['temperature'][base_data['temperature'] == 9999] = np.nan
        base_data['dew'][base_data['dew'] == 9999] = np.nan

        # Sea Level Pressure
        # As we extracted the slp values from METAR message using regex,
        # some typos corrupted the data extracted. Let's just ignore them...
        dirty = base_data['slp'].tolist()
        dirty = [str(i) for i in dirty]

        clean = []
        for value in dirty:
            if not value.isdigit():
                clean.append(9999)
            else:
                clean.append(value)

        clean = [float(x) for x in clean]
        base_data['slp'] = clean

        # Also, values of pressure greater than 1050 and lesser than 900 are absurd.
        # They are probably typos as well so let's get rid of them...
        base_data['slp'][(base_data['slp'] > 1050) | (base_data['slp'] < 900)] = np.nan

        # Correcting data for standard units

        # Wind direction is in degrees, which is fine...

        # Wind Speed is in meters per second and scaled by 10, let's downscale them and convert to knots...
        base_data['speed'] = base_data['speed'] * 0.194384

        # Ceiling is in meters, let's set them to feet
        base_data['ceiling'] = round(base_data['ceiling'] * 3.28084)

        # Visibility is in meters, which is fine...

        # Temperature and dew are scaled by 10, let's downscale them...
        base_data['temperature'] = base_data['temperature'] / 10
        base_data['dew'] = base_data['dew'] / 10

        # Pressure is in Hectopascal, which is fine...

        # Broad view of the data
        # print(base_data.describe())


        # Dropping unused columns
        base_data = base_data.drop(['REM', 'cavok'], axis=1).round(0)
        # Create a column for relative humidity
        base_data['rh'] = self.calculate_rh(base_data['temperature'], base_data['dew'])

        base_data[['direction',
                   'speed',
                   'visibility',
                   'temperature',
                   'dew',
                   'slp',
                   'rh']] = (base_data[['direction',
                                        'speed',
                                        'visibility',
                                        'temperature',
                                        'dew',
                                        'slp',
                                        'rh']].ffill() + base_data[['direction',
                                                                    'speed',
                                                                    'visibility',
                                                                    'temperature',
                                                                    'dew',
                                                                    'slp',
                                                                    'rh']].bfill()) / 2
        return base_data
