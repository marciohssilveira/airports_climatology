import os
from pathlib import Path
import pandas as pd
import locale
from climatology import Climatology
import warnings

warnings.filterwarnings('ignore')

locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

# Define where the script will find the files
INPUT_PATH = './src/data/ready'  # Files ready to be used
OUTPUT_PATH = f'./src/plots'  # Directory where the plots will be stored
start_year = 2011
end_year = 2020

# Access folder for each airport grouped in airports.txt
base_data = {}
for file in os.listdir(INPUT_PATH):
    # Read the directory with the ready files and store them in a dictionary for future use
    if not file.startswith('.'):
        airport = f'{file.split("_")[0]}'
        df = pd.read_csv(f'{INPUT_PATH}/{file}', engine='python')
        df.index = pd.to_datetime(df['DATE'])
        airport_path = f'{OUTPUT_PATH}/{airport}'
        Path(airport_path).mkdir(parents=True, exist_ok=True)
        # Instantiate Climatology Class with the parameters
        plot_climatology = Climatology(airport_path, df, airport, start_year, end_year)
        # Plot all time boxplots with the variables
        plot_climatology.plot_variables_climatology()
        # Plot wx
        plot_climatology.plot_wx()
        # Plot all time windroses
        plot_climatology.plot_windrose()
        # Plot monthly windroses
        plot_climatology.plot_monthly_windrose()
        # Plot hourly windroses
        plot_climatology.plot_hourly_windrose()