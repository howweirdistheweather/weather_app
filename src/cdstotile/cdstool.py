import os.path
import cdsapi
import netCDF4

cds = cdsapi.Client()
app_version = "0.91"
force_download = False;

# the variables we are interested in
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

# the years we want. era5 back extension goes from 1950 to 1978
era5_start_year = 1950
era5_end_year = 1955#1978
years = list( range( era5_start_year, era5_end_year + 1 ) )

# hello
print( f'** ][WITW Copernicus data download tool v{app_version}**\n')

for year in years:
    for var_name in variables:
        # file naming scheme
        pathname = f'./cds_era5_backext/{year}/'
        filename = f'global-{year}-{var_name}.nc'
        fullname = pathname + filename

        # see if file already downloaded.. if it exists and is larger then some nonsense amount
        already_exists = os.path.isfile( fullname ) and os.path.getsize( fullname ) > 500
        if already_exists:
            print( f'{filename} exists already' )
            # todo: validate the existing netcdf file
            # # check if it is a valid complete download by trying to load it
            # try:
            #     ds = netCDF4.Dataset( fullname )
            # except OSError:
            #     print( f'{filename} is not a valid netcdf' )
            #     already_exists = False;

        if not already_exists or force_download:
            print( f'{filename} requested...')
            # remove any existing file
            try:
                os.remove( fullname )
            except FileNotFoundError:
                pass
            # create the path if necessary
            os.makedirs( pathname, exist_ok=True )

            # download to temp file
            tempfullname = fullname + '.tempdl' 
            r = cds.retrieve(
                'reanalysis-era5-single-levels-preliminary-back-extension',
                {
                    'product_type': 'reanalysis',
                    'format': 'netcdf',
                    'year': [year],
                    'time': 'all',
                    'variable': [ var_name ]
                }, tempfullname )
            #r.download()
            # rename completed download
            os.rename( tempfullname, fullname )

