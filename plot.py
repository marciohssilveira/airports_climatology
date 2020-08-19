import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from my_windrose import WindRose
import warnings

warnings.filterwarnings('ignore')

offices = ['cma_gr', 'cma_gl']


def fix_wx_names(data):
    # Wx
    # A csv file with all phenomenon codes was created using the ISD manual
    # Then they were put in a dict and then replaced in the rows
    codes = pd.read_csv('./data/input/wx_codes.csv', sep=';', index_col=False)
    codes_dict = codes['Phenomenon'].to_dict()
    phenomena = data.filter(like='phenomenon').fillna(0)
    data[phenomena.columns] = phenomena.replace(codes_dict)
    return data


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
        output_path = f'./data/output/{office}/{airport}'
        Path(output_path).mkdir(parents=True, exist_ok=True)
        filename = f'{output_path}/windrose_00_{airport}_2011-2019.png'
        if not os.path.exists(filename):
            windrose = WindRose()
            windrose_data = windrose.create_rosedata(data)
            windrose.create_windrose(windrose_data)
            plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019')
            plt.savefig(filename)
        # Plot wx
        data = fix_wx_names(data)
        data.index = pd.to_datetime(data['DATE'])
        data['month'] = data.index.month
        data['hour'] = data.index.hour
        phenomena = sorted(set(data['phenomenon_1']))
        output_path = f'./data/output/{office}/{airport}'
        Path(output_path).mkdir(parents=True, exist_ok=True)
        for wx in phenomena:
            filtered_data = data[data['phenomenon_1'] == wx]
            fig, ax = plt.subplots(figsize=(10, 8))
            heatmap_data = pd.pivot_table(filtered_data,
                                          index='hour',
                                          columns='month',
                                          values='phenomenon_1',
                                          fill_value=0,
                                          aggfunc='count').reindex(sorted(data['hour'].unique()),
                                                                   columns=data['month'].unique(), fill_value=0)
            sns.heatmap(heatmap_data, cmap='Blues')
            xlabels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            ax.set_xticklabels(xlabels)
            plt.yticks(rotation=0)
            ax.set_xlabel('Mês')
            ax.set_ylabel('Hora (UTC)')
            plt.suptitle(f'Frequência de {wx} em {airport} com dados de 2011 a 2019')
            filename = f'{output_path}/wx_{wx}_{airport}_2011-2019.png'
            plt.savefig(filename)

        # Create the phenomena frequency for each month
        year = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

        for month_number, month_name in year.items():
            data.index = pd.to_datetime(data['DATE'])
            data = data[data.index.month.isin([month_number])]
            try:
                # Plot Windrose
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                filename = f'{output_path}/windrose_{month_number:02}_{month_name}_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019\n'
                                 f'{month_name.upper()}')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue

        for hour in range(0, 24, 1):
            data.index = pd.to_datetime(data['DATE'])
            data = data[data.index.hour.isin([hour])]
            try:
                output_path = f'./data/output/{office}/{airport}'
                Path(output_path).mkdir(parents=True, exist_ok=True)
                filename = f'{output_path}/windrose_{hour:02}00UTC_{airport}_2011-2019.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {airport} com dados de 2011 a 2019'
                                 f'\n{hour:02}00 UTC')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue
