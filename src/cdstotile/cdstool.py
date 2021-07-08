import os.path
import cdsapi

cds = cdsapi.Client()

#cell_lat = 59.5
#cell_long = -151.75
app_version = "0.9"
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

# the years we want
era5_start_year = 1950
era5_end_year = 1951#1978
years = list( range( era5_start_year, era5_end_year + 1 ) )

# hello
print( f'** ][WITW Copernicus data download tool v{app_version}**\n')

for var_name in variables:
    for year in years: 
        # file naming scheme
        pathname = f'./cds_era5_backext/{year}/'
        filename = f'global-{year}-{var_name}.nc'
        fullname = pathname + filename

        # see if file already downloaded.. if it exists and is larger then some nonsense amount
        already_exists = os.path.isfile( fullname ) and os.path.getsize( fullname ) > 100
        if already_exists:
            print( f'{filename} exists already' )

        if not already_exists or force_download:
            print( f'{filename} requested...')
            # remove any existing file & create the path
            try:
                os.remove( fullname )
            except FileNotFoundError:
                pass 
            os.makedirs( pathname, exist_ok=True )

            # download to file
            r = cds.retrieve(
                'reanalysis-era5-single-levels-preliminary-back-extension',
                {
                    'product_type': 'reanalysis',
                    'format': 'netcdf',
                    'year': [year],
                    'time': 'all',
                    'variable': [ var_name ]
                }, fullname )
            #r.download()







# r = cds.retrieve(
#     'reanalysis-era5-single-levels-preliminary-back-extension',
#     {
#         'product_type': 'reanalysis',
#         'format': 'netcdf',
#         'year': [1950],#list(range(1950, 1978 + 1)),
#         #'month': '01',
#         #'day': '01',
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'variable': [
#             '10m_u_component_of_wind'
#             # '10m_v_component_of_wind',
#             # '2m_dewpoint_temperature',
#             # '2m_temperature',
#             # 'cloud_base_height',
#             # 'precipitation_type',
#             # 'surface_pressure',
#             # 'total_cloud_cover',
#             # 'total_precipitation',
#         ],
#         'area': [
#             cell_lat+0.2499, cell_long+0.2499,
#             cell_lat, cell_long,
#         ],
#     }, )
#     #'download.nc')
