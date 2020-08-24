import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')


class WindRose:

    def __init__(self):
        self.directions = np.arange(0, 360, 15)

    # Define a function that will give us nice labels for a wind speed range
    # E.g., 5 - 10 knots
    def speed_labels(self, bins, units):
        labels = []
        for left, right in zip(bins[:-1], bins[1:]):
            if left == bins[0]:
                labels.append('calm'.format(right))
            elif np.isinf(right):
                labels.append(f'>{left} {units}')
            else:
                labels.append(f'{left} - {right} {units}')

        return labels

    # Define a function to convert centered angles to left-edge radians
    def _convert_dir(self):
        N = self.directions.shape[0]
        barDir = np.deg2rad(self.directions)
        barWidth = 2 * np.pi / N
        return barDir, barWidth

    def create_rosedata(self, data):
        """
        Determine the relative percentage of observation in each speed and direction bin
        Here's how we do it:
        -assign a speed bin for each row with pandas.cut
        -assign a direction bin for each row (again, pandas.cut)
        -unify the 360° and 0° bins under the 0° label
        -group the data simultaneously on both speed and direction bins
        -compute the size of each group
        -unstack (pivot) the speed bins into columns
        -fill missing values with 0
        -assign a "calm" column to be the total number of calm observations evenly distributed across all directions
        -sort the columns -- they are a catgorical index, so "calm" will be first (this is awesome!)
        -convert all of the counts to percentages of the total number of observations
            """
        # Define our bins and labels for speed and wind
        spd_bins = [-1, 0, 5, 10, 15, 20, 25, 30, np.inf]
        spd_labels = self.speed_labels(spd_bins, units='nós')

        dir_bins = np.arange(-7.5, 370, 15)
        dir_labels = (dir_bins[:-1] + dir_bins[1:]) / 2

        # Determine the total number of observations and how many have calm conditions
        total_count = data.shape[0]
        calm_count = data[data['speed'] == 0].shape[0]

        rose = (
            data.assign(
                Spd_bins=pd.cut(
                    data['speed'], bins=spd_bins, labels=spd_labels, right=True
                )
            )
                .assign(
                Dir_bins=pd.cut(
                    data['direction'], bins=dir_bins, labels=dir_labels, right=False
                )
            )
                .replace({"Dir_bins": {360: 0}})
                .groupby(by=["Spd_bins", "Dir_bins"])
                .size()
                .unstack(level="Spd_bins")
                .fillna(0)
                .assign(calm=lambda df: calm_count / df.shape[0])
                .sort_index(axis=1)
                .applymap(lambda x: x / total_count * 100)
        )
        directions = np.arange(0, 360, 15)
        for i in directions:
            if i not in rose.index:
                rose = rose.reindex(rose.index.values.tolist() + [i])

        rose = rose.sort_index().fillna(0)
        return rose

    # Define our wind rose function
    def create_windrose(self, windrose_data, palette=None):
        if palette is None:
            palette = sns.color_palette('coolwarm', n_colors=windrose_data.shape[1])

        bar_dir, bar_width = self._convert_dir()

        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        ax.set_theta_direction('clockwise')
        ax.set_theta_zero_location('N')

        for n, (c1, c2) in enumerate(zip(windrose_data.columns[:-1], windrose_data.columns[1:])):
            if n == 0:
                # first column only
                ax.bar(bar_dir, windrose_data[c1].values,
                       width=bar_width,
                       color=palette[0],
                       edgecolor='none',
                       label=c1,
                       linewidth=0)

            # all other columns
            ax.bar(bar_dir, windrose_data[c2].values,
                   width=bar_width,
                   bottom=windrose_data.cumsum(axis=1)[c1].values,
                   color=palette[n + 1],
                   edgecolor='none',
                   label=c2,
                   linewidth=0)

        ax.legend(loc=(1, 0), ncol=1)
        ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

        return fig
