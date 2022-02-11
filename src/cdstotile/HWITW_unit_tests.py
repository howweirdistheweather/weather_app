import copy
import os
from test_tiletool import *
from data_groups import *
from location_settings import *
from generate_HWITW_stats import *

inp_lat = site_settings['Seldovia']['inp_lat']
inp_long = site_settings['Seldovia']['inp_long']

lat0 = math.ceil(inp_lat * 4) / 4
lat1 = (math.floor(inp_lat * 4) / 4)  # + 0.01 # edge is not inclusive
long0 = math.floor(inp_long * 4) / 4
long1 = (math.ceil(inp_long * 4) / 4)  # - 0.01

area0 = [lat0, long0, lat1, long1]

grid_num = int( ((area0[0] + 90) * 4) * 360 * 4 + ((area0[1] + 180) * 4) )

year = 1989

def load_file(filename, key):
    already_exists = os.path.isfile(filename)  # and os.path.getsize( fullname ) > 500
    if not already_exists:
        print(bcolors.WARNING + f'{filename} is missing!' + bcolors.ENDC)
    print(f'processing {filename}')
    try:
        ds = netCDF4.Dataset(filename)
    except OSError:
        print(bcolors.FAIL + f'{filename} could not be opened!' + bcolors.ENDC)
        exit(-1)
    return universal_flatten_cds(ds[key])

def test_temp_RH():
    temp_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-2m_temperature.nc','t2m')
    DP_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-2m_dewpoint_temperature.nc', 'd2m')
    test_data = numpy.zeros((2,HOURS_PER_WEEK), dtype=float)
    test_data[0] = temp_raw[0:HOURS_PER_WEEK]
    test_data[1] = DP_raw[0:HOURS_PER_WEEK]
    test_results = do_temp_dp(test_data, area0) #A dict like {"temperature":{"min":xxx,"p10":...},"relative_humidity":{"p10":xxx,"p50":...}}
    test_results_decompressed = copy.deepcopy(test_results) #Will be overwritten by decompressed values
    for variable,details in test_results_decompressed.items():
        for statistic, value in details.items():
            test_results_decompressed[variable][statistic] = data_settings_internal['flat_functions'][f'inverse_{variable}_{statistic}'](value)
    #Compare to values computed in excel:
    independent_values = {
        "temperature":{
            "min":-2.428058784,
            "p10":-1.273427306,
            "avg":0.933304887,
            "p90":3.10403466,
            "max":4.274579895,
            "day_avg":0.944513981,
            "night_avg":0.922095792,
            "range_avg":2.158376965
        },
        "relative_humidity":{
            "p10":0.89755,
            "p50":0.94093,
            "p90":0.97510
        }
    }
    for variable,details in test_results_decompressed.items():
        for statistic, value in details.items():
            independent = independent_values[variable][statistic]
            print(f'For {variable} {statistic}: {value} vs. {independent} ({round(value/independent*100)}%)')

test_temp_RH()

