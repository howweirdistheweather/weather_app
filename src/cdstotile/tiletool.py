# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021
#
import math
import copy
import struct
import datetime
import os.path
import gc
import json
import numpy
import netCDF4
import concurrent.futures

from generate_HWITW_statistics import *
from data_settings import data_settings
#from hig_utils import pretty_duration
#from hig_csv import write_csv_from_dict_of_lists


# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
HOURS_PER_YEAR = 364 * 24
WEEKS_PER_YEAR = 52

# this is how CDS global netcdf files are indexed - by qtr degree
NUM_LONGIDX_GLOBAL = 1440
NUM_LATIDX_GLOBAL  = 721

APP_VERSION = "0.66"
current_time = datetime.datetime.now()

# the variables we are interested, long name and short name.
# short name is used inside the netcdf files
CDSVAR_U10      = ['10m_u_component_of_wind', 'u10']
CDSVAR_V10      = ['10m_v_component_of_wind', 'v10']
CDSVAR_D2M      = ['2m_dewpoint_temperature', 'd2m']
CDSVAR_T2M      = ['2m_temperature',          't2m']
CDSVAR_CBH      = ['cloud_base_height',       'cbh']
CDSVAR_PTYPE    = ['precipitation_type',      'ptype']
CDSVAR_TCC      = ['total_cloud_cover',       'tcc']
CDSVAR_TP       = ['total_precipitation',     'tp']

process_settings = [
    {
        'data_group': 'temperature_and_humidity',
        'files': [CDSVAR_T2M, CDSVAR_D2M],
        'analyze': do_temp_dp,
        'analysis_kwargs': {
            'lon': 0.0
        }
    },
    {
        'data_group': 'wind',
        'files': [CDSVAR_U10, CDSVAR_V10],
        'analyze': do_wind,
        'analysis_kwargs': {}
    },
    {
        'data_group': 'precipitation',
        'files': [CDSVAR_TP, CDSVAR_PTYPE],
        'analyze': do_precip,
        'analysis_kwargs': {}
    },
    {
        'data_group': 'cloud_cover',
        'files': [CDSVAR_TCC],
        'analyze': do_cloud_cover,
        'analysis_kwargs': {}
    },

]


# make full pathname string for Global var nc input file
def var_filename( dir_name:str, year:int, var_name:str ) -> (str, str):
    # file naming scheme
    pathname = f'./{dir_name}/{year}/'
    # filename = f'gn{grid_num}-{year}-{var_name}.nc'
    filename = f'global-{year}-{var_name}.nc'
    fullname = pathname + filename
    return fullname, filename


# make full pathname string for Global output json file
def out_filename( dgroup_name:str, year:int, week:int ) -> (str, str, str):
    # file naming scheme
    pathname = f'./tt_output/{year}/'
    # filename = f'gn{grid_num}-{year}-{var_name}.nc'
    filename = f'global-{dgroup_name}-{year}-{week}.nc'
    fullname = pathname + filename
    return pathname, fullname, filename


# create output netcdf
def create_output( dgroup_name:str, year:int, week_idx:int ) -> (netCDF4.Dataset, str):
    # create & initialize the output dataset
    o_pathname, o_fullname, o_filename = out_filename( dgroup_name, year, week_idx + 1 )
    os.makedirs( o_pathname, exist_ok=True )    # create the path if necessary

    try:
        ods = netCDF4.Dataset( o_fullname, "w", format="NETCDF4" )
    except OSError:
        print( f'{o_filename} could not be opened!' )
        exit(-1)

    ods.createDimension( "latitude",  NUM_LATIDX_GLOBAL )
    ods.createDimension( "longitude", NUM_LONGIDX_GLOBAL )

    latitude = ods.createVariable( 'Latitude', 'f4', 'latitude' )
    latitude[:] = [(90 - (i * 180.25 / NUM_LATIDX_GLOBAL)) for i in range( NUM_LATIDX_GLOBAL )]
    latitude.units = 'degrees_north'

    longitude = ods.createVariable( 'Longitude', 'f4', 'longitude' )
    longitude[:] = [(i * 360.0 / NUM_LONGIDX_GLOBAL) for i in range( NUM_LONGIDX_GLOBAL )]
    longitude.units = 'degrees_east'

    return (ods, o_filename)


# write to output netcdf
def save_output( ods:netCDF4.Dataset, odat:dict ):
    # iterate thru the odat dictionary & save stuff to ods
    for ovar_name, ovar in odat.items():
        for stat_name, lat_dat in ovar.items():
            comb_name = ovar_name + '.' + stat_name
            if not comb_name in ods.variables:
                nc_var = ods.createVariable( comb_name, 'u1', ("latitude", "longitude") )

            nc_var = ods.variables[ comb_name ]
            for lat_idx, stat in lat_dat.items():
                nc_var[lat_idx] = numpy.asarray( stat, dtype=numpy.uint8 )


# store output data in a dictionary
def store_out_lat( odat:dict, var_name:str, stat_name:str, lat_i:int, long_i:int, wk_value ):
    if not var_name in odat.keys():
        odat[ var_name ] = { stat_name: { lat_i: [None for i in range(NUM_LONGIDX_GLOBAL)] } }

    if not stat_name in odat[ var_name ].keys():
        odat[ var_name ][ stat_name ] = { lat_i: [None for i in range(NUM_LONGIDX_GLOBAL)] }

    odat[ var_name ][ stat_name ][ lat_i ][long_i] = wk_value


def process_lat( lat_i:int, lat_data, data_group:dict ):
    out_lat = {}
    # for each longitude
    for long_i in range( NUM_LONGIDX_GLOBAL ):
        # process 1 location 1 week
        #if ( data_group['analysis_kwargs'].contains( 'lon' ) ):
        longitude_deg_e = long_i * 360.0 / NUM_LONGIDX_GLOBAL - 180.0
        data_group['analysis_kwargs']['lon'] = longitude_deg_e

        # get hourly datas' as ndarrays for this location
        loc_data = []
        for var in lat_data:
            var_loc = var[ long_i ]
            loc_data.append( var_loc )

        analyze_func = data_group['analyze']
        results = analyze_func( loc_data, **data_group['analysis_kwargs'] )

        # store the results
        for variable, variable_info in results.items():
            for stat, wk_value in variable_info.items():
                store_out_lat( out_lat, variable, stat, lat_i, long_i, wk_value )

    return out_lat


# process one full year for one data_group
def process_data_group( dir_name:str, year:int, data_group:dict ):
    print( f"Analyzing {data_group['data_group']}..." )

    # open all the netcdf input files needed to process this data_group
    ncds_group = []
    for var in data_group['files']:
        var_name = var[0]
        short_var_name = var[1]

        # make sure file exists
        fullname, filename = var_filename( dir_name, year, var_name )
        already_exists = os.path.isfile( fullname )
        if not already_exists:
            print( f'{filename} is missing!', flush=True )
            return

        # load file
        #print( f'loading {filename}', flush=True )
        try:
            ds = netCDF4.Dataset( fullname, 'r' )
        except OSError:
            print( f'{filename} could not be opened!' )
            exit(-1)

        # these should all be true for a global var nc1
        total_num_hours = ds.dimensions['time'].size
        num_lat         = ds.dimensions['latitude'].size
        num_long        = ds.dimensions['longitude'].size
        assert total_num_hours >= 8753  #HOURS_PER_YEAR ...whats up with this 8753 hours?
        assert num_long == NUM_LONGIDX_GLOBAL
        assert num_lat == NUM_LATIDX_GLOBAL

        # store the ds
        ncds_group.append( {
            'dataset':          ds,
            'var_name':         var_name,
            'short_var_name':   short_var_name }
        )

    # for each week of the year...
    num_weeks = WEEKS_PER_YEAR
    for week_i in range( num_weeks ):

        # store output in this guy
        print( f'\rOutput {o_filename} done', end='', flush=True )
        ods, o_filename = create_output( data_group['data_group'], year, week_i )
        #out_data = copy.deepcopy( data_settings )
        #out_data = { 'cat':'meow' }

        # for each ds needed by the data_group
        week_data = []
        for ncds in ncds_group:
            ds =                ncds['dataset']
            short_var_name =    ncds['short_var_name']
            
            # load the weeks worth of hours (for all locations in file). transpose to lat,long,hour
            hr_0 = week_i * HOURS_PER_WEEK
            hr_1 = hr_0 + HOURS_PER_WEEK
            var_week = numpy.transpose( ds[ short_var_name ][hr_0:hr_1][:][:], axes=(1, 2, 0) )
            assert( var_week.dtype == numpy.float64 )
            week_data.append( var_week )

        # for each latitude in the file, spawn processes
        with concurrent.futures.ProcessPoolExecutor() as execute:   #max_workers=6
            lfuts = []
            for lat_i in range( num_lat ):
                # get hourly datas' as ndarrays for this entire latitude
                lat_data = []
                for var_week in week_data:
                    var_lat = numpy.ma.getdata( var_week[:][lat_i] )
                    lat_data.append( var_lat )

                lfuts.append( execute.submit( process_lat, lat_i, lat_data, data_group ) )

            # wait for futures and save to ods
            cnt = 1
            for lf in lfuts:
                print( f'\rOutput {o_filename} {year} week {week_i+1}/{num_weeks} latitude {cnt}/{num_lat} ', end='', flush=True )
                olat = lf.result()
                save_output( ods, olat )
                cnt += 1

        # clear the progress output line from screen
        print( f'\rOutput {o_filename} ...done', flush=True )

        # close ods file
        ods.close()
        # todo: rename ods file to mark it as done.

    # free the input ds objects
    for ncds in ncds_group:
        ncds['dataset'].close()


# for all years process data_groups'
def load_netcdfs( dir_name:str, start_year:int, end_year:int ):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    #grid_num = CalcQtrDegGridNum( area_lat_long )
    years = list( range( start_year, end_year + 1 ) )
    for year in years:
        yidx = year - start_year
        
        for data_group in process_settings:
            process_data_group( dir_name, year, data_group );


def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num


##########################################################
# main
def main():
    print( f'** HWITW tile tool v{APP_VERSION} **\n')

    # era5 goes from 1979 to present
    load_netcdfs(   'cds_era5', 1979, current_time.year )

    # era5 back extension goes from 1950 to 1978
    load_netcdfs(   'cds_era5_backext', 1950, 1978 )


if __name__ == '__main__':
    main()
