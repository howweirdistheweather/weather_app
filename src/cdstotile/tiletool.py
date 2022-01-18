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
import argparse
import pathlib
import concurrent.futures

from generate_HWITW_stats import *
from data_settings import data_settings
from data_groups import data_groups, all_variables


# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
HOURS_PER_YEAR = 364 * 24
WEEKS_PER_YEAR = 52

# this is how CDS global netcdf files are indexed - by qtr degree
NUM_LONGIDX_GLOBAL = 1440
NUM_LATIDX_GLOBAL  = 721

APP_VERSION = "0.72"
current_time = datetime.datetime.now()

# what data processing to do for the whole globe (as opposed to specific locations)
global_data_groups = ['temperature_and_humidity','wind','precipitation','cloud_cover']


# make full pathname string for Global var netcdf input file
def var_filename( inp_path:str, dir_name:str, year:int, var_name:str ) -> (str, str):
    # file naming scheme
    pathname = f'{inp_path}/{dir_name}/{year}/'
    # filename = f'gn{grid_num}-{year}-{var_name}.nc'
    filename = f'global-{year}-{var_name}.nc'
    fullname = pathname + filename
    return fullname, filename


# make full pathname string for a Global output netcdf file
def out_filename( out_path:str, dgroup_name:str, year:int ) -> (dict):
    pathname = f'{out_path}/tt_output/{year}/'
    # filename = f'gn{grid_num}-{year}-{var_name}.nc'
    filestr = f'hwglobal-{dgroup_name}-{year}'
    filename = filestr + '.nc'
    tempfilename = filestr +'.tempnc'
    fullname = pathname + filename
    tempfullname = pathname + tempfilename
    o_names = {
        'pathname':pathname,
        'fullname':fullname,
        'filename':filename,
        'tempfullname':tempfullname
    }
    return o_names


# does output file already exist
def output_exists( out_path:str, dgroup_name:str, year:int ) -> bool:
    o_names = out_filename( out_path, dgroup_name, year )
    return os.path.isfile( o_names['fullname'] )


# create output netcdf
def create_output( out_path:str, dgroup_name:str, year:int ) -> (netCDF4.Dataset, str):
    # create & initialize the output dataset
    o_names = out_filename( out_path, dgroup_name, year )
    os.makedirs( o_names['pathname'], exist_ok=True )    # create the path if necessary

    try:
        ods = netCDF4.Dataset( o_names['tempfullname'], "w", format="NETCDF4" )
    except OSError:
        print( f'output {o_names["filename"]} could not be created!' )
        exit(-1)

    ods.createDimension( "week",      WEEKS_PER_YEAR )
    ods.createDimension( "latitude",  NUM_LATIDX_GLOBAL )
    ods.createDimension( "longitude", NUM_LONGIDX_GLOBAL )

    week_var = ods.createVariable( 'Week', 'f4', 'week' )
    week_var[:] = [ range(1, WEEKS_PER_YEAR+1) ]
    week_var.units = 'weeks'

    latitude = ods.createVariable( 'Latitude', 'f4', 'latitude' )
    latitude[:] = [(90 - (i * 180.25 / NUM_LATIDX_GLOBAL)) for i in range( NUM_LATIDX_GLOBAL )]
    latitude.units = 'degrees_north'

    longitude = ods.createVariable( 'Longitude', 'f4', 'longitude' )
    longitude[:] = [(i * 360.0 / NUM_LONGIDX_GLOBAL) for i in range( NUM_LONGIDX_GLOBAL )]
    longitude.units = 'degrees_east'

    return (ods, o_names)


# rename temporary output
def rename_finished_output( o_names:dict ):
    os.rename( o_names['tempfullname'], o_names['fullname'] )


# write to netcdf output Dataset
def save_output( ods:netCDF4.Dataset, week_idx:int, odat:dict ):
    # iterate thru the odat dictionary & save stuff to ods
    for ovar_name, ovar in odat.items():
        for stat_name, lat_dat in ovar.items():
            comb_name = ovar_name + '.' + stat_name
            if not comb_name in ods.variables:
                nc_var = ods.createVariable( comb_name, 'u1', ("week","latitude", "longitude") )
                #todo: annotate with descriptino compression type etc
                nc_var.description = data_settings['variables'][ovar_name][stat_name]['long_name']
                comp_type = data_settings['variables'][ovar_name][stat_name]['compression']
                nc_var.units = comp_type + json.dumps( data_settings['compression'][comp_type] )

            nc_var = ods.variables[ comb_name ]
            for lat_idx, stat in lat_dat.items():
                nc_var[week_idx, lat_idx] = numpy.asarray( stat, dtype=numpy.uint8 )


# store the hig stats output data in a dictionary.
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
        latitude_deg_n = 90.0 - (lat_i * 180.25 / NUM_LATIDX_GLOBAL)
        longitude_deg_e = long_i * 360.0 / NUM_LONGIDX_GLOBAL - 180.0
        lat0 = math.ceil( latitude_deg_n * 4 ) / 4
        lat1 = (math.floor( latitude_deg_n * 4 ) / 4) #+ 0.01 # edge is not inclusive
        long0 = math.floor( longitude_deg_e * 4 ) / 4
        long1 = (math.ceil( longitude_deg_e * 4 ) / 4) #- 0.01
        area_lat_long = [ lat0, long0, lat1, long1 ]

        # get hourly datas' as ndarrays for this location
        loc_data = []
        for var in lat_data:
            var_loc = var[ long_i ]
            loc_data.append( var_loc )

        analyze_func = data_group['analyze']
        results = analyze_func( loc_data, area_lat_long )

        # store the results
        for variable, variable_info in results.items():
            for stat, wk_value in variable_info.items():
                store_out_lat( out_lat, variable, stat, lat_i, long_i, wk_value )

    return out_lat


# process one full year for one data_group
def process_data_group( flag_args:dict, inp_path:str, out_path:str, dir_name:str, year:int, dg_name:str, data_group:dict ):

    fcalc = flag_args[ 'force_recalc' ]
    show_progress = flag_args[ 'show_progress' ]

    # if output file already exists and not force_recalc, skip this one. it is done.
    if output_exists( out_path, dg_name, year ) and (fcalc == False):
        print( f'\rSkipping completed output {dg_name}-{year}' )
        return

    if show_progress: print( f"Analyzing {dg_name}..." )
    # open all the netcdf input files needed to process this data_group
    ncds_group = []
    for var in data_group['files']:
        var_name = var[0]
        short_var_name = var[1]

        # make sure input file exists
        fullname, filename = var_filename( inp_path, dir_name, year, var_name )
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

        # these should all be true for a global var nc
        total_num_hours = ds.dimensions['time'].size
        num_lat         = ds.dimensions['latitude'].size
        num_long        = ds.dimensions['longitude'].size
        assert total_num_hours >= 8753  #HOURS_PER_YEAR ...whats up with this 8753 hours?
        assert num_long == NUM_LONGIDX_GLOBAL
        assert num_lat == NUM_LATIDX_GLOBAL

        # store the Dataset
        ncds_group.append( {
            'dataset':          ds,
            'var_name':         var_name,
            'short_var_name':   short_var_name
        } )

    # create netcdf Output file
    ods, o_names = create_output( out_path, dg_name, year )
    if show_progress:
        print( f'\rOutput {o_names["filename"]}', end='', flush=True )
    else:
        print( f'\rOutput {o_names["filename"]}', flush=True )


    # for each week of the year...
    num_weeks = WEEKS_PER_YEAR
    for week_i in range( num_weeks ):

        # for each Dataset needed by the data_group
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
                if show_progress: print( f'\rOutput {o_names["filename"]} {year} week {week_i+1}/{num_weeks} latitude {cnt}/{num_lat} ', end='', flush=True )
                olat = lf.result()
                save_output( ods, week_i, olat )
                cnt += 1

    # clear the progress output line from screen
    if show_progress: print( f'\rOutput {o_names["filename"]} done.                            ', flush=True )

    # close ods file and rename to mark as done
    ods.close()
    rename_finished_output( o_names )

    # free the input ds objects
    for ncds in ncds_group:
        ncds['dataset'].close()


# for all years process data_groups'
def load_netcdfs( flag_args:dict, inp_path:str, out_path:str, dir_name:str, start_year:int, end_year:int ):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    #grid_num = CalcQtrDegGridNum( area_lat_long )
    years = list( range( start_year, end_year + 1 ) )
    for year in years:
        yidx = year - start_year
        
        for dg_name in global_data_groups:
            dg = data_groups[ dg_name ]
            process_data_group( flag_args, inp_path, out_path, dir_name, year, dg_name, dg );


def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num


##########################################################
# main
def main():
    print( f'** HWITW data processing tool v{APP_VERSION} **\n')

    # default options
    input_path = '.'
    output_path = '.'

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-i", "--input", help = "Set input path" )
    parser.add_argument( "-o", "--output", help = "Set output path" )
    parser.add_argument( "-f", "--force", action='store_true', help = "Force recalculation of all output" )
    parser.add_argument( "-p", "--progress", action='store_true', help = "Show fancy progress" )
    args = parser.parse_args()

    flag_args = {
        'force_recalc':args.force,
        'show_progress':args.progress }

    show_progress = args.progress

    if args.input:
        input_path = args.input

    if args.output:
        output_path = args.output

    if not pathlib.Path( input_path ).exists():
        print( f'input path does not exist: {input_path}' )
        exit( -1 )

    if not pathlib.Path( output_path ).exists():
        print( f'output path does not exist: {output_path}' )
        exit( -1 )

    # era5 goes from 1979 to present
    load_netcdfs( flag_args, input_path, output_path, 'cds_era5', 1979, current_time.year )

    # era5 back extension goes from 1950 to 1978
    load_netcdfs( flag_args, input_path, output_path, 'cds_era5_backext', 1950, 1978 )


if __name__ == '__main__':
    main()
