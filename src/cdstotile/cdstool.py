# CDS API data download tool (C) 2021 HWITW project
#
# Downloads data we are interested in from Copernicus webapi in the form of netcdf files.
# Semi intelligent.. It can't resume a partial individual file, but it knows what files
# it has sucessfully downloaded and will resume at the next file where it left off.
# It will save files to the directory that it is run from.
#
# NOTE:
# The cdsapi library looks for a file called ~/.cdsapirc that holds the auth token.
# I think the first time you run/load it, it will prompt for the token. the cds
# website explains it.
#
import math
import datetime
import dateutil
import dateutil.relativedelta
import os.path
import argparse
import glob
from cleancdsdata import remove_expver

import parsl
from parsl import python_app
from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor

DAYS_PER_YEAR = 365

# download era5 or era5 back extention data to netcdf files
def download_dataset( start_year, end_year, area_lat_long, cds_variables, force_download=False ):
    
    assert start_year <= end_year
    years = list( range( start_year, end_year + 1 ) )

    # download year & cds_variable for entire globe
    lfut = []   # store the parsl futures
    for year in reversed( years ):

        # era5 back extension goes from 1950 to 1978
        # era5 goes from 1979 to present
        if year >= 1950 and year <= 1978:
            ds_name = 'reanalysis-era5-single-levels-preliminary-back-extension'
            dir_name = 'cds_era5_backext'
        else:
            ds_name = 'reanalysis-era5-single-levels'
            dir_name = 'cds_era5'

        # handle 5 day data embargo
        end_day = DAYS_PER_YEAR
        current_date = datetime.datetime.now().date()
        era5t_end_date = current_date - datetime.timedelta( days=5 )
        if year >= era5t_end_date.year:
            end_day = era5t_end_date.timetuple().tm_yday
            
        for var_name in cds_variables:
            for day in range( 1, end_day + 1 ):
                lfut.append( download_cds_var(ds_name, dir_name, year, day, area_lat_long, var_name, force_download) )

    # Wait for the results
    [i.result() for i in lfut]
    print( 'download_dataset finished.' )
    pass

@python_app
def download_cds_var(cds_ds_name, dir_name, year, day_of_year, area_lat_long, cds_var_name, force_download=False):

    import math
    import datetime
    import os.path
    import cdsapi
    import netCDF4
    import logging

    cds = cdsapi.Client()
    # cdsapi has a logging bug that causes parsl to spit out alot of stuff we dont need
    # disable all logging
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    #clog = logging.getLogger[ 'cdsapi' ]
    logging.disable( level=logging.CRITICAL+1 )
    
    # file naming scheme
    doy_str = str( day_of_year ).zfill( 3 )
    pathname = f'./{dir_name}/{year}/{cds_var_name}/'
    filename = f'global-{year}-{doy_str}-{cds_var_name}.nc'
    fullname = pathname + filename

    # create the path if necessary
    os.makedirs(pathname, exist_ok=True)

    # remove any existing file
    if force_download:
        try:
            os.remove(fullname)
        except FileNotFoundError:
            pass

    # see if file already downloaded.. if it exists and is larger then some nonsense amount
    already_exists = os.path.isfile(fullname) and os.path.getsize(fullname) > 500
    if already_exists:
        #print(f'{filename} exists already')
        return

    req_date = datetime.date(year, 1, 1) + dateutil.relativedelta.relativedelta( days=+(day_of_year-1) )
    
    request_dict = {
        'product_type': 'reanalysis',
        'format': 'netcdf',
        'year': year,
        'variable': [cds_var_name],
        'month': req_date.month,
        'day': req_date.day,
        'time': 'all'
    }

    tempfullname = fullname + f'.tempdl'
    print(f'{filename} requested.')
    r = cds.retrieve( cds_ds_name, request_dict, tempfullname )
    ## rename completed download
    os.rename( tempfullname, fullname )
    pass
# 
# # request a month of data from cdsapi
# def cds_get_month( cds, cds_ds_name:str, cds_var_name:str, year:int, month:int, dest_file_name:str ):
#     
#     request_dict = {
#         'product_type': 'reanalysis',
#         'format': 'netcdf',
#         'year': year,
#         'variable': [cds_var_name],
#         'month': month,
#         'day': [str(i) for i in range( 1, 32 )],
#         'time': 'all'
#     }
#     temp_month_fullname = dest_file_name + f'.tempdl-{month}'
#     print(f'{dest_file_name}-{month} requested.')
#     #print( f'debug: {request_dict}' )
#     r = cds.retrieve( cds_ds_name, request_dict, temp_month_fullname )
#     remove_expver( temp_month_fullname )
#     # concat completed download
#     concat_month( dest_file_name, temp_month_fullname )
# 
# # request a partial month of data
# def cds_get_partmonth( cds, cds_ds_name:str, cds_var_name:str, year:int, month:int, end_day:int, dest_file_name:str ):
#     
#     start_day = 1
#     request_dict = {
#         'product_type': 'reanalysis',
#         'format': 'netcdf',
#         'year': year,
#         'variable': [cds_var_name],
#         'month': month,
#         'day': [str(i) for i in range( 1, end_day+1 )],
#         'time': 'all'
#     }
#     temp_month_fullname = dest_file_name + f'.tempdl-{month}'
#     print(f'{dest_file_name}-{month} partial requested.')
#     #print( f'debug: {request_dict}' )
#     r = cds.retrieve( cds_ds_name, request_dict, temp_month_fullname )    
#     remove_expver( temp_month_fullname )
#     # concat completed download
#     concat_month( dest_file_name, temp_month_fullname )
#     
# 
# # get the last datetime present in a netcdf
# def nc_last_datetime( filename:str ):
#      # open for read
#     try:
#         nds = netCDF4.Dataset( filename, 'r' )
# 
#     except OSError:
#         print( f'{filename} could not be opened!' )
#         exit(-1)
# 
#     tvar = nds.variables['time']
#     last_hour = tvar[-1]
#     ldt = netCDF4.num2date( last_hour, tvar.units, tvar.calendar, only_use_cftime_datetimes=False )
#     nds.close()
#     return ldt
# 
# def nc_first_datetime( filename:str ):
#      # open for read
#     try:
#         nds = netCDF4.Dataset( filename, 'r' )
# 
#     except OSError:
#         print( f'{filename} could not be opened!' )
#         exit(-1)
# 
#     tvar = nds.variables['time']
#     last_hour = tvar[0]
#     ldt = netCDF4.num2date( last_hour, tvar.units, tvar.calendar, only_use_cftime_datetimes=False )
#     nds.close()
#     return ldt
# 
# # get the first hour present in a netcdf
# def nc_first_hour( filename:str ):
#      # open for read
#     try:
#         nds = netCDF4.Dataset( filename, 'r' )
# 
#     except OSError:
#         print( f'{filename} could not be opened!' )
#         exit(-1)
# 
#     tvar = nds.variables['time']
#     first_hour = tvar[0]
#     fdt = netCDF4.num2date( last_hour, tvar.units, tvar.calendar, only_use_cftime_datetimes=False )
#     nds.close()
#     return fdt
# 
# # trim a netcdf of any values at time >= first_
# def nc_trim_hours( filename:str, first_dt ):
# 
#     tname = filename + '.temptrim'
#     ds = xarray.open_dataset( filename, chunks={'time':52} )
#     end0_dt = first_dt - datetime.timedelta( minutes=1 )
#     dss = ds.sel( time=slice('1900-01-01', end0_dt))
#     if dss.sizes['time'] >= ds.sizes['time']:
#         return  # nothing to trim
#     
#     dss.to_netcdf( tname )#, encoding={'time':{'units': "hours since 1900-01-01 00:00:00.0"}} )
#     ds.close()
#     dss.close()
#     os.rename( tname, filename )
# 
# # concatenate a netcdf onto another netcdf using xarray.open_mfdataset
# def concat_month( destfilename:str, srcfilename:str ):
# 
#     import xarray
#     
#     already_exists = os.path.isfile( destfilename )
#     if not already_exists:
#         # for the first month, just rename src file as dest
#         os.rename( srcfilename, destfilename )
#         return
# 
#     # trim dest so it doesn't overlap with src. xarray doesn't like that.
#     src_dt = nc_first_datetime( srcfilename )
#     nc_trim_hours( destfilename, src_dt )
# 
#     # concatenate src onto dest
#     temp_filename = destfilename + '.concat'
# 
#     ds = xarray.open_mfdataset(
#         [destfilename, srcfilename],
#         combine ='by_coords',
#         chunks={'time': 52} )
#     # Export netcdf file, have to force xarray to keep our time unit thus the encoding parameter.
#     ds.to_netcdf( temp_filename, encoding={'time':{'units': "hours since 1900-01-01 00:00:00.0"}} )
#     ds.close()
#     # fix name of finished dest file
#     os.rename( temp_filename, destfilename )
#     # remove the src file
#     os.remove( srcfilename )
#     pass

# clean up downloaded files
def clean_dataset( dir_name:str ):
    print( f'cleaning dataset {dir_name}...' )
    # look for any .nc files and remove expver from them
    pathname = './' + dir_name + '/**/*.nc'
    for fname in glob.iglob( pathname, recursive=True ):
        remove_expver( fname )
    pass

def main():
    '''Main program to download data from Copernicus.'''

    # Configure parsl to use a local thread pool
    # debug - disable parsl until new changes more stable
    local_threads = Config(
        executors=[ 
            ThreadPoolExecutor( max_threads=5, label='local_threads')
        ]
    )
    parsl.clear()
    parsl.load(local_threads)

    app_version = "1.0"
    current_time = datetime.datetime.now()
    start_year = 1950
    end_year = current_time.year
    force_download = False;

    # hello
    print( f'** HWITW Copernicus data download tool v{app_version} **\n')

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-f", "--forcedownload", action='store_true', help = "Force download overwriting existing files" )
    parser.add_argument( "-s", "--startyear", help = "Set start year" )
    parser.add_argument( "-e", "--endyear", help = "Set end year" )
    parser.add_argument( "-c", "--cleanonly", action='store_true', help = "Dont downoad, just clean data already downloaded" )
    #parser.add_argument( "-l", "--era5t", action='store_true', help = "Force download this year and last year" )
    args = parser.parse_args()

    force_download = args.forcedownload
    clean_only = args.cleanonly

    if args.startyear:
        start_year = int(args.startyear)

    if args.endyear:
        end_year = int(args.endyear)

    '''if args.latest:
        start_year = current_time.year - 1
        end_year = current_time.year
        force_download = True
    '''

    # 0.25 degree resolution. N positive, W negative
    #inp_lat = 59.64 # homer ak
    #inp_long = -151.54

    # get the containing cell 
    #lat0 = math.ceil( inp_lat * 4 ) / 4
    #lat1 = (math.floor( inp_lat * 4 ) / 4) + 0.01 # edge is not inclusive
    #long0 = math.floor( inp_long * 4 ) / 4
    #long1 = (math.ceil( inp_long * 4 ) / 4) - 0.01
    #area0 = [ lat0, long0, lat1, long1 ]
    area0 = None  # we are doing global downloads!

    # the era5 variables we are interested in
    variables = [
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_dewpoint_temperature',
        '2m_temperature',
        'cloud_base_height',
        'precipitation_type',
        'surface_pressure',
        'total_cloud_cover',
        'total_precipitation',
    ]

    if not clean_only:
        # download netcdfs from CDS
        download_dataset( start_year, end_year, area0, variables, force_download )
    # clean up any expver data that might be present in downloaded files
    clean_dataset( 'cds_era5' )
    print( 'done.' )


if __name__ == "__main__":
    main()

