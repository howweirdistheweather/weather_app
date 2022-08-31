# CDS API data download tool (C) 2021 HWITW project
#
# Downloads data we are interested in from Copernicus webapi in the form of netcdf files.
# Semi intelligent.. It can't resume a partial individual file, but it knows what files
# it has sucessfully downloaded and will resume at the next file where it left off.
# It will save files to the directory that it is run from.
#
# NOTE:
# The cdsapi library looks for a file called ~/.cdsapirc that holds the auth token.
# I think the first time you run/load it, it will prompt for the token. I forget.. the cds
# website explains it.
#
import math
import datetime
import dateutil
import os.path
import cdsapi
import netCDF4
import argparse
import numpy

import parsl
from parsl import python_app
from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor

# download era5 or era5 back extention data to netcdf files
def download_dataset( start_year, end_year, area_lat_long, variables, force_download=False ):
    '''
    Download a multi-year dataset.
    :param ds_name: The dataset name to be downloaded from CDS
    :param dir_name: name of the directory to save downloaded files for the dataset
    :param start_year: the first year of the range for downloads
    :param end_year: the last year of the range for downloads
    :param area_lat_long: The area to be downloaded, or None for global
    :param variables: List of variables to be downloaded
    :param force_download: Download file even if it already exists locally
    '''
    assert start_year <= end_year
    years = list( range( start_year, end_year + 1 ) )

    # download year, variable for entire globe
    for year in reversed( years ):

        # era5 back extension goes from 1950 to 1978
        # era5 goes from 1979 to present
        if year >= 1950 and year <= 1978:
            ds_name = 'reanalysis-era5-single-levels-preliminary-back-extension'
            dir_name = 'cds_era5_backext'
        else:
            ds_name = 'reanalysis-era5-single-levels'
            dir_name = 'cds_era5'

        for var_name in variables:
            download_var_for_year( ds_name, dir_name, year, area_lat_long, var_name, force_download)
            #print_var_for_year( ds_name, dir_name, year, area_lat_long, var_name, force_download)
            print(f'Submitted {var_name} for {year}: {ds_name}')

#@python_app
def print_var_for_year(ds_name, dir_name, year, area_lat_long, var_name, force_download=False):
    '''Test method for debugging parsl operation.'''
    import time
    time.sleep(5)
    print(f'Processing {var_name} for {year}: {ds_name}')

#@python_app
def download_var_for_year(ds_name, dir_name, year, area_lat_long, var_name, force_download=False):
    '''
    Download a single year dataset for a single variable.
    :param ds_name: The dataset name to be downloaded from CDS
    :param dir_name: name of the directory to save downloaded files for the dataset
    :param year: the year to be downloaded
    :param area_lat_long: The area to be downloaded, or None for global
    :param var_name: The name of the variable to be downloaded
    :param force_download: Download file even if it already exists locally
    '''

    import math
    import datetime
    import os.path
    import cdsapi
    import netCDF4

    cds = cdsapi.Client()

    # file naming scheme
    pathname = f'./{dir_name}/{year}/'
    filename = f'global-{year}-{var_name}.nc'
    fullname = pathname + filename

    # see if file already downloaded.. if it exists and is larger then some nonsense amount
    already_exists = os.path.isfile(fullname) and os.path.getsize(fullname) > 500
    if already_exists:
        print(f'{filename} exists already')
        # todo: validate the existing netcdf file

    if not already_exists or force_download:
        print(f'{filename} requested...')
        # remove any existing file
        try:
            os.remove(fullname)
        except FileNotFoundError:
            pass
        # create the path if necessary
        os.makedirs(pathname, exist_ok=True)

        # download to temp file then rename to mark as completed.
        # So - There is ERA5 data (expver=1), and ERA5T data(expver=5). Every month a month of
        # ERA5T data becomes ERA5. In other words 1950 to now minus 3 months is ERA5. Anything
        # newer is ERA5T.
        # And if downloading ERA5T, we have to respect 5day embargo on latest data. So it is
        # NOW minus 5 days for the newest available.
        # I am solving this request issue by requesting month data for the latest year(s).
        # The final month request is for a partial set of days - up to a full month.
        # Doing it this way makes it easy to cat the files together into a year file. We don't
        # have to deal with the expver column.
        cur_date = datetime.datetime.now().date()
        era5_end_date = cur_date - dateutil.relativedelta.relativedelta( months=3 )
        era5_end_date = era5_end_date.replace( day=31 )

        if year < era5_end_date.year:
            # request a full year of ERA5
            request_dict = {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'year': year,
                'time': 'all',
                'variable': [var_name]
                #'area': area_lat_long,
            }

            tempfullname = fullname + '.tempdl'
            r = cds.retrieve( ds_name, request_dict, tempfullname )
            # rename completed download
            os.rename(tempfullname, fullname)

        else:
            # request by month. could be era5 or era5t
            start_month = 1
            end_month = 12
            era5t_end_date = cur_date - datetime.timedelta( days=5 )

            if year >= era5t_end_date.year:
                end_month = era5t_end_date.month

            tempfullname = fullname + f'.tempdl'
            for month in range( start_month, end_month ):
                request_dict = {
                    'product_type': 'reanalysis',
                    'format': 'netcdf',
                    'year': year,
                    'variable': [var_name],
                    'month': month,
                    'day': [str(i) for i in range( 1, 32 )],
                    'time': 'all'
                }

                temp_month_fullname = fullname + f'.tempdl-{month}'
                r = cds.retrieve( ds_name, request_dict, temp_month_fullname )
                # concat completed download
                concat_month( tempfullname, temp_month_fullname )

            # the final month could be partial set of days up to a whole months worth.
            start_day = 1
            end_day = era5t_end_date.day+1
            request_dict = {
                    'product_type': 'reanalysis',
                    'format': 'netcdf',
                    'year': year,
                    'variable': [var_name],
                    'month': end_month,
                    'day': [str(i) for i in range( 1, end_day+1 )],
                    'time': 'all'
                }

            tempfullname = fullname + f'.tempdl-{end_month}'
            r = cds.retrieve( ds_name, request_dict, temp_month_fullname )
            # concat completed download
            concat_month( tempfullname, temp_month_fullname )
            # rename completed download
            os.rename( tempfullname, fullname )
    pass

# put monthly netcdf downloads together
def concat_month( destfilename:str, srcfilename:str ):

    import xarray

    already_exists = os.path.isfile( destfilename )
    if not already_exists:
        # for the first month, just copy src to dest
        os.rename( srcfilename, destfilename )
        return

    # concatenate src with dest
    temp_filename = destfilename + '.concat'
    ds = xarray.open_mfdataset( [destfilename, srcfilename], combine ='by_coords' )
    ds.to_netcdf( temp_filename )  # Export netcdf file
    ds.close()
    # fix name
    os.rename( temp_filename, destfilename )
    # remove the src file
    os.remove( srcfilename )
    pass

'''
# get rid of the expver stuff..
# newest ERA5 data has an experiment version dimension with 2 coordinates.
# the data is spread across the 2 columns
def remove_expver( filename:str ):

     # open for read/write
    try:
        ds = netCDF4.Dataset( filename, 'a' )

    except OSError:
        print( f'{filename} could not be opened!' )
        exit(-1)

    if 'expver' not in ds.dimensions:
        return

    short_var_name = list(ds.variables)[4]
    print( f'removing expvar for {short_var_name}' )
    data = ds[short_var_name]
    # convert invalids to 0
    data[:, :, :, 0] = data[:, :, :, 0] + data[:, :, :, 1]
    # = numpy.ma.filled( data, 0 )

    #data[:,:,:,0] = data[:,:,:,0] if not math.isnan( data[:,:,:,0] ) else data[:,:,:,0]

    #numpy.transpose( ds[ short_var_name ][hr_0:hr_1][:][:][:], axes=(2, 3, 0, 1) )
    # convert invalids to 0
    #var_week = numpy.ma.filled( var_week, 0 )
    # sum columns on dimension 3 and then drop expvar column
    #data = numpy.delete( data, 1, axis=3 )
    ds.close()
    pass
'''

def main():
    '''Main program to download data from Copernicus.'''

    # Configure parsl to use a local thread pool
    local_threads = Config(
        executors=[ 
            ThreadPoolExecutor( max_threads=1, label='local_threads')
        ]
    )
    parsl.clear()
    parsl.load(local_threads)

    app_version = "0.96"
    current_time = datetime.datetime.now()
    start_year = 1950
    end_year = current_time.year
    force_download = False;

    # hello
    print( f'** HWITW Copernicus data download tool v{app_version} **\n')

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-f", "--forcedownload", action='store_true', help = "Force download even if file already exists" )
    parser.add_argument( "-s", "--start", help = "Set start year" )
    parser.add_argument( "-e", "--end", help = "Set end year" )
    parser.add_argument( "-l", "--latest", action='store_true', help = "Force download this year and last year" )
    args = parser.parse_args()

    force_download = args.forcedownload

    if args.start:
        start_year = int(args.start)

    if args.end:
        end_year = int(args.end)

    if args.latest:
        start_year = current_time.year - 1
        end_year = current_time.year
        force_download = True


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

    download_dataset( 1950, current_time.year, area0, variables, force_download )


if __name__ == "__main__":
    main()

