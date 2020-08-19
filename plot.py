import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from my_windrose import WindRose
from climatology import Climatology
import warnings

warnings.filterwarnings('ignore')

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
        # Plot windrose
        windrose = WindRose()
        windrose_data = windrose.create_rosedata(data)
        windrose.create_windrose(windrose_data)
        output_path = f'./data/output/{office}/{airport}'
        Path(output_path).mkdir(parents=True, exist_ok=True)
        plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019')
        filename = f'{output_path}/windrose_00_{airport}_2011-2019.png'
        if not os.path.exists(filename):
            plt.savefig(filename)
        # Plot wx
        wx = Climatology()
        fixed_data = wx.fix_wx_names(data)
        wx.plot_phenomena(fixed_data)
        output_path = f'./data/output/{office}/{airport}'
        Path(output_path).mkdir(parents=True, exist_ok=True)
        plt.suptitle(f'Frequência de fenômenos significativos em {airport} com dados de 2011 a 2019')
        filename = f'{output_path}/wx_00_{airport}_2011-2019.png'
        if not os.path.exists(filename):
            plt.savefig(filename)

    # Create the phenomena frequency for each month
    year = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    for month_number, month_name in year.items():
        for airport, data in base_data.items():
            data.index = pd.to_datetime(data['DATE'])
            data = data[data.index.month.isin([month_number])]
            try:
                # Plot Windrose
                windrose = WindRose()
                windrose_data = windrose.create_rosedata(data)
                windrose.create_windrose(windrose_data)
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019\n'
                             f'{month_name.upper()}')
                filename = f'{output_path}/windrose_{month_number:02}_{month_name}_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    plt.savefig(filename)
                # Plot wx
                wx = Climatology()
                fixed_data = wx.fix_wx_names(data)
                wx.plot_phenomena(fixed_data)
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                plt.suptitle(
                    f'Frequência de fenômenos significativos em {airport} com dados de 2011 a 2019\n'
                    f'{month_name.upper()}')
                filename = f'{output_path}/wx_{month_number:02}_{month_name}_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue

    for hour in range(1, 24, 1):
        for airport, data in base_data.items():
            data.index = pd.to_datetime(data['DATE'])
            data = data[data.index.hour.isin([hour])]
            try:
                windrose = WindRose()
                windrose_data = windrose.create_rosedata(data)
                windrose.create_windrose(windrose_data)
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019'
                             f'\n{hour:02}00 UTC')
                filename = f'{output_path}/windrose_{hour:02}00UTC_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    plt.savefig(filename)
                # Plot wx
                wx = Climatology()
                fixed_data = wx.fix_wx_names(data)
                wx.plot_phenomena(fixed_data)
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                plt.suptitle(f'Frequência de fenômenos significativos em {airport} com dados de 2011 a 2019'
                             f'\n{hour:02}00 UTC')
                filename = f'{output_path}/wx_{hour:02}00UTC_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue
