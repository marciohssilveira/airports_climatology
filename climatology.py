import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


def fix_wx_names(data):
    # Wx
    # A csv file with all phenomenon codes was created using the ISD manual
    # Then they were put in a dict and then replaced in the rows
    codes = pd.read_csv('./data/input/wx_codes.csv', sep=';', index_col=False)
    codes_dict = codes['Phenomenon'].to_dict()
    phenomena = data.filter(like='phenomenon').fillna(0)
    data[phenomena.columns] = phenomena.replace(codes_dict)
    return data


def plot_wx(data, office, airport):
    data = fix_wx_names(data)
    data.index = pd.to_datetime(data['DATE'])
    data['month'] = data.index.month
    data['hour'] = data.index.hour
    phenomena = sorted(set(data['phenomenon_1']))
    output_path = f'./data/output/{office}/{airport}'
    Path(output_path).mkdir(parents=True, exist_ok=True)
    for wx in phenomena:
        filename = f'{output_path}/wx_{wx}_{airport}_2011-2019.png'
        if not os.path.exists(filename):
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
            plt.savefig(filename)
            return fig

