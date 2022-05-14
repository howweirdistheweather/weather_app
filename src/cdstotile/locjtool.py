import datetime
import numpy
import netCDF4
import json
import argparse
import pathlib
from data_groups import data_groups, all_variables
from data_settings import *
from location_settings import *

APP_VERSION         = '0.69'

HOURS_PER_WEEK      = 24 * 7
HOURS_PER_YEAR      = 364 * 24
WEEKS_PER_YEAR      = 52
NUM_LONGIDX_GLOBAL  = 1440
NUM_LATIDX_GLOBAL   = 721
HWITW_START_YEAR    = 1950  # hardcoded in the web client right?

current_time        = datetime.datetime.now()


# make full pathname string for a HWITW Global output netcdf file created by tiletool.py
def hn_filename( out_path:str, dgroup_name:str, year:int ) -> (dict):
    pathname = f'{out_path}/tt_output/{year}/'
    filestr = f'hwglobal-{dgroup_name}-{year}'
    filename = filestr + '.nc'
    fullname = pathname + filename
    hn_names = {
        'pathname':pathname,
        'fullname':fullname,
        'filename':filename
    }
    return hn_names


# get datagroup's data for this year for this single grid location
def read_data_group( flag_args:dict,
        loc_lat:float, loc_long:float, 
        inp_path:str, year:int, 
        dg_name:str, dg:dict, 
        out_data:dict ):

    in_names = hn_filename( inp_path, dg_name, year )
    try:
        ds = netCDF4.Dataset( in_names['fullname'], mode='r', format='NETCDF4' )
    except OSError as ex:        
        print( f'{in_names["fullname"]} could not be opened!: {ex.strerror}' )
        exit(-1)

    # these should all be true for a global var nc
    num_weeks       = ds.dimensions['week'].size
    num_lat         = ds.dimensions['latitude'].size
    num_long        = ds.dimensions['longitude'].size
    num_dimensions  = len(ds.dimensions)
    assert num_weeks > 0 and num_weeks < 53
    assert num_long == NUM_LONGIDX_GLOBAL
    assert num_lat == NUM_LATIDX_GLOBAL
    assert num_dimensions == 3

    # convert lat long to index
    lat_i = int( math.ceil((90.0 - loc_lat) * NUM_LATIDX_GLOBAL / 180.25 ))
    long_deg_e = loc_long if loc_long >= 0 else 360.0 + loc_long
    long_i = int( long_deg_e * NUM_LONGIDX_GLOBAL / 360.0 )

    #print( f'{lat_i},{long_i} {loc_lat} {loc_long} {long_deg_e}' )

    assert out_data['data_specs']['start_year'] == HWITW_START_YEAR
    year_i = year - HWITW_START_YEAR
    year_is = str( year_i )

    # copy the data
    for var in ds.variables:
        # skip these
        if var in ('Week','Latitude','Longitude'):
            continue

        # split variable & subvariable names out of string
        svname = var.split('.')
        var_name = svname[0]
        sub_name = svname[1]

        # does out_data want what we have in the ds?
        if var_name not in out_data['variables']:
            print( f'{var} is not wanted in out_data' )
            exit(-1)
            continue

        if sub_name not in out_data['variables'][var_name]:
            print( f'{var} is not wanted in out_data' )
            exit(-1)
            continue

        # allocate year list if necessary
        if len( out_data['variables'][var_name][sub_name]['data'] ) <= 0:
            total_years = current_time.year - HWITW_START_YEAR
            out_data['variables'][var_name][sub_name]['data'] = [[] for _ in range(total_years)]

        #print( ds[var][:,lat_i,long_i] )
        out_data['variables'][var_name][sub_name]['data'][year_i].extend( ds[var][:num_weeks,lat_i,long_i].tolist() )
        #out_data['variables'][var_name][sub_name]['data'][year_i] = ds[var][:num_weeks,lat_i,long_i].tolist()
        #for week_i in range( num_weeks ):
        #    val = ds[var][week_i][lat_i][long_i]
        #    out_data['variables'][var_name][sub_name]['data'][year_i].append( int(val) )

    ds.close()
    pass


# get all the data for all the years for a single grid location on earth
def get_locdata( flag_args:dict, 
        loc_lat:float, loc_long:float, 
        inp_path:str, 
        start_year:int, end_year:int ) -> (dict):

    num_years = end_year - start_year
    assert num_years > 0

    # get the 'global site' data processing settings and setup output dictionary/structure
    global_site = site_settings['Global']
    out_data = copy.deepcopy(data_settings)
    site_name = f'location {loc_lat}, {loc_long}'
    out_data['data_specs'].update( [('Name',site_name)] )

    # process the years of interest
    years = list( range( start_year, end_year + 1 ) )
    for year in years:
        yidx = year - start_year
        print( f'{year} ', end='' )
        for dg_name in global_site['available_groups']:
            print( f'{dg_name} ', end='',flush=True )
            dg = data_groups[ dg_name ]
            read_data_group( flag_args, loc_lat, loc_long, inp_path, year, dg_name, dg, out_data );
        print( '' )

    return out_data


# basically a lat,long hash
def CalcQtrDegGridNum( loc_lat:float, loc_long:float ) -> int:
    grid_num = int( ((90 - loc_lat) * 4) * 360 * 4 + ((loc_long + 180) * 4) )
    return grid_num


##########################################################
# main

def main():
    print( f'** HWITW location JSON generation tool v{APP_VERSION} **\n')

    # default options
    input_path = '.'
    output_path = '.'
    start_year = 1950
    end_year = current_time.year

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-l", "--location", help = "Set location latxlong +N -W (ex. 64.0x-151.25)" )
    parser.add_argument( "-i", "--input", help = "Set input path" )
    parser.add_argument( "-o", "--output", help = "Set output path" )
    parser.add_argument( "-f", "--force", action='store_true', help = "Force recalculation of all output" )
    parser.add_argument( "-p", "--progress", action='store_true', help = "Show fancy progress" )
    parser.add_argument( "-s", "--start", help = "Set start year" )
    parser.add_argument( "-e", "--end", help = "Set end year" )
    args = parser.parse_args()

    # validate arguments
    flag_args = {
        'force_recalc':args.force,
        'show_progress':args.progress }

    show_progress = args.progress

    loc_lat = 0.0   # lat N is positive, long W is negative
    loc_long = 0.0

    if args.location:
        locstrs = args.location.split('x')
        if len(locstrs) is not 2:
            print( 'invalid location format' )
            exit( -1 )
        loc_lat = float(locstrs[ 0 ])
        loc_long = float(locstrs[ 1 ])

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

    # print location
    lat_c = 'S' if loc_lat < 0 else 'N'
    long_c = 'W' if loc_long < 0 else 'E'
    print( f'location: {abs(loc_lat)}{lat_c}, {abs(loc_long)}{long_c}' )

    # do it! get the data
    loc_dat = get_locdata( flag_args, loc_lat, loc_long, input_path, start_year, end_year )

    # write as JSON file
    gnum = CalcQtrDegGridNum( loc_lat, loc_long )
    outname = f'{output_path}/gn{gnum:07}.json'
    print( f'Output {outname} (gnum={gnum})...', end='' )
    with open( outname, 'w') as outfile:
        json.dump( loc_dat, outfile )

    print('done.')

if __name__ == '__main__':
    main()
