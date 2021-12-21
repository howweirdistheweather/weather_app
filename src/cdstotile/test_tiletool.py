# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021
#
import math
import datetime
import time
import os.path
import json
import numpy
import netCDF4
import random
import copy

import hwxpo
from generate_HWITW_stats import (
    do_temp_dp,
    do_wind,
    do_precip,
    do_cloud_cover,
    do_cloud_ceiling,
    HOURS_PER_WEEK,
    HOURS_PER_YEAR,
    WEEKS_PER_YEAR
)
from data_settings import data_settings
from hig_utils import pretty_duration
from hig_csv import write_csv_from_dict_of_lists

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
    return flattened_array.flatten() #May be too short - current year doesn't have enough hours. Without .flatten() it's an array of 1-element arrays

def flatten_cds_2021(ds): #This is very slow. Is there any more efficient way to detect the break between the two expver columns?
    #This hunts for nulls, and if there's a null checks for a real value in the other expver column. Very slow.
    flattened_array = numpy.full((HOURS_PER_YEAR),-32767 , dtype = numpy.float32)#Start out with an array of Nulls (-32767)
    try:
        for i in range(HOURS_PER_YEAR):
            value = ds[i,0,0,0]
            if value > -32767: flattened_array[i] = value
            else:
                flattened_array[i] = ds[i,1,0,0]
    except IndexError: pass #We ran out of input arrays, so we're done.
    return flattened_array

def export_cds_to_csv(ds,name):
    out_array = ds[0:,0,0]
    numpy.savetxt(f"{name}.csv",out_array,delimiter=',')

def initialize_results(first_week_results):
    #This is passed a data structure with a single week of results - populate the first value in relevant arrays.
    results_dict = {}
    for variable, stats in first_week_results.items():
        results_dict.update([(variable,{})])
        for stat, first_value in stats.items():
            results_dict[variable].update([(stat,numpy.zeros(WEEKS_PER_YEAR, dtype=int))])
            results_dict[variable][stat][0] = first_value
    return results_dict

def load_netcdfs(out_data, dir_name, start_year, end_year, area_lat_long ):
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

    process_settings = [
        {'data_group': 'temperature and humidity', 'files': [CDSVAR_T2M, CDSVAR_D2M], 'analyze': do_temp_dp, 'analysis_kwargs': {'lon': area_lat_long[1]}},
        {'data_group': 'wind', 'files': [CDSVAR_U10, CDSVAR_V10], 'analyze': do_wind, 'analysis_kwargs': {}},
        {'data_group': 'precipitation', 'files': [CDSVAR_TP, CDSVAR_PTYPE], 'analyze': do_precip, 'analysis_kwargs': {}},
        {'data_group': 'cloud cover', 'files': [CDSVAR_TCC], 'analyze': do_cloud_cover, 'analysis_kwargs': {}},
#        {'data_group': 'cloud ceiling', 'files': [CDSVAR_CBH], 'analyze': do_cloud_ceiling, 'analysis_kwargs': {}}
    ]

    def process_data(out_data, year, data_group, files, analyze, analysis_kwargs):
        print(f"Analyzing {data_group}")
        raw_data = []
        for i, filename in enumerate([f'{path}gn{grid_num}-{year}-{var[0]}.nc' for var in files]):
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
            if year == 2021: raw_data.append(flatten_cds_2021(ds[files[i][1]])) #Now this is the only divergence between 2021 and other years.
            else: raw_data.append(flatten_cds(ds[files[i][1]]))
        start_time = time.time()
        analysis_function = analyze
        for week in range(WEEKS_PER_YEAR):
            if week == 0:
                start = 0
                end = HOURS_PER_WEEK
                results = initialize_results(analysis_function([data_array[start:end] for data_array in raw_data], **analysis_kwargs))
            else:
                start = week*HOURS_PER_WEEK
                end = (week+1)*HOURS_PER_WEEK
                result = analysis_function([data_array[start:end] for data_array in raw_data], **analysis_kwargs)
                for variable,variable_info in result.items():
                    for stat,value in variable_info.items():
                        results[variable][stat][week] = value
        run_time = time.time()-start_time
        print(f'time to process 1 year (not including loading or storing): {pretty_duration(run_time)}')
        for variable,variable_info in results.items():
            for stat,value_array in variable_info.items():
                out_data['variables'][variable][stat]['data'].append(value_array.tolist()) #Currently no protection against mis-ordered years
        return run_time

    years = list( range( start_year, end_year + 1 ) )

    benchmark_log = dict([(data_group['data_group'],[]) for data_group in process_settings])
    for year in years:
        path = f'./{dir_name}/{year}/'
        for data_group in process_settings:
            benchmark_log[data_group['data_group']].append(process_data(out_data, year, **data_group))
    return benchmark_log

def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num

##########################################################
def export_2021_to_csv(area_lat_long, filename):
    print("Writing csv of 2021 data.")
    CDSVAR_U10 = ['10m_u_component_of_wind', 'u10']
    CDSVAR_V10 = ['10m_v_component_of_wind', 'v10']
    CDSVAR_D2M = ['2m_dewpoint_temperature', 'd2m']
    CDSVAR_T2M = ['2m_temperature', 't2m']
    CDSVAR_CBH = ['cloud_base_height', 'cbh']
    CDSVAR_PTYPE = ['precipitation_type', 'ptype']
    CDSVAR_TCC = ['total_cloud_cover', 'tcc']
    CDSVAR_TP = ['total_precipitation', 'tp']
    all_variables = [CDSVAR_U10, CDSVAR_V10, CDSVAR_D2M, CDSVAR_T2M, CDSVAR_CBH, CDSVAR_PTYPE, CDSVAR_TCC, CDSVAR_TP]
    n_variables = len(all_variables)

    path = './cds_era5/2021/'
    grid_num = CalcQtrDegGridNum(area_lat_long)
    stored_data = numpy.zeros((n_variables, HOURS_PER_YEAR), dtype=numpy.float32)
    for i, filepath in enumerate([f'{path}gn{grid_num}-2021-{var[0]}.nc' for var in all_variables]):
        already_exists = os.path.isfile( filepath ) #and os.path.getsize( fullname ) > 500
        if not already_exists:
            print( bcolors.WARNING + f'{filepath} is missing!' + bcolors.ENDC )
            continue
        print( f'processing {filepath}' )
        try:
            ds = netCDF4.Dataset( filepath )
        except OSError:
            print( bcolors.FAIL + f'{filepath} could not be opened!' + bcolors.ENDC )
            exit(-1)
        export_cds_to_csv(ds[all_variables[i][1]],all_variables[i][0])
        this_array = flatten_cds_2021(ds[all_variables[i][1]])
        print(this_array.shape)
        stored_data[i][0:this_array.size] = this_array
    numpy.savetxt(f"2021_data_{filename}.csv", numpy.swapaxes(stored_data,0,1), delimiter=",")



##########################################################
# main

print( f'** HWITW tile tool v{APP_VERSION} **\n')

site_settings = [
    {"name":"Seldovia", "inp_lat": 59.45, "inp_long":-151.72},
    {"name":"Sterling", "inp_lat":60.54, "inp_long":-150.78},
    {"name":"Plymouth", "inp_lat":41.96, "inp_long":-70.67},
    {"name":"Taan_Fiord", "inp_lat": 60.178, "inp_long":-141.0838},
    {"name":"Puerto_Maldonado", "inp_lat": -12.583, "inp_long":-69.195},
    {"name":"Phoenix", "inp_lat":33.4, "inp_long":-112.1},
    {"name":"Little_Diomede", "inp_lat":65.76, "inp_long":-168.93},
]

# inp_lat = 59.64 # homer ak
# inp_long = -151.54
# -141.0838,60.178 - Taan Fiord
#inp_lat = 60.178
#inp_long = -141.0838
#-69.195, -12.583 - Puerto Maldonado
#inp_lat = -12.583
#inp_long = -69.195
#inp_lat = 59.45 # Seldovia
#inp_long = -151.72

def process_site(out_data, name, inp_lat, inp_long):
    print(f"Processing site {name}.")
    filename = f'{name}.json'
    out_data['data_specs'].update([('Name',name)])
    # todo Zoom level 11 tile number
    # get the containing cell
    lat0 = math.ceil( inp_lat * 4 ) / 4
    lat1 = (math.floor( inp_lat * 4 ) / 4) #+ 0.01 # edge is not inclusive
    long0 = math.floor( inp_long * 4 ) / 4
    long1 = (math.ceil( inp_long * 4 ) / 4) #- 0.01

    area0 = [ lat0, long0, lat1, long1 ]

    # Since 2021 data is weird, let's take a closer look.
    export_2021_to_csv(area0, filename)

    # era5 back extension goes from 1950 to 1978
    log = load_netcdfs( out_data,
                        'cds_era5_backext',
                        1950, 1978,
                        area0 )

    # era5 goes from 1979 to present
    log2 = load_netcdfs(out_data,
                        'cds_era5',
                        1979, current_time.year,
                        area0 )

    #write log of processing time
    for key,time_list in log2.items():
        log[key] += time_list
    write_csv_from_dict_of_lists(f'log_of_processing_times_{name}.csv',log)
    # dump json
    gnum = CalcQtrDegGridNum( area0 )
    #outname = f'gn{gnum}-hwxpo.json'
    outname = filename
    print( f'Output {outname} (gnum={gnum})' )
    with open( outname, 'w') as outfile:
        json.dump( out_data, outfile )

for site in site_settings: process_site(copy.deepcopy(data_settings), **site)