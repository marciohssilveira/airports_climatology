import os
from pathlib import Path
import pandas as pd
import locale
import warnings
from climatology import Climatology

warnings.filterwarnings('ignore')
locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

offices = ['cma_gr', 'cma_gl']

for office in offices:
    input_path = f'./data/input/isd/ready/{office}'
    base_data = {}
    for file in os.listdir(input_path):
        if not file.startswith('.'):
            airport = f'{file.split("_")[0]}'
            df = pd.read_csv(f'{input_path}/{file}')
            base_data[airport] = df

    for airport, data in base_data.items():
        output_path = f'./data/output/{office}/{airport}'
        Path(output_path).mkdir(parents=True, exist_ok=True)
        # Instantiate Climatology Class with the parameters
        plot_climatology = Climatology(output_path, data, airport)
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