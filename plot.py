import sys
sys.path.append('./src')
import os
from pathlib import Path
import pandas as pd
import locale
import warnings
from climatology import Climatology

warnings.filterwarnings('ignore')
locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
start_year = 2011
end_year = 2020
# offices = ['cma_gr', 'cma_gl']
offices = ['example']

for office in offices:
    INPUT_PATH = f'./data/input/isd/ready/{office}'
    base_data = {}
    for file in os.listdir(INPUT_PATH):
        if not file.startswith('.'):
            airport = f'{file.split("_")[0]}'
            df = pd.read_csv(f'{INPUT_PATH}/{file}')
            df.index = pd.to_datetime(df['DATE'])
            base_data[airport] = df

    for airport, data in base_data.items():
        OUTPUT_PATH = f'./data/output/{office}/{airport}'
        Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
        # Instantiate Climatology Class with the parameters
        plot_climatology = Climatology(OUTPUT_PATH, data, airport, start_year, end_year)
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