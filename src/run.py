import os
import sys
src_dir = os.path.join(os.getcwd(), '..', 'src')
sys.path.append(src_dir)

from d01_data.get_data import GetIsdData
from d03_visualisation.plot_climatology import Climatology
import pandas as pd


airport = 'SBGR'


data = GetIsdData(airport).download_isd_data()

climatology = Climatology(data, airport)
climatology.plot_variables_climatology()
# Plot wx
climatology.plot_wx()
# Plot all time windroses
climatology.plot_windrose()
# Plot monthly windroses
climatology.plot_monthly_windrose()
# Plot hourly windroses
climatology.plot_hourly_windrose()
print('Done!')