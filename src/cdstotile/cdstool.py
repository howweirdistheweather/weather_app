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
def download_dataset( output_path:str, start_year:int, end_year:int,
                      area_lat_long, cds_variables, force_download=False ):
    
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
                lfut.append(
                    download_cds_var( output_path, ds_name, dir_name, year, day,
                                      area_lat_long, var_name, force_download)
                )

    # Wait for the results
    [i.result() for i in lfut]
    print( 'download_dataset finished.' )
    pass

@python_app
def download_cds_var( output_path:str, cds_ds_name, dir_name, year, day_of_year,
                      area_lat_long, cds_var_name, force_download=False):

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
    pathname = f'{output_path}/{dir_name}/{year}/{cds_var_name}/'
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
        #'time': 'all'
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
    }

    tempfullname = fullname + f'.tempdl'
    print(f'{filename} requested.')
    r = cds.retrieve( cds_ds_name, request_dict, tempfullname )
    ## rename completed download
    os.rename( tempfullname, fullname )
    pass


# clean up downloaded files
def clean_dataset( nc_path:str, dir_name:str, start_year:int, end_year:int ):
    for year in range(start_year,end_year+1):
        print( f'cleaning dataset {dir_name} {year}...' )
        # look for any .nc files and remove expver from them
        #pathname = nc_path + '/' + dir_name + '/**/*.nc'
        pathname = nc_path + '/' + dir_name + f'/{year}/**/*.nc'
        print( f'debug: ' + pathname )
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

    app_version = "0.9.6"
    current_time = datetime.datetime.now()
    start_year = 1950
    end_year = current_time.year
    force_download = False
    output_path = '.'

    # hello
    print( f'** HWITW Copernicus data download tool v{app_version} **\n')

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument( "-f",
                        "--forcedownload",
                         action='store_true',
                         help = "Force download overwriting existing files" )
    parser.add_argument( "-s", "--startyear", help = "Set start year" )
    parser.add_argument( "-e", "--endyear", help = "Set end year" )
    parser.add_argument( "-c",
                         "--cleanonly",
                         action='store_true',
                         help = "Dont downoad, just clean data already downloaded" )
    parser.add_argument( "-o", "--output", help = "Set output path" )
    args = parser.parse_args()

    force_download = args.forcedownload
    clean_only = args.cleanonly

    if args.startyear:
        start_year = int(args.startyear)

    if args.endyear:
        end_year = int(args.endyear)

    if args.output:
        output_path = args.output

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
        download_dataset( output_path, start_year, end_year, area0, variables, force_download )

    # clean up any expver data that might be present in downloaded files
    clean_dataset( output_path, 'cds_era5', start_year, end_year )
    print( 'done.' )


if __name__ == "__main__":
    main()

