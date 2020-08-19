import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class Climatology:

    def __init__(self):
        self.wx_codes_path = './data/input/wx_codes.csv'

    def fix_wx_names(self, data):
        # Wx
        # A csv file with all phenomenon codes was created using the ISD manual
        # Then they were put in a dict and then replaced in the rows
        codes = pd.read_csv(self.wx_codes_path, sep=';', index_col=False)
        codes_dict = codes['Phenomenon'].to_dict()
        phenomena = data.filter(like='phenomenon').fillna(0)
        data[phenomena.columns] = phenomena.replace(codes_dict)
        return data

    def plot_phenomena(self, fixed_data, palette=None):
        # Filter CAVOK data
        cavok = fixed_data['phenomenon_1'].isin(['CAVOK'])
        cavok_data = fixed_data['phenomenon_1'].loc[cavok]
        non_cavok_data = fixed_data.loc[~cavok]
        # Plot countplot
        if palette is None:
            palette = sns.color_palette('coolwarm', n_colors=non_cavok_data.shape[1])
        total = float(len(fixed_data))
        total_cavok = float(len(cavok_data))
        fig, ax = plt.subplots(figsize=(8, 6))
        fig = sns.countplot(data=non_cavok_data,
                            x='phenomenon_1',
                            order=non_cavok_data['phenomenon_1'].value_counts().index,
                            color=palette[0])
        ax.set(xlabel='Fenômeno', ylabel='Número de ocorrências')
        # Plotting the CAVOk information in the top right position
        position = fig.patches
        x_position = position[-1].get_x()
        y_position = position[0].get_height()
        ax.text(x_position, y_position,
                f'Sem fenômeno: {(total_cavok / total) * 100:.2f}%',
                horizontalalignment='right',
                verticalalignment='top')
        # Plotting percentages on the bars
        for p in fig.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2.,
                    height + 0.3,
                    f'{(height / total) * 100:.2f}%',
                    ha="center")
        return fig
