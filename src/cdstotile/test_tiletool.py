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
    HOURS_PER_WEEK,
    HOURS_PER_YEAR,
    WEEKS_PER_YEAR
)
from extra_data_settings import (
    data_settings,
    data_settings_internal
)
from location_settings import (
    site_settings,
    ready_locations
)
from hig_utils import pretty_duration
from hig_csv import (
    write_csv_from_dict_of_lists,
    write_csv_from_list_of_dicts_simple
)
from data_groups import (
    data_groups,
    all_variables
)

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

def universal_flatten_cds(ds):
    dimensions = len(ds.dimensions)
    if dimensions == 3:
        time_size = len(ds[:,0,0])
        if time_size >= HOURS_PER_YEAR:
            flattened_array = ds[0:HOURS_PER_YEAR,0,0] #Truncate, pulling out the first dimension, since lat & lon are constant
            return flattened_array.flatten() #May be too short - current year doesn't have enough hours. Without .flatten() it's an array of 1-element arrays
        else:
            flattened_array = numpy.full((HOURS_PER_YEAR), -32767, dtype=numpy.float32)  # Start out with an array of Nulls (-32767)
            flattened_array[0:time_size] = ds[0:time_size,0,0]
            return flattened_array
    elif dimensions == 4:
        #This hunts for nulls, and if there's a null checks for a real value in the other expver column. Very slow.
        #Check for a NumPy "memscan" type function
        flattened_array = numpy.full((HOURS_PER_YEAR),-32767 , dtype = numpy.float32)#Start out with an array of Nulls (-32767)
        try:
            for i in range(HOURS_PER_YEAR):
                value = ds[i,0,0,0]
                if value > -32767: flattened_array[i] = value
                else:
                    flattened_array[i] = ds[i,1,0,0]
        except IndexError: pass #We ran out of input arrays, so we're done.
        return flattened_array
    else: raise RuntimeError(f"Unknown dataset - it should have either 3 or 4 dimensions, but instead has {dimensions}.")

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

def load_netcdfs(out_data, dir_name, start_year, end_year, area_lat_long, available_groups):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    grid_num = CalcQtrDegGridNum( area_lat_long )

    def process_data(out_data, year, files, analyze, sub_vars):
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
            raw_data.append(universal_flatten_cds(ds[files[i][1]]))
        start_time = time.time()
        analysis_function = analyze
        for week in range(WEEKS_PER_YEAR):
            if week == 0:
                start = 0
                end = HOURS_PER_WEEK
                results = initialize_results(analysis_function([data_array[start:end] for data_array in raw_data], area_lat_long))
            else:
                start = week*HOURS_PER_WEEK
                end = (week+1)*HOURS_PER_WEEK
                result = analysis_function([data_array[start:end] for data_array in raw_data], area_lat_long)
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

    benchmark_log = dict([(data_group,[]) for data_group in available_groups])
    for year in years:
        path = f'./{dir_name}/{year}/'
        for data_group in available_groups:
            benchmark_log[data_group].append(process_data(
                out_data,
                year,
                **data_groups[data_group]
            ))
    return benchmark_log

def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num

##########################################################

def export_year_to_csv(area_lat_long, year, filename):
    if year < 1979: path = f'./cds_era5_backext/{year}/'
    else: path = f'./cds_era5/{year}/'
    grid_num = CalcQtrDegGridNum(area_lat_long)
    stored_data = {}
    for i, var in enumerate(all_variables):
        filepath = f'{path}gn{grid_num}-{year}-{var[0]}.nc'
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
        this_array = universal_flatten_cds(ds[all_variables[i][1]])
        stored_data.update([(var[0],this_array)])
    write_csv_from_dict_of_lists(f"{year}_data_{filename}.csv",stored_data)

def write_full_csv(name, out_data):
    start_year = out_data['data_specs']['start_year']
    year = start_year
    csv_formatted_data = []
    variable_list = ['year','week']
    for variable, var_data in out_data['variables'].items():
        for statistic, stat_data in var_data.items():
            variable_name = f'{variable}_{statistic}'
            compressed_variable_name = f'compressed_{variable}_{statistic}'
            variable_list+=[variable_name, compressed_variable_name]
#            variable_list.append(variable_name)
            i = 0
            year = start_year
            for year_data in stat_data['data']:
                for week,value in enumerate(year_data):
                    try:
                        csv_formatted_data[i].update([
                            ('year',year),
                            ('week',week),
                            (compressed_variable_name, value),
                            (variable_name, data_settings_internal['flat_functions'][f'inverse_{variable}_{statistic}'](value))
                        ])
                    except IndexError:
                        csv_formatted_data.append({
                            'year':year,
                            'week':week,
                            compressed_variable_name:value,
                            variable_name:data_settings_internal['flat_functions'][f'inverse_{variable}_{statistic}'](value)
                        })
                    i += 1
                year += 1
    write_csv_from_list_of_dicts_simple(f'{name}.csv',csv_formatted_data, keys=variable_list)


##########################################################
# main

def process_site(out_data, name, end_year, inp_lat, inp_long, available_groups, output_raw_years):
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

    for year in output_raw_years:
        export_year_to_csv(area0, year, name)
    valid_vars = []
    for data_group in available_groups: valid_vars.extend(data_groups[data_group]['sub_vars'])

    # era5 back extension goes from 1950 to 1978
    log = load_netcdfs( out_data,
                        'cds_era5_backext',
                        1950, 1978,
                        area0,
                        available_groups)

    # era5 goes from 1979 to present
    log2 = load_netcdfs(out_data,
                        'cds_era5',
                        1979, end_year,
                        area0,
                        available_groups)

    #write log of processing time
    for key,time_list in log2.items():
        log[key] += time_list
    write_csv_from_dict_of_lists(f'log_of_processing_times_{name}.csv',log)
    # dump json
    # First check that the variables that are included are on var_list
    del_list = []
    for variable in out_data['variables']:
        if variable not in valid_vars: del_list.append(variable)
    for variable in del_list: del out_data['variables'][variable]
    gnum = CalcQtrDegGridNum( area0 )
    #outname = f'gn{gnum}-hwxpo.json'
    outname = filename
    print( f'Output {outname} (gnum={gnum})' )
    with open( outname, 'w') as outfile:
        json.dump( out_data, outfile )
    write_full_csv(name,out_data)



if __name__ == "__main__":
    print(f'** HWITW tile tool v{APP_VERSION} **\n')
    for site in [site_settings[name] for name in ready_locations]:
        process_site(copy.deepcopy(data_settings), **site)