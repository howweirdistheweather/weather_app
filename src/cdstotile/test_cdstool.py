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
import os.path
import cdsapi
import netCDF4

import parsl
from parsl import python_app
from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor

from location_settings import site_settings
from data_groups import data_groups

# download era5 or era5 back extention data to netcdf files
def download_dataset( ds_name, dir_name, start_year, end_year, area_lat_long, variables, force_download=False ):
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
    years = list( range( start_year, end_year + 1 ) )
    # # calculate a unique number for each quarter degree on the planet.
    # # makes having a unique filename for the coordinates simpler.
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    print( f'Downloading {ds_name} {area_lat_long} (gn{grid_num}) from {start_year} to {end_year}')

    # download year, variable for entire globe
    for year in reversed( years ):
        for var_name in variables:
            download_var_for_year( ds_name, dir_name, year, area_lat_long, var_name, grid_num, force_download)
            #print_var_for_year( ds_name, dir_name, year, area_lat_long, var_name, force_download)
            print(f'Submitted {var_name} for {year}: {ds_name}')

@python_app
def print_var_for_year(ds_name, dir_name, year, area_lat_long, var_name, force_download=False):
    '''Test method for debugging parsl operation.'''
    import time
    time.sleep(5)
    print(f'Processing {var_name} for {year}: {ds_name}')

@python_app
def download_var_for_year(ds_name, dir_name, year, area_lat_long, var_name, grid_num, force_download=False):
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
    filename = f'gn{grid_num}-{year}-{var_name}.nc'
    #filename = f'global-{year}-{var_name}.nc'
    fullname = pathname + filename

    # see if file already downloaded.. if it exists and is larger then some nonsense amount
    already_exists = os.path.isfile(
        fullname) and os.path.getsize(fullname) > 500
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

        # download to temp file
        tempfullname = fullname + '.tempdl'
        r = cds.retrieve(
            ds_name,
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'year': year,
                'time': 'all',
                'variable': [var_name],
                'area': area_lat_long,
            }, tempfullname)
        # rename completed download
        os.rename(tempfullname, fullname)


# 0.25 degree resolution

def main(name, end_year, inp_lat, inp_long, available_groups, output_raw_years):
    '''Main program to download data from Copernicus.'''

    # Configure parsl to use a local thread pool
    local_threads = Config(
        executors=[ 
            ThreadPoolExecutor( max_threads=5, label='local_threads') 
        ]
    )
    parsl.clear()
    parsl.load(local_threads)

    app_version = "0.94"
    force_download = False;
    current_time = datetime.datetime.now()

    # hello
    print( f'** HWITW Copernicus data download tool v{app_version} **\n')
    print( f'Processing {name}')

    # get the containing cell 
    lat0 = math.ceil( inp_lat * 4 ) / 4
    lat1 = (math.floor( inp_lat * 4 ) / 4) + 0.01 # edge is not inclusive
    long0 = math.floor( inp_long * 4 ) / 4
    long1 = (math.ceil( inp_long * 4 ) / 4) - 0.01

    area0 = [ lat0, long0, lat1, long1 ]
    #area0 = None  # we are doing global downloads!

    # A few variables we haven't implemented that sound cool:
        #'forecast_albedo',
        #'sea_ice_cover',
        #'snow_depth',

    variables = []
    for data_group in available_groups:
        variables += [file[0] for file in data_groups[data_group]['files']]
    print(f"Downloading {variables} for site {name}")

    # era5 back extension goes from 1950 to 1978
    download_dataset(   'reanalysis-era5-single-levels-preliminary-back-extension',
                        'cds_era5_backext',
                        1950, 1978,
                        area0, variables, force_download )

    # era5 goes from 1979 to present
    download_dataset(   'reanalysis-era5-single-levels',
                        'cds_era5',
                        1979, current_time.year,
                        area0, variables, force_download )


if __name__ == "__main__":
    main(**site_settings['Seattle'])

