import datetime
import warnings
from d01_data.get_data import GetIsdData
from d02_processing.calculate_windrose import WindRose
import seaborn as sns
import matplotlib.pyplot as plt
import locale
import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

warnings.filterwarnings('ignore')
locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')


class Climatology:

    def __init__(self, data, icao):
        self.data = data
        self.station_icao = icao
        self.output_path = f'data/03_img_output/{self.station_icao}'
        self.end_year = datetime.datetime.today().year - 1
        self.start_year = datetime.datetime.today().year - 10

    def fix_wx_names(self):
        # Wx
        # A csv file with all phenomenon codes was created using the ISD manual
        # Then they were put in a dict and then replaced in the rows
        codes = pd.read_csv('data/01_raw/wx_codes.csv',
                            sep=';', index_col=False)
        codes_dict = codes['Phenomenon'].to_dict()
        self.data['phenomenon'] = self.data['phenomenon'].fillna(
            0).astype(int).map(codes_dict)
        return self.data

    def plot_variables_climatology(self):
        # Filter data to remove outliers (caused mostly by typos)
        self.data[self.data['ceiling'] > 5001]['ceiling'] = np.nan
        self.data[self.data['slp'] > 1040]['slp'] = np.nan
        self.data[self.data['slp'] < 960]['slp'] = np.nan
        self.data[self.data['visibility'] >= 9998]['visibility'] = np.nan

        # Plot boxplots with the variables
        self.data['month'] = self.data.index.strftime('%b')

        data = self.data[['month', 'visibility', 'ceiling',
                          'temperature', 'dew', 'rh', 'slp']]

        variables = ['Mês',
                     'Visibilidade (< 10.000 m)',
                     'Teto (pés)',
                     'Temperatura do Ar (ºC)',
                     'Ponto de Orvalho (ºC)',
                     'Umidade Relativa (%)',
                     'QNH (hPa)']

        data.columns = variables

        print('Plotting variables climatology.')

        for variable in data.columns[1:]:
            fig, ax = plt.subplots()
            fig.set_size_inches((12, 6))
            sns.boxplot(x=data.columns[0], y=variable, data=data, ax=ax)
            plt.title(f'Valores mensais de {variable.split(" (")[0]} em {self.station_icao} '
                      f'com dados de {self.start_year} a {self.end_year}')
            variables_output_path = f'{self.output_path}/variaveis'
            Path(variables_output_path).mkdir(parents=True, exist_ok=True)
            filename = f'{variables_output_path}/{variable.lower().split(" (")[0].replace(" ", "_")}_' \
                       f'{self.station_icao}_{self.start_year}-{self.end_year}.png'
            plt.savefig(filename)
        
        print(f'Images stored in {variables_output_path}.')

    def plot_wx(self):
        # Plot wx
        self.data = self.fix_wx_names()
        self.data['month'] = self.data.index.month
        self.data['hour'] = self.data.index.hour
        phenomena = sorted(set(self.data['phenomenon']))
        months = self.data.index.strftime('%b').unique()
        
        print('Plotting phenomena climatology.')

        for wx in phenomena:
            filtered_data = self.data[self.data['phenomenon'] == wx]
            fig, ax = plt.subplots(figsize=(10, 8))
            heatmap_data = pd.pivot_table(filtered_data,
                                          index='hour',
                                          columns='month',
                                          values='phenomenon',
                                          fill_value=0,
                                          aggfunc='count').reindex(sorted(self.data['hour'].unique()),
                                                                   columns=self.data['month'].unique(), fill_value=0)
            sns.heatmap(heatmap_data, cmap='Blues')
            ax.set_xticklabels(months)
            plt.yticks(rotation=0)
            ax.set_xlabel('Mês')
            ax.set_ylabel('Hora (UTC)')
            plt.suptitle(
                f'Frequência de {wx} em {self.station_icao} com dados de {self.start_year} a {self.end_year}')
            phenomena_output_path = f'{self.output_path}/fenomenos_significativos'
            Path(phenomena_output_path).mkdir(parents=True, exist_ok=True)
            filename = f'{phenomena_output_path}/wx_{wx}_{self.station_icao}_2011-2019.png'
            plt.savefig(filename)

        print(f'Phenomena climatology stored in {phenomena_output_path}.')

    def plot_windrose(self):
        # Plot windrose
        print('Plotting all time windroses.')
        all_time_windrose_output_path = f'{self.output_path}/rosa_dos_ventos_total'
        Path(all_time_windrose_output_path).mkdir(parents=True, exist_ok=True)
        filename = f'{all_time_windrose_output_path}/windrose_all_time_' \
            f'{self.station_icao}_{self.start_year}-{self.end_year}.png'
        if not os.path.exists(filename):
            windrose = WindRose()
            windrose_data = windrose.create_rosedata(self.data)
            windrose.create_windrose(windrose_data)
            plt.suptitle(
                f'Rosa dos ventos de {self.station_icao} com dados de {self.start_year} a {self.end_year}')
            plt.savefig(filename)

        print(f'Images stored in {all_time_windrose_output_path}.')

    def plot_monthly_windrose(self):
        # Create the phenomena frequency for each month
        print('Plotting monthly windroses.')
        year = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

        for month_number, month_name in year.items():
            data = self.data[self.data.index.month.isin([month_number])]
            try:
                monthly_windrose_output_path = f'{self.output_path}/rosa_dos_ventos_mensal'
                Path(monthly_windrose_output_path).mkdir(
                    parents=True, exist_ok=True)
                filename = f'{monthly_windrose_output_path}/windrose_monthly_{month_number:02}_{month_name}_' \
                           f'{self.station_icao}_{self.start_year}-{self.end_year}.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {self.station_icao} com dados de {self.start_year} a {self.end_year}\n'
                                 f'{month_name.upper()}')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError, TypeError):
                continue
        print(f'Images stored in {monthly_windrose_output_path}.')

    def plot_hourly_windrose(self):
        print('Plotting hourly windroses.')
        for hour in range(0, 24, 1):
            data = self.data[self.data.index.hour.isin([hour])]
            try:
                hourly_windrose_output_path = f'{self.output_path}/rosa_dos_ventos_horaria'
                Path(hourly_windrose_output_path).mkdir(
                    parents=True, exist_ok=True)
                filename = f'{hourly_windrose_output_path}/windrose_hourly_{hour:02}00UTC_' \
                           f'{self.station_icao}_{self.start_year}-{self.end_year}.png'
                if not os.path.exists(filename):
                    windrose = WindRose()
                    windrose_data = windrose.create_rosedata(data)
                    windrose.create_windrose(windrose_data)
                    plt.suptitle(f'Rosa dos ventos de {self.station_icao} com dados de {self.start_year} a {self.end_year}'
                                 f'\n{hour:02}00 UTC')
                    plt.savefig(filename)
            except (ValueError, ZeroDivisionError):
                continue
        
        print(f'Images stored in {hourly_windrose_output_path}.')