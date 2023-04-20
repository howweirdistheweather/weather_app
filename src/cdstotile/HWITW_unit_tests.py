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

import os
import netCDF4
#from test_tiletool import * #This should be eliminated so that test_tiletool.py
from data_settings import *
from location_settings import *
from generate_HWITW_stats import *

location = "Seldovia"
inp_lat = site_settings[location]['inp_lat']
inp_long = site_settings[location]['inp_long']

lat0 = math.ceil(inp_lat * 4) / 4
lat1 = (math.floor(inp_lat * 4) / 4)  # + 0.01 # edge is not inclusive
long0 = math.floor(inp_long * 4) / 4
long1 = (math.ceil(inp_long * 4) / 4)  # - 0.01

area0 = [lat0, long0, lat1, long1]

grid_num = int( ((area0[0] + 90) * 4) * 360 * 4 + ((area0[1] + 180) * 4) )

year = 1989

def test_similarity(variable, statistic, processed, independent, verbose=False):
    cmp_name = data_settings['variables'][variable][statistic]['compression']
    cmp_info = data_settings['compression'][cmp_name]
    cmp_type = cmp_info['type']
    cmp_scale = cmp_info['scale']
    if cmp_type == 'linear':
        try: assert abs(processed-independent) < cmp_scale*2
        except AssertionError as error_text:
            print(f'{processed} too dissimilar to {independent}: difference {abs(processed-independent)} greater than threshold {cmp_scale*2}')
            print(error_text)
            raise AssertionError
        if verbose:
            print(f'Comparing {variable} {statistic} processed: {processed} (via {cmp_type}), independent: {independent}, difference: {abs(processed-independent)}, 2x scale: {2*cmp_scale}')
    elif cmp_type in ['parabolic', 'signed_parabolic']:
        try:
            assert processed == independent or \
                   0.95 < processed/independent < 1.05 or \
                   (math.sqrt(independent) < cmp_scale*3 and math.sqrt(processed) < cmp_scale*3)
        except AssertionError as error_text:
            print(f'{processed} too dissimilar to {independent}: ratio {processed/independent} > 5% different and sqrt source ({math.sqrt(independent)}) > {cmp_scale*3}.')
            print(error_text)
            raise AssertionError
        if verbose:
            if independent > 0:
                if math.sqrt(independent) > cmp_scale * 3:
                    print(f'Comparing {variable} {statistic} processed: {processed} (via {cmp_type}), independent: {independent}, ratio: {processed/independent}, scale: {cmp_scale}')
                else: print(f'Independent value {independent} close enough to zero relative to scale {cmp_scale} that a larger discrepancy is acceptable as long as processed {processed} is also close to zero.')
            else: print(f'Both processed {processed} and independent {independent} are zero.')

def load_file(filename, key, flatten_function):
    already_exists = os.path.isfile(filename)  # and os.path.getsize( fullname ) > 500
    if not already_exists:
        print(f'{filename} is missing!' + bcolors.ENDC)
    print(f'processing {filename}')
    try:
        ds = netCDF4.Dataset(filename)
    except OSError:
        print(f'{filename} could not be opened!' + bcolors.ENDC)
        exit(-1)
    return flatten_function(ds[key])

def compare_test_results(test_results, independent_values, verbose=False):
    test_results_decompressed = copy.deepcopy(test_results) #Will be overwritten by decompressed values
    for variable,details in test_results_decompressed.items():
        for statistic, value in details.items():
            test_results_decompressed[variable][statistic] = data_settings_internal['flat_functions'][f'inverse_{variable}_{statistic}'](value)
    #Compare to values computed in excel:
    for variable,details in test_results_decompressed.items():
        for statistic, value in details.items():
            independent = independent_values[variable][statistic]
            test_similarity(variable,statistic,value,independent, verbose)

def test_temp_RH(flatten_function, verbose=False):
    temp_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-2m_temperature.nc','t2m', flatten_function)
    DP_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-2m_dewpoint_temperature.nc', 'd2m', flatten_function)
    test_data = numpy.zeros((2,HOURS_PER_WEEK), dtype=float)
    test_data[0] = temp_raw[0:HOURS_PER_WEEK]
    test_data[1] = DP_raw[0:HOURS_PER_WEEK]
    test_results = do_temp_dp(test_data, area0) #A dict like {"temperature":{"min":xxx,"p10":...},"relative_humidity":{"p10":xxx,"p50":...}}
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
    compare_test_results(test_results, independent_values, verbose)

def test_wind(flatten_function, verbose=False):
    U_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-10m_u_component_of_wind.nc', 'u10', flatten_function)
    V_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-10m_v_component_of_wind.nc', 'v10', flatten_function)
    test_data = numpy.zeros((2,HOURS_PER_WEEK), dtype=float)
    test_data[0] = U_raw[0:HOURS_PER_WEEK]
    test_data[1] = V_raw[0:HOURS_PER_WEEK]
    test_results = do_wind(test_data, area0)
    independent_values = {"wind":{
        "speed_avg":8.480671507,
        "speed_max":15.88650145,
        "speed_net":2.102308947,
        "dir_net":340.0535809,
        "dir_modal":272 #2-degree bin width
    }}
    compare_test_results(test_results, independent_values, verbose)

def test_precip(flatten_function, verbose=False):
    amount_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-total_precipitation.nc', 'tp', flatten_function)
    type_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-precipitation_type.nc', 'ptype', flatten_function)
    test_data = numpy.zeros((2,HOURS_PER_WEEK), dtype=float)
    test_data[0] = amount_raw[0:HOURS_PER_WEEK]
    test_data[1] = type_raw[0:HOURS_PER_WEEK]
    test_results = do_precip(test_data, area0)
    independent_values = {
        "precipitation":{
            "total":0.060222441,
            "total_rain":0.026671887,
            "total_snow":0.0000611576,
            "total_wet_snow":0.033482141,
            "total_ice_pellets":0,
            "total_freezing_rain":0,
            "p90":0.001120499,
            "max":0.003818076
        }
    }
    compare_test_results(test_results, independent_values, verbose)

def test_cloud_cover(flatten_function, verbose=False):
    clouds_raw = load_file(f'./cds_era5/{year}/gn{grid_num}-{year}-total_cloud_cover.nc', 'tcc', flatten_function)
    test_data = numpy.zeros((1,HOURS_PER_WEEK), dtype=float)
    test_data[0] = clouds_raw[0:HOURS_PER_WEEK]
    test_results = do_cloud_cover(test_data, area0)
    independent_values = {
        "cloud_cover":{
            "p25":0.584987716,
            "p50":0.993346863,
            "p75":1.0,
            "p_sunny":0.041666667,
            "p_cloudy":0.636904762
        }
    }
    compare_test_results(test_results, independent_values, verbose)

def test_all(flatten_function, verbose=False):
    print(f'  Testing statistics, compression, and decompression code using {location} in {year} (first week of year). For example reading ./cds_era5/{year}/gn{grid_num}-{year}-2m_temperature.nc')
    test_temp_RH(flatten_function, verbose=verbose)
    test_wind(flatten_function, verbose=verbose)
    test_precip(flatten_function, verbose=verbose)
    test_cloud_cover(flatten_function, verbose=verbose)
    print('  Unit tests completed successfully')