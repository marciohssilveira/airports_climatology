import urllib.request
from urllib.error import HTTPError
import pandas as pd
from pandas.io import parsers
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

    def __init__(self, data, path, start_year, end_year):
        self.station_codes = data['CODE'].values  # Code goes into the link to download the files
        self.station_icao = data['ICAO'].values  # ICAO identifier goes into file name
        self.path = path
        self.start_year = start_year
        self.end_year = end_year

    def download_isd_data(self):
        """
        Creates the link to download ISD files as well as the directories to put the files
        :return: Organizes the downloaded files into folders
        """
        for code, icao in zip(self.station_codes, self.station_icao):  # Looping over the given airports
            Path(f'{self.path}/{icao}').mkdir(parents=True,
                                              exist_ok=True)  # Creating a folder for each airport
            for year in range(self.start_year, self.end_year, 1):
                url = f'https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{code}.csv'
                filename = f'{self.path}/{icao}/{year}.csv'
                if not os.path.exists(filename):  # Only download if file does not exist
                    try:
                        urllib.request.urlretrieve(url, filename)
                    except urllib.error.HTTPError as exception:
                        print(f'Unfortunately there is no {year} data available for {icao}: Error {exception.code}')
                        continue

    def unify_files(self):
        """
        Takes oll the raw downloaded files and unites them into one file
        :return: a dictionary with the airport ICAO as key and dataframes with all the years concatenated as values
        """
        dict_data = {}
        for icao in self.station_icao:
            csv_list = os.listdir(path=f'{self.path}/{icao}/')
            grouped = []
            for file in sorted(csv_list):
                # DATE column is used as index
                try:
                    df = pd.read_csv(f'{self.path}/{icao}/{file}',
                                     index_col='DATE',
                                     error_bad_lines=False,
                                     engine="python")
                except (parsers.CParserWrapper, KeyError) as exception:
                    f'{file} data for {icao} could not be processed: Error {exception.code}'
                    continue
                grouped.append(df)
            data = pd.concat(grouped, sort=False)  # Stores all data data into a dataframe
            data = data.set_index(data.index)  # Sets index to datetime format
            dict_data[icao] = data
        return dict_data

    def get_variable(self, data, column, column_list):
        """
        This function access the raw 'df' (pandas dataframe),
        uses a list with the 'column' name (str) to explore the variable column,
        receives a 'column_list' of the columns names and
        returns a dataframe with the extracted data for the variable indicated.
        """
        variable = pd.DataFrame(data[column], columns=[column])
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
        # Selecting ONLY METAR observations to avoid redundancies
        data = data[data['REPORT_TYPE'].isin(['FM-15', 'FM-16', 'SY-MT'])]

        # Extracting wind data from WND column
        wind_cols = ['direction', 'quality', 'type_code', 'speed', 'speed_quality']
        wind = self.get_variable(data, 'WND', wind_cols)

        # Extracting visibility data from VIS column
        visibility_cols = ['visibility', 'quality', 'variability', 'quality_variability']
        visibility = self.get_variable(data, 'VIS', visibility_cols)

        # Extracting first two groups of sigwx data from MW1 and MW2 columns
        phenomenon_cols = ['phenomenon', 'quality']
        phenomenon1 = self.get_variable(data, 'MW1', phenomenon_cols)
        phenomenon2 = self.get_variable(data, 'MW2', phenomenon_cols)

        # Extracting four layers of sky cover from GAx columns
        sky_cover_cols = ['coverage', 'quality', 'base_height', 'base_height_quality', 'cloud_type',
                          'cloud_type_quality']
        sky_cover1 = self.get_variable(data, 'GA1', sky_cover_cols)
        sky_cover2 = self.get_variable(data, 'GA2', sky_cover_cols)
        sky_cover3 = self.get_variable(data, 'GA3', sky_cover_cols)
        sky_cover4 = self.get_variable(data, 'GA4', sky_cover_cols)

        # Extracting Ceiling data from CIG column
        ceiling_cols = ['ceiling', 'quality', 'determination_code', 'cavok']
        ceiling = self.get_variable(data, 'CIG', ceiling_cols)

        # Extracting air temperature data from TMP column
        temperature_cols = ['temperature', 'quality']
        temperature = self.get_variable(data, 'TMP', temperature_cols)

        # Extracting dew point temperature data from DEW column
        dew_cols = ['dew', 'quality']
        dew = self.get_variable(data, 'DEW', dew_cols)

        # Concatenating all data into a base df containing the meteorological variables
        base_data = pd.concat([wind[['direction', 'speed']].fillna(99999),
                               visibility[['visibility']].fillna(99999),
                               phenomenon1[['phenomenon']].fillna(99999),
                               phenomenon2[['phenomenon']].fillna(99999),
                               sky_cover1[['coverage']].fillna(99999),
                               sky_cover2[['coverage']].fillna(99999),
                               sky_cover3[['coverage']].fillna(99999),
                               sky_cover4[['coverage']].fillna(99999),
                               ceiling[['ceiling']].fillna(99999),
                               ceiling[['cavok']].fillna(99999),
                               temperature[['temperature']].fillna(99999),
                               dew[['dew']].fillna(99999)],
                              axis=1)

        # Note that there were no information on sea level pressure, which will be extracted from REM column
        # Iterating over the METAR messages to extract the slp values
        metar = data['REM'].to_list()
        pressure = []
        for code in metar:
            slp = str(re.findall(r"Q\d.+", code))
            # the values are put into the list pressure, which will be appended to the final data frame
            pressure.append(slp[3:7])

        # Sea Level Pressure
        # As we extracted the slp values from METAR message using regex,
        # some typos corrupted the data extracted. Let's just ignore them...
        dirty = [str(i) for i in pressure]

        clean = []
        for value in dirty:
            if not value.isdigit():
                clean.append(np.nan)
            else:
                clean.append(value)

        clean = [float(x) for x in clean]
        base_data['slp'] = clean

        base_data.columns = ['direction', 'speed', 'visibility',
                             'phenomenon_1', 'phenomenon_2',
                             'coverage_1',
                             'coverage_2',
                             'coverage_3',
                             'coverage_4',
                             'ceiling', 'cavok', 'temperature', 'dew', 'slp']

        # Some corrections in the data...
        # Wind
        # According with the manual, wind direction as 999 can be missing or variable wind.
        # It can be calm too, as seen by the data (comparing them to METAR)...
        # When the wind is calm, let's set them to 0
        base_data['direction'].loc[(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0
        base_data['speed'].loc[(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0

        # When the wind is variable, let's set only the direction to 0
        base_data['direction'].loc[(base_data['direction'] == 999) & (base_data['speed'] != 0)] = 0

        # According to the manual, speed_rate seen as 9999 means it is missing.
        # Or it is just a typo at the METAR. Let's just delete them...
        base_data['speed'].loc[base_data['speed'] == 9999] = 0

        # Visibility
        # The manual says visibility values of 999999 means they are missing.
        # If CAVOK is Y, it means the visibility is greater than 10000 meters...
        # Also, values of visibility above 10,000m must not be considered as restrictive to the operations,
        # thus, let's just set them as unlimited...
        # Ignoring non significant visibility values (above 9000)
        base_data['visibility'] = base_data['visibility'].astype(int)
        base_data['visibility'].loc[base_data['visibility'] == 999999] = np.nan

        # Ceiling
        # According to the manual, ceiling regarded as 99999 means it's missing (from the METAR)
        # and 22000 means unlimited...
        # BUT... "ceiling values above 1600m (5000ft) are not considered ceiling" Lets just make them NaN...
        base_data['ceiling'] = base_data['ceiling'].astype(int)
        base_data['ceiling'].loc[(base_data['ceiling'] > 1599)] = np.nan

        # Temperature
        # The manual says temperature/dew values above 9999 means they are missing...
        base_data['temperature'].loc[base_data['temperature'] == 9999] = np.nan
        base_data['dew'].loc[base_data['dew'] == 9999] = np.nan

        # Also, values of pressure greater than 1040 and lesser than 980 are absurd.
        # They are probably typos as well so let's get rid of them...
        # base_data['slp'][(base_data['slp'] > 1040) | (base_data['slp'] < 960)] = np.nan

        # Correcting data for standard units
        # Wind direction is in degrees, which is fine...
        # Wind Speed is in meters per second and scaled by 10, let's downscale them and convert to knots...
        base_data['speed'] = base_data['speed'].astype(int) * 0.194384
        base_data['speed'] = base_data['speed'].astype(int)

        # Ceiling is in meters, let's set them to feet

        base_data['ceiling'] = round(base_data['ceiling'] * 3.28084)

        # Visibility is in meters, which is fine...

        # Temperature and dew are scaled by 10, let's downscale them...
        base_data['temperature'] = base_data['temperature'].astype(int) / 10
        base_data['temperature'] = base_data['temperature'].astype(int)
        base_data['dew'] = base_data['dew'].astype(int) / 10
        base_data['dew'] = base_data['dew'].astype(int)

        # Pressure is in Hectopascal, which is fine...

        # Create a column for relative humidity using a previously defined function
        base_data['rh'] = self.calculate_rh(base_data['temperature'], base_data['dew'])
        base_data['rh'] = base_data['rh'].astype(int)

        base_data.replace(to_replace=[99999], value=np.nan, inplace=True)
        
        return base_data
