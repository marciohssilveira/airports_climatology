import pandas as pd
import numpy as np

list_gr = ['SBGR', 'SBCR', 'SBPP', 'SBCY', 'SBPJ', 'SBBR', 'SBGO', 'SBKP', 'SBPO', 'SSGG', 'SBTD',
           'SBCA', 'SBMG', 'SBLO', 'SBDB', 'SBDO', 'SBTG', 'SBRD', 'SBBW', 'SNBR', 'SWLC', 'SBCN', 'SBMK', 'SBUL',
           'SBUR', 'SBAX', 'SBVG', 'SBBH', 'SBSR', 'SBAQ', 'SBAU', 'SBDN', 'SBML', 'SBBU', 'SBAE', 'SBBP',
           'SBJD', 'SBJH', 'SDCO', 'SBMT', 'SBSP']

list_gl = ['SBGL', 'SBAR', 'SBFZ', 'SBJP', 'SBMO', 'SBRF', 'SBSG', 'SBPL', 'SBVT', 'SBBV', 'SBEG',
           'SBPV', 'SBTT', 'SBCZ', 'SBBE', 'SBMQ', 'SBSN', 'SBSL', 'SBIP', 'SBAT', 'SBCP', 'SBES', 'SBJR',
           'SBRJ', 'SBST', 'SBTA', 'SBZM', 'SBIL', 'SBFN', 'SBJU', 'SBNT', 'SBPB', 'SBTE', 'SBGV',
           'SBMS', 'SBVC', 'SBJE', 'SBAC', 'SNTF', 'SDIY', 'SNVB', 'SBIH', 'SBMY', 'SBRB', 'SBSO', 'SBTF',
           'SBUA', 'SBCJ', 'SBHT', 'SBMA', 'SBOI', 'SBCI', 'SBIZ', 'SBTB', 'SBSI', 'SBJI']

br_airports_list = list_gl + list_gr

isd_stations = pd.read_csv('isd_all_stations.csv')

br_airports = isd_stations[isd_stations['ICAO'].isin(br_airports_list)].sort_values(by='END',
                                                                                    ascending=True)

br_airports = br_airports.iloc[6:]

br_airports.to_csv('isd_br_stations.csv', index=False)
