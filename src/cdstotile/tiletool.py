"""
Copyright 2023 Ground Truth Alaska

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021, 2022, 2023
#
import math
import copy
import struct
import datetime
import os.path
import shutil
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
from wxdb import *


# ignoring leap years (i.e. week 53)!
HOURS_PER_WEEK = 24 * 7
HOURS_PER_YEAR = 364 * 24
WEEKS_PER_YEAR = 52

# this is how CDS global netcdf files are indexed - by qtr degree
NUM_LONGIDX_GLOBAL = 1440
NUM_LATIDX_GLOBAL  = 721

APP_VERSION = "0.9.5"
current_time = datetime.datetime.now()

# what data processing to do for the whole globe (as opposed to specific locations)
global_data_groups = ['temperature_and_humidity','wind','precipitation','cloud_cover']


# make full pathname string for Global var netcdf input file
def inp_filename( inp_path:str, dir_name:str, year:int, cds_var_name:str ) -> (str, str):
    # file naming scheme
    pathname = f'{inp_path}/{dir_name}/{year}/'
    # filename = f'gn{grid_num}-{year}-{cds_var_name}.nc'
    filename = f'global-{year}-{cds_var_name}.nc'
    fullname = pathname + filename
    return fullname, filename


# make full pathname string for MultiSet Global var netcdf Input files
def inp_multiset_filename( inp_path:str, dir_name:str, year:int, cds_var_name:str ) -> (str, str):
    # file naming scheme
    pathname = f'{inp_path}/{dir_name}/{year}/{cds_var_name}/'
    # filename = f'gn{grid_num}-{year}-{cds_var_name}.nc'
    filename = f'global-{year}-*-{cds_var_name}.nc'
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
def create_output( out_path:str, dgroup_name:str, year:int, num_weeks:int ) -> (netCDF4.Dataset, str):
    # create & initialize the output dataset
    o_names = out_filename( out_path, dgroup_name, year )
    os.makedirs( o_names['pathname'], exist_ok=True )    # create the path if necessary

    try:
        ods = netCDF4.Dataset( o_names['tempfullname'], mode="w", clobber=True, format="NETCDF4" )
    except OSError:
        print( f'output {o_names["tempfullname"]} could not be created!' )
        exit(-1)

    ods.createDimension( "week",      None ) # make this an unlimitd dimension. #num_weeks )
    ods.createDimension( "latitude",  NUM_LATIDX_GLOBAL )
    ods.createDimension( "longitude", NUM_LONGIDX_GLOBAL )

    week_var = ods.createVariable( 'Week', 'int', 'week' )
    for i in range(num_weeks):
        week_var[i] = i+1
    week_var.units = 'weeks'

    latitude = ods.createVariable( 'Latitude', 'f4', 'latitude' )
    latitude[:] = [(90 - (i * 180.25 / NUM_LATIDX_GLOBAL)) for i in range( NUM_LATIDX_GLOBAL )]
    latitude.units = 'degrees_north'

    longitude = ods.createVariable( 'Longitude', 'f4', 'longitude' )
    longitude[:] = [(i * 360.0 / NUM_LONGIDX_GLOBAL) for i in range( NUM_LONGIDX_GLOBAL )]
    longitude.units = 'degrees_east'

    return (ods, o_names)


# open existing output netcdf as temp file
def open_output( out_path:str, dgroup_name:str, year:int ) -> (netCDF4.Dataset, str):
    # create & initialize the output dataset
    o_names = out_filename( out_path, dgroup_name, year )

    try:
        # copy existing file to tempfilename, then try to open it
        shutil.copy2( o_names['fullname'], o_names['tempfullname'] )
        ods = netCDF4.Dataset( o_names['tempfullname'], mode="r+", clobber=False )
    except OSError:
        print( f'Existing output {o_names["tempfullname"]} could not be opened!' )
        exit(-1)

    return (ods, o_names)


# open existing output netcdf readonly
def open_output_ro( out_path:str, dgroup_name:str, year:int ) -> (netCDF4.Dataset, str):
    # create & initialize the output dataset
    o_names = out_filename( out_path, dgroup_name, year )

    try:
        ods = netCDF4.Dataset( o_names['fullname'], mode="r", clobber=False )
    except OSError:
        print( f'Existing output {o_names["fullname"]} could not be opened!' )
        exit(-1)

    return (ods, o_names)


# rename temporary output
def rename_finished_output( o_names:dict ):
    os.rename( o_names['tempfullname'], o_names['fullname'] )


# write to netcdf output Dataset
def save_output( ods:netCDF4.Dataset, year:int, week_idx:int, odat:dict ):
    # iterate thru the odat dictionary & save stuff to ods
    for ovar_name, ovar in odat.items():
        for stat_name, lat_dat in ovar.items():
            comb_name = ovar_name + '.' + stat_name
            if not comb_name in ods.variables:
                nc_var = ods.createVariable( comb_name, 'u1', ("week","latitude","longitude") )
                #todo: annotate with description compression type etc
                nc_var.description = data_settings['variables'][ovar_name][stat_name]['long_name']
                comp_type = data_settings['variables'][ovar_name][stat_name]['compression']
                nc_var.units = comp_type + json.dumps( data_settings['compression'][comp_type] )

            nc_var = ods.variables[ comb_name ]

            for lat_idx, stat in lat_dat.items():
                stat_array = numpy.asarray( stat, dtype=numpy.uint8 )
                nc_var[week_idx, lat_idx] = stat_array


# store the hig stats output data in a dictionary.
def store_out_lat( odat:dict, var_name:str, stat_name:str, lat_i:int, long_i:int, wk_value ):
    # create output dicts if they don't already exist
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
        # is this next line correct?
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

    fcalc         = flag_args[ 'force_recalc' ]
    show_progress = flag_args[ 'show_progress' ]
    fupdate       = flag_args[ 'update_data' ]

    # if output file already exists follow this logic
    fout_exists = output_exists( out_path, dg_name, year )
    if (fout_exists == True) and (fcalc == False) and (fupdate == False):
        print( f'\rSkipping completed output {dg_name}-{year}' )
        return

    if show_progress: print( f"Analyzing {dg_name}..." )
    # open all the netcdf input files needed to process this data_group
    ncds_group = []
    total_num_hours = HOURS_PER_YEAR
    for var in data_group['files']:
        var_name = var[0]
        short_var_name = var[1]

        # first try to load the daily set of netcdfs
        fullname, filename = inp_multiset_filename( inp_path, dir_name, year, var_name )
        try:
            # todo: make sure this fails if some daily files are missing in the middle of the set
            # ...time should monotonically increase
            ds = netCDF4.MFDataset( files=fullname, check=True, aggdim='time' )
        except OSError as ex:
            print( f'daily input {filename} could not be opened. {ex} Trying yearly.' )
            # ok try to open the single big yearly netcdf
            fullname, filename = inp_filename( inp_path, dir_name, year, var_name )
            try:
                ds = netCDF4.Dataset( fullname, 'r' )
            except OSError as ex:
                print( f'{filename} could not be opened! {ex}' )
                exit( -1 )
        
        total_num_hours = min( len(ds.dimensions['time']), total_num_hours )
        num_lat         = ds.dimensions['latitude'].size
        num_long        = ds.dimensions['longitude'].size
        num_dimensions  = len(ds.dimensions)

        assert total_num_hours >= 0
        assert num_long == NUM_LONGIDX_GLOBAL
        assert num_lat == NUM_LATIDX_GLOBAL
        assert (num_dimensions == 3) # or num_dimensions == 4)

        # store the Dataset
        ncds_group.append( {
            'dataset':          ds,
            'var_name':         var_name,
            'short_var_name':   short_var_name
        } )

    start_week = 0
    num_weeks = min( total_num_hours // HOURS_PER_WEEK, WEEKS_PER_YEAR )
    # create netcdf Output file
    if fcalc == True or (fupdate == True and fout_exists == False) or fupdate == False:
        ods, o_names = create_output( out_path, dg_name, year, num_weeks )
    # open existing output file
    else:
        ods, o_names = open_output( out_path, dg_name, year )
        #print( f'debug: {ods.dimensions["week"]}' )
        start_week = ods.dimensions['week'].size
    print( f'debug: start_week {start_week} num_weeks {num_weeks} total_num_hours {total_num_hours}' )

    if show_progress:
        print( f'\rOutput {o_names["filename"]}', end='', flush=True )
    else:
        print( f'\rOutput {o_names["filename"]}', flush=True )

    # for each week present in the input data
    #debug
    for week_i in range( start_week, num_weeks ):

        # keep Week value correct in ods
        wk_var = ods.variables[ 'Week' ]
        if wk_var.size-1 < week_i:
            wk_var.append(week_i + 1)
        else:
            wk_var[week_i] = week_i + 1

        # for each Dataset needed by the data_group
        week_data = []
        for ncds in ncds_group:
            ds =                ncds['dataset']
            short_var_name =    ncds['short_var_name']

            # load the weeks worth of hours (for all locations in file). transpose to lat,long,hour
            hr_0 = week_i * HOURS_PER_WEEK
            hr_1 = hr_0 + HOURS_PER_WEEK
            if num_dimensions == 3:
                var_week = numpy.transpose( ds[ short_var_name ][hr_0:hr_1][:][:], axes=(1, 2, 0) )

            elif num_dimensions == 4:
                # todo: we shouldn't need this code. cdstool should be fixing expver
                # handle current year. it has a weird expver column / extra dimension
                var_week = numpy.transpose( ds[ short_var_name ][hr_0:hr_1][:][:][:], axes=(2, 3, 0, 1) )
                # convert invalids to 0
                var_week = numpy.ma.filled( var_week, 0 )
                # sum columns on dimension 3 and then drop column 1
                var_week[:, :, :, 0] = var_week[:, :, :, 0] + var_week[:, :, :, 1]
                var_week = numpy.delete( var_week, 1, axis=3 )

            else:
                raise RuntimeError(f"Unknown dataset - it should have either 3 or 4 dimensions, but instead has {num_dimensions}.")

            assert( var_week.dtype == numpy.float64 )
            week_data.append( var_week )

        # # debug: single threaded version for profiling
        # cnt = 1
        # #debug
        # for lat_i in range( num_lat ):
        #     # get hourly datas' as ndarrays for this entire latitude
        #     lat_data = []
        #     for var_week in week_data:
        #         var_lat = numpy.ma.getdata( var_week[:][lat_i] )
        #         lat_data.append( var_lat )
        #
        #     olat = process_lat( lat_i, lat_data, data_group )
        #     if show_progress:
        #         print( f'\rOutput {o_names["filename"]} {year} week {week_i+1}/{num_weeks} latitude {cnt}/{num_lat} ', end='', flush=True )
        #     save_output( ods, year, week_i, olat )
        #     cnt += 1

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

            # wait for futures
            cnt = 1
            olat=[]
            for lf in lfuts:
                if show_progress:
                    print( f'\rOutput {o_names["filename"]} {year} week {week_i+1}/{num_weeks} latitude {cnt}/{num_lat}      ', end='', flush=False )
                olat.append( lf.result() )
                cnt += 1
            # save to ods
            cnt = 1
            for ol in olat:
                if show_progress:
                    print( f'\rSave {o_names["filename"]} {year} week {week_i+1}/{num_weeks} latitude {cnt}/{num_lat}      ', end='', flush=False )
                save_output( ods, year, week_i, ol )
                cnt += 1

    # clear the progress output line from screen
    if show_progress: print( f'\rOutput {o_names["filename"]} done.                                 ', flush=True )

    # free the input ds objects
    for ncds in ncds_group:
        ncds['dataset'].close()

    # close ods file and rename to mark as done
    ods.close()
    rename_finished_output( o_names )


# for all years process data_group's
def load_netcdfs( flag_args:dict, inp_path:str, out_path:str, start_year:int, end_year:int ):
    years = list( range( start_year, end_year + 1 ) )
    for year in years:
        yidx = year - start_year

        # era5 back extension goes from 1950 to 1978
        if year >= 1950 and year <= 1978:
            dir_name = 'cds_era5_backext'
        # era5 goes from 1979 to present
        else:
            dir_name = 'cds_era5'

        for dg_name in global_data_groups:
            dg = data_groups[ dg_name ]
            process_data_group( flag_args, inp_path, out_path, dir_name, year, dg_name, dg );


def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((90 - area_lat_long[0]) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num


# def process_lat_wxdb( out_path:str, wxvt:list, year:int, lat_i:int ) -> list:
#     num_wx_vars = len(wxvt)
#     # open all our custom processed netcdf output files for this year
#     ods_list = []
#     ods_vars = {}
#     start_week = 0
#     num_weeks = 0
#     for dg_name in global_data_groups:
#         ods, o_names = open_output_ro( out_path, dg_name, year )
#         ods_list.append( ods )
#         #print( f'debug: opened {o_names["fullname"]}' )
#         #print( f'debug week dimension: {ods.dimensions["week"]}' )
#         num_weeks = ods.dimensions['week'].size
#         #print( f'debug: start_week {start_week} num_weeks {num_weeks}' )
#
#         # get all variables in a dict
#         var_i = 0
#         for nc_varname, nc_var in ods.variables.items():
#             if nc_varname in ['Week','Latitude','Longitude']: # skip
#                 continue
#             ods_vars[nc_varname] = nc_var
#             #print( f'debug: added {nc_varname} to ods_vars' )
#
#     # for each longitude
#     lat_data = []
#     for long_i in range( NUM_LONGIDX_GLOBAL ):
#         # gather the 1 year worth of data
#         # for each variable, get the weeks of data for year
#         wk_var_array = numpy.zeros( (num_weeks, num_wx_vars), dtype=numpy.uint8 )
#         var_idx = 0
#         for var_name in wxvt:
#             wk_var_array[:,var_idx] = ods_vars[var_name][start_week:num_weeks, lat_i, long_i]
#             var_idx += 1
#
#         lat_data.append( wk_var_array )
#
#     return lat_data
#
#
# def save_lat_wxdb(  year:int, lat_i:int, lat_dat:list ):
#     #for each longitude
#     for long_i in range( NUM_LONGIDX_GLOBAL ):
#         # write data for location, year
#         wk_var_array = lat_dat[ lat_i ]
#         write_wxdb( lat_i, long_i, year, wk_var_array )


# basically pull data out of our custom processed netcdfs, and put it into the wxdb
#@profile
def update_wxdb( flag_args:dict, out_path:str, start_year:int, end_year:int ):
    print( 'debug: update_wxdb()' )
    fcalc         = flag_args[ 'force_recalc' ]
    show_progress = flag_args[ 'show_progress' ]
    fupdate       = flag_args[ 'update_data' ]

    print( f'\rOutput WXDB', flush=True )

    wxvtable = open_wxdb( out_path + '/hwitw.wxdb' )
    try:
        num_wx_vars = len(wxvtable)
        print( f'debug: num_wx_vars {num_wx_vars}' )

        # we will process one year at a time
        years = list( range( start_year, end_year + 1 ) )
        for year in years:
            yidx = year - start_year
            start_week = 0
            num_weeks = 0

            # open all our custom processed netcdf output files for this year,
            # to get all the data for all the variables we want.
            ods_list = []
            ods_vars = {}
            for dg_name in global_data_groups:
                ods, o_names = open_output_ro( out_path, dg_name, year )
                ods_list.append( ods )
                print( f'debug: opened {o_names["fullname"]}' )
                #print( f'debug week dimension: {ods.dimensions["week"]}' )

                # get the number of weeks. make sure each file has the same
                nw_in_file = ods.dimensions['week'].size
                if num_weeks == 0:  num_weeks=nw_in_file
                elif nw_in_file != num_weeks:
                    raise RuntimeError(f'num_weeks mismatch looking for {num_weeks}, got {nw_in_file} {o_names["fullname"]}.')
                #print( f'debug: start_week {start_week} num_weeks {num_weeks}' )

                # get all variables in a dict
                var_i = 0
                for nc_varname, nc_var in ods.variables.items():
                    if nc_varname in ['Week','Latitude','Longitude']: # skip
                        continue
                    ods_vars[nc_varname] = nc_var
                    #print( f'debug: added {nc_varname} to ods_vars' )

            if show_progress:
                print( f'\rSave WXDB {year}                                 ', end='', flush=False )

            # create array for grabbing netcdf data
            grab_data_array = numpy.zeros(
                (NUM_LATIDX_GLOBAL, NUM_LONGIDX_GLOBAL, num_weeks, num_wx_vars),
                dtype=numpy.uint8 )
            # for each variable, get all weeks of data for year for all locations
            var_idx = 0
            for var_name in wxvtable:
                nc_var = ods_vars[var_name]
                #print( f'debug: transpose {var_idx}' )
                # get this [week,lat,long,variable]
                # store as this [lat,long,week,variable]
                tmpa = nc_var[start_week:num_weeks, :, :]
                tmpb = numpy.transpose( tmpa, (1,2,0) )
                grab_data_array[:,:,:,var_idx] = tmpb[:]
                var_idx += 1

            # write the years worth of data to disk
            print( 'debug: write wxdb' )
            write_wxdb_lat( year, grab_data_array )

            # clear the progress output line from screen
            if show_progress:
                print( f'\rWXDB Output done {year}.                             ', flush=True)

            # close netcdf datasets
            for ads in ods_list:
                ads.close()
    finally:
        close_wxdb()

    return


##########################################################
# main
def main():
    print( f'** HWITW data processing tool v{APP_VERSION} **\n')

    # default options
    input_path = '.'
    output_path = '.'
    start_year = 1950
    end_year = current_time.year
    data_dir = 'cds_era5'

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-i", "--input", help = "Set input path" )
    parser.add_argument( "-o", "--output", help = "Set output path" )
    parser.add_argument( "-f", "--force", action='store_true', help = "Force recalculation of all output" )
    parser.add_argument( "-p", "--progress", action='store_true', help = "Show fancy progress" )
    parser.add_argument( "-s", "--start", help = "Set start year" )
    parser.add_argument( "-e", "--end", help = "Set end year" )
    parser.add_argument( "-u", "--update", action='store_true', help = "get latest data" )
    parser.add_argument( "-c", "--createwxdb", action='store_true', help = "recreate the wxdb file" )
    
    args = parser.parse_args()

    flag_args = {
        'force_recalc':args.force,
        'show_progress':args.progress,
        'update_data':args.update }

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

    if args.start:
        start_year = int(args.start)

    if args.end:
        end_year = int(args.end)

    if args.createwxdb:
        create_wxdb( 'hwitw.wxdb' )

    # process the cds downloads into our custom netcdfs
    load_netcdfs( flag_args, input_path, output_path, start_year, end_year )

    # process the netcdfs into the wxdb
    # import cProfile,pstats
    # profob = cProfile.Profile()
    # profob.enable()
    update_wxdb( flag_args, output_path, start_year, end_year )
    # profob.disable()
    # pstats.Stats(profob).sort_stats('cumulative').print_stats() #.strip_dirs()


if __name__ == '__main__':
    main()
