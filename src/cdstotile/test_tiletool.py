# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021
#
import math
import datetime
import os.path
import json
import numpy
import netCDF4

import hwxpo
from generate_HWITW_statistics import *
from data_settings import data_settings

# a helper class for printing color text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


APP_VERSION = "0.50"
current_time = datetime.datetime.now()

def flatten_cds(ds):
    flattened_array = ds[0:HOURS_PER_YEAR,0,0] #Truncate, pulling out the first dimension, since lat & lon are constant
    return numpy.ma.resize(flattened_array, HOURS_PER_YEAR) #Make sure it's the right length - the last year won't be.

def load_netcdfs( dir_name, start_year, end_year, area_lat_long ):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    grid_num = CalcQtrDegGridNum( area_lat_long )

    # the variables we are interested, long name and short name.
    # short name is used inside the netcdf files
    CDSVAR_U10 = ['10m_u_component_of_wind', 'u10']
    CDSVAR_V10 = ['10m_v_component_of_wind', 'v10']
    CDSVAR_D2M = ['2m_dewpoint_temperature', 'd2m']
    CDSVAR_T2M = ['2m_temperature', 't2m']
    CDSVAR_CBH = ['cloud_base_height', 'cbh']
    CDSVAR_PTYPE = ['precipitation_type', 'ptype']
    CDSVAR_TCC = ['total_cloud_cover', 'tcc']
    CDSVAR_TP = ['total_precipitation', 'tp']

    years = list( range( start_year, end_year + 1 ) )

    for year in years:

        path = f'./{dir_name}/{year}/'

        #Process temperature and dewpoint
        temp_dp_files = [CDSVAR_T2M, CDSVAR_D2M] #They will remain in this order, Temp then Dewpoint, throughout
        raw_temp_dp_data = numpy.zeros((2,HOURS_PER_YEAR), dtype = numpy.float32) 
        for i,filename in enumerate([f'{path}gn{grid_num}-{year}-{var[0]}.nc' for var in temp_dp_files]):
            already_exists = os.path.isfile( filename ) #and os.path.getsize( fullname ) > 500
            if not already_exists:
                print( bcolors.WARNING + f'{filename} is missing!' + bcolors.ENDC )
                continue
            print( f'processing {filename}' )
            try:
                ds = netCDF4.Dataset( filename )
            except OSError:
                print( bcolors.FAIL + f'{filename} could not be opened!' + bcolors.ENDC )
                exit(-1)
            raw_temp_dp_data[i] = flatten_cds(ds[temp_dp_files[i][1]])
        temp_results = do_temp_dp(raw_temp_dp_data, area_lat_long[1])
        for variable,variable_info in temp_results.items():
            for stat,value_array in variable_info.items():
                data_settings['variables'][variable][stat]['data'].append(value_array.tolist()) #Currently no protection against mis-ordered years

def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num
    
##########################################################
# main

print( f'** HWITW tile tool v{APP_VERSION} **\n')

# inp_lat = 59.64 # homer ak
# inp_long = -151.54
# -141.0838,60.178 - Taan Fiord
#inp_lat = 60.178
#inp_long = -141.0838
#-69.195, -12.583 - Puerto Maldonado
inp_lat = -12.583
inp_long = -69.195

# todo Zoom level 11 tile number
# get the containing cell 
lat0 = math.ceil( inp_lat * 4 ) / 4
lat1 = (math.floor( inp_lat * 4 ) / 4) #+ 0.01 # edge is not inclusive
long0 = math.floor( inp_long * 4 ) / 4
long1 = (math.ceil( inp_long * 4 ) / 4) #- 0.01

area0 = [ lat0, long0, lat1, long1 ]

# era5 back extension goes from 1950 to 1978
load_netcdfs(   'cds_era5_backext',
                1950, 1978,
                area0 )

# era5 goes from 1979 to present
load_netcdfs(   'cds_era5',
                1979, current_time.year,
                area0 )

# dump json
gnum = CalcQtrDegGridNum( area0 )
outname = f'gn{gnum}-hwxpo.json'
print( f'Output {outname}' )
with open( outname, 'w') as outfile:
    json.dump( data_settings, outfile )
