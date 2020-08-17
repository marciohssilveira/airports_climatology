import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


def fix_wx_names(data, wx_codes_path):
    # Wx
    # A csv file with all phenomenon codes was created using the ISD manual
    # Then they were put in a dict and then replaced in the rows
    codes = pd.read_csv(wx_codes_path, sep=';', index_col=False)
    codes_dict = codes['Phenomenon'].to_dict()
    phenomena = data.filter(like='phenomenon').fillna(0)
    data[phenomena.columns] = phenomena.replace(codes_dict)
    return data


# Reading files into a Pandas Data Frame
airport = 'SBBR'
data = pd.read_csv(f'./data/isd/ready/{airport}_isd_data.csv', index_col='DATE')

# Appying a function to fix wx codes
wx_codes_path = './data/input/wx_codes.csv'
data = fix_wx_names(data, wx_codes_path)


# Filter CAVOK data
cavok = data['phenomenon_1'].isin(['CAVOK'])
data = data.loc[~cavok]

# Plot countplot
sns.countplot(data=data, x='phenomenon_1')
plt.show()

# Create functions for temperature, humidity, phenomena, etc.




# Use it
ready_data_path = './data/isd/ready'
img_path = './data/output'
files = []
for file in os.listdir(ready_data_path):
    if not file.startswith('.'):
        files.append(file)

files = sorted(files)

# Create the windroses for the entire period of the data
for i in range(len(files)):
    # Read into a Pandas dataframe all the i files inside the defined PATH
    airport = pd.read_csv(f'{ready_data_path}/{files[i]}')
    # Determine the relative percentage of observation in each speed and direction bin
    directions = np.arange(0, 360, 15)
    airport_name = f'{files[i].split("_")[0]}'
    print(f'Creating windrose for {airport_name}')
    rose_data = create_rosedata(airport)  # <------------------ PUT NEW FUNCTIONS HERE
    fig = wind_rose(rose_data, directions)   # <------------------ PUT NEW FUNCTIONS HERE
    plt.suptitle(f'Rosa dos ventos de {airport_name} com dados de 2011 a 2019')
    Path(f'{img_path}/{airport_name}').mkdir(parents=True, exist_ok=True)
    filename = f'{img_path}/{airport_name}/00_{airport_name}_2011-2019.png'
    if not os.path.exists(filename):
        plt.savefig(filename)

# Create the windrose for each month
year = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

for month_number, month_name in year.items():
    for i in range(len(files)):
        # Read into a Pandas dataframe all the i files inside the defined PATH
        airport = pd.read_csv(f'{ready_data_path}/{files[i]}')
        # Filter the specific month given the year dict
        airport.index = pd.to_datetime(airport['DATE'])
        airport = airport[airport.index.month.isin([month_number])]
        # Determine the relative percentage of observation in each speed and direction bin
        directions = np.arange(0, 360, 15)
        airport_name = f'{files[i].split("_")[0]}'
        print(f'Creating {month_name.upper()} windrose for {airport_name}')
        rose_data = create_rosedata(airport)   # <------------------ PUT NEW FUNCTIONS HERE
        fig = wind_rose(rose_data, directions)    # <------------------ PUT NEW FUNCTIONS HERE
        plt.suptitle(f'Rosa dos ventos de {airport_name} com dados de 2011 a 2019 \n {month_name.upper()}')
        Path(f'{img_path}/{airport_name}').mkdir(parents=True, exist_ok=True)
        filename = f'{img_path}/{airport_name}/{month_number:02}_{airport_name}_2011-2019_{month_name}.png'
        if not os.path.exists(filename):
            plt.savefig(filename)


# Create the windrose for each time of the day
for hour in range(1, 24, 1):
    for i in range(len(files)):
        # Read into a Pandas dataframe all the i files inside the defined PATH
        airport = pd.read_csv(f'{ready_data_path}/{files[i]}')
        # Filter the specific month given the year dict
        airport.index = pd.to_datetime(airport['DATE'])
        airport = airport[airport.index.hour.isin([hour])]
        # Determine the relative percentage of observation in each speed and direction bin
        directions = np.arange(0, 360, 15)
        airport_name = f'{files[i].split("_")[0]}'
        print(f'Creating {hour} UTC windrose for {airport_name}')
        rose_data = create_rosedata(airport)    # <------------------ PUT NEW FUNCTIONS HERE
        fig = wind_rose(rose_data, directions)    # <------------------ PUT NEW FUNCTIONS HERE
        plt.suptitle(f'Rosa dos ventos de {airport_name} com dados de 2011 a 2019 \n {hour:02} UTC')
        Path(f'{img_path}/{airport_name}').mkdir(parents=True, exist_ok=True)
        filename = f'{img_path}/{airport_name}/{airport_name}_2011-2019_{hour:02} UTC.png'
        if not os.path.exists(filename):
            plt.savefig(filename)