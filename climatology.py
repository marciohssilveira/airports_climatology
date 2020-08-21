import os
from pathlib import Path
import numpy as np
import pandas as pd
import locale
import matplotlib.pyplot as plt
import seaborn as sns
from my_windrose import WindRose
import warnings

warnings.filterwarnings('ignore')
locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')


class Climatology:

    def __init__(self, output_path, data, airport):
        self.output_path = output_path
        self.data = data
        self.airport = airport

    def fix_wx_names(self):
        # Wx
        # A csv file with all phenomenon codes was created using the ISD manual
        # Then they were put in a dict and then replaced in the rows
        codes = pd.read_csv('./data/input/wx_codes.csv', sep=';', index_col=False)
        codes_dict = codes['Phenomenon'].to_dict()
        phenomena = self.data.filter(like='phenomenon').fillna(0)
        self.data[phenomena.columns] = phenomena.replace(codes_dict)
        return self.data

    def plot_variables_climatology(self):
        # Plot boxplots with the variables
        self.data.index = pd.to_datetime(self.data['DATE'])
        self.data['month'] = self.data.index.strftime('%b')
        self.data['ceiling'][(self.data['ceiling'] > 5001)] = np.nan

        data = self.data[['month', 'visibility', 'ceiling', 'temperature', 'dew', 'rh', 'slp']]

        variables = ['Mês', 'Visibilidade (m)', 'Teto (pés)', 'Temperatura do Ar (ºC)',
                     'Ponto de Orvalho (ºC)', 'Umidade Relativa (%)', 'QNH (hPa)']

        data.columns = variables

        for variable in data.columns[1:]:
            fig, ax = plt.subplots()
            fig.set_size_inches((12, 6))
            sns.boxplot(x=data.columns[0], y=variable, data=data, ax=ax)
            plt.title(f'Valores mensais de {variable.split(" (")[0]} em {self.airport} com dados de 2011 a 2019')
            variables_output_path = f'{self.output_path}/variaveis'
            Path(variables_output_path).mkdir(parents=True, exist_ok=True)
            filename = f'{variables_output_path}/{variable.lower().split(" (")[0].replace(" ", "_")}_' \
                       f'{self.airport}_2011-2019.png'
            plt.savefig(filename)

    def plot_wx(self):
        # Plot wx
        data = self.fix_wx_names()
        data.index = pd.to_datetime(data['DATE'])
        data['month'] = data.index.month
        data['hour'] = data.index.hour
        phenomena = sorted(set(data['phenomenon_1']))
        months = data.index.strftime('%b').unique()
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
            ax.set_xticklabels(months)
            plt.yticks(rotation=0)
            ax.set_xlabel('Mês')
            ax.set_ylabel('Hora (UTC)')
            plt.suptitle(f'Frequência de {wx} em {self.airport} com dados de 2011 a 2019')
            phenomena_output_path = f'{self.output_path}/fenomenos significativos'
            Path(phenomena_output_path).mkdir(parents=True, exist_ok=True)
            filename = f'{phenomena_output_path}/wx_{wx}_{self.airport}_2011-2019.png'
            plt.savefig(filename)

    def plot_windrose(self):
        # Plot windrose
        all_time_windrose_output_path = f'{self.output_path}/rosa dos ventos - total'
        Path(all_time_windrose_output_path).mkdir(parents=True, exist_ok=True)
        filename = f'{all_time_windrose_output_path}/windrose_all_time_{self.airport}_2011-2019.png'
        if not os.path.exists(filename):
            windrose = WindRose()
            windrose_data = windrose.create_rosedata(self.data)
            windrose.create_windrose(windrose_data)
            plt.suptitle(f'Rosa dos ventos de {self.airport} com dados de 2011 a 2019')
            plt.savefig(filename)

    def plot_monthly_windrose(self):
        # Create the phenomena frequency for each month
        year = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

        for month_number, month_name in year.items():
            self.data.index = pd.to_datetime(self.data['DATE'])
            data = self.data[self.data.index.month.isin([month_number])]
            try:
                monthly_windrose_output_path = f'{self.output_path}/rosa dos ventos - mensal'
                Path(monthly_windrose_output_path).mkdir(parents=True, exist_ok=True)
                filename = f'{monthly_windrose_output_path}/windrose_monthly_{month_number:02}_{month_name}_{self.airport}_2011-2019.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {self.airport} com dados de 2011 a 2019\n'
                                 f'{month_name.upper()}')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue

    def plot_hourly_windrose(self):
        for hour in range(0, 24, 1):
            self.data.index = pd.to_datetime(self.data['DATE'])
            data = self.data[self.data.index.hour.isin([hour])]
            try:
                hourly_windrose_output_path = f'{self.output_path}/rosa dos ventos - horaria'
                Path(hourly_windrose_output_path).mkdir(parents=True, exist_ok=True)
                filename = f'{hourly_windrose_output_path}/windrose_hourly_{hour:02}00UTC_{self.airport}_2011-2019.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {self.airport} com dados de 2011 a 2019'
                                 f'\n{hour:02}00 UTC')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue
