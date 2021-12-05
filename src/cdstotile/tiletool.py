# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021
#
import math
import datetime
import os.path
import json
import numpy
import netCDF4
import timeit

import parsl
from parsl import python_app
from parsl.config import Config
#from parsl.executors.threads import ThreadPoolExecutor
from parsl.providers import LocalProvider
from parsl.channels import LocalChannel
from parsl.executors import HighThroughputExecutor

import hwxpo
from wxstat import *

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

# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
HOURS_PER_YEAR = 365 * 24
WEEKS_PER_YEAR = 52

APP_VERSION = "0.50"
current_time = datetime.datetime.now()


def process_netcdf( fullname:str, filename:str, year:int, short_var_name:str ) -> hwxpo.HWXGlobal:
    # load file and process each location and time
    print( f'processing {filename}', flush=True )
    try:
        ds = netCDF4.Dataset( fullname, 'r' )
    except OSError:
        print( bcolors.FAIL + f'{filename} could not be opened!' + bcolors.ENDC )
        exit(-1)

    total_num_hours = ds.dimensions['time'].size
    num_lat         = ds.dimensions['latitude'].size
    num_long        = ds.dimensions['longitude'].size
    assert total_num_hours >= 8753  #HOURS_PER_YEAR ...whats up with this 8753 hours?
    assert num_long == 1440
    assert num_lat == 721

    hwxout = []# hwxpo.HWXGlobal( year )

    # for each week in ds..
    num_weeks = int(total_num_hours / HOURS_PER_WEEK)
    for week_i in range( num_weeks ):
        # print progress
        print( f'\rweek {week_i}/{num_weeks}', end='\n', flush=True )

        # load the weeks worth of hours for all locations. transpose to long,lat,hour
        hr_0 = week_i * HOURS_PER_WEEK
        hr_1 = hr_0 + HOURS_PER_WEEK
        var_week = numpy.transpose( ds[short_var_name][hr_0:hr_1][:][:] )
        assert( var_week.dtype == numpy.float64 )

        # for each location in var_week
        for lat_i in range( num_lat ):
            
            print( f'\r{lat_i}/{num_lat}', end='', flush=True )
            for long_i in range( num_long ):
                # get hourly as ndarray for this location
                var_loc = numpy.ma.getdata( var_week[long_i][lat_i] )
                #print( f'{type(var_loc)} {var_loc.dtype} {var_loc.shape} {var_loc.size}' )
                #print( timeit.timeit( lambda: numpy.average( var_loc ), number=4 )/4 )                
                # process a specific variable and week and location
                hs = calc_week_stat( var_loc, short_var_name )
                #hwxout.merge_stat( hs, lat_i, long_i, week_i )

    print( f'\r', end='', flush=True )    # newline
    return hwxout

def load_netcdfs( dir_name, start_year, end_year ):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    #grid_num = CalcQtrDegGridNum( area_lat_long )

    years = list( range( start_year, end_year + 1 ) )
    #yearly_results = [None] * len(years)

    for year in years:
        yidx = year - start_year

        for vnames in cds_variables:
            var_name = vnames[0]
            short_var_name = vnames[1]

            # file naming scheme
            pathname = f'./{dir_name}/{year}/'
            # filename = f'gn{grid_num}-{year}-{var_name}.nc'
            filename = f'global-{year}-{var_name}.nc'
            fullname = pathname + filename

            # make sure file exists
            already_exists = os.path.isfile( fullname )
            if not already_exists:
                print(bcolors.WARNING + f'{filename} is missing!' + bcolors.ENDC, flush=True)
                continue

            # process the file
            hwx_f = process_netcdf( fullname, filename, year, short_var_name );
            #write to disk

def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num

##########################################################
# main

print( f'** HWITW tile tool v{APP_VERSION} **\n')

inp_lat = 59.64 # homer ak
inp_long = -151.54

# get the containing cell 
lat0 = math.ceil( inp_lat * 4 ) / 4
lat1 = (math.floor( inp_lat * 4 ) / 4) #+ 0.01 # edge is not inclusive
long0 = math.floor( inp_long * 4 ) / 4
long1 = (math.ceil( inp_long * 4 ) / 4) #- 0.01

area0 = [ lat0, long0, lat1, long1 ]
area0 = None

# era5 goes from 1979 to present
load_netcdfs(   'cds_era5',
                1979, current_time.year )

# era5 back extension goes from 1950 to 1978
load_netcdfs(   'cds_era5_backext',
                1950, 1978 )

# dump json
#gnum = CalcQtrDegGridNum( area0 )
#outname = f'gn{gnum}-hwxpo.json'
#print( f'Output {outname}' )
#with open( outname, 'w') as outfile:
    #json.dump( hpo.get_jodict(), outfile )
