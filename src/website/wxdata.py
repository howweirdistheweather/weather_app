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

# get weather data for the webapp
#
import json
import numpy
import os
import wxdb_reader as wxdb
from collections import defaultdict

def get_data_path():
    output_dir = os.getenv(key='DATA_OUTPUT_DIR', default=".")
    wxdb_file = 'hwitw.wxdb'
    path = os.path.join(output_dir, wxdb_file)
    return(path)


def wxdata_to_dict( var_table:list, ldata:numpy.array ) -> dict:
    ldict = json.loads( wxdb.read_src_datasettings_json() )
    # build the weather data into the dict
    var_idx = 0
    for var_name in var_table:
        major_vn, minor_vn = var_name.split('.')
        ldict['variables'][major_vn][minor_vn]['data'] = ldata[:,:,var_idx].tolist()
        var_idx += 1
    return ldict


def get_wxvar_list():
    wxvt = wxdb.open_wxdb( get_data_path() )
    wxdb.close_wxdb()
    return wxvt


def get_wxvar( lat_n:float, long_e:float ):
    print( f'debug: request lat {lat_n}, long {long_e}' )

    # #for debugging
    # directly return a json from a file
    # with open( 'Seldovia.json', 'r') as infile:
    #     wxvar_json = infile.read()
    #     infile.close()
    # return wxvar_json

    if -91 <= lat_n <= 91 and -181 <= long_e <= 181:
        wxvt = wxdb.open_wxdb_ro( get_data_path() )
        try:
            loc_data = wxdb.read_wxdb( lat_n, long_e )
            ld_dict = wxdata_to_dict( wxvt, loc_data )
            site_name = f'location {lat_n}, {long_e}'
            ld_dict['data_specs'].update( [('Name',site_name)] )
            wxvar_json = json.dumps( ld_dict )
        finally:
            wxdb.close_wxdb()
    else: #Debug case if nonsense lat/lon passed
        print(f'DEBUG: {lat_n}, {long_e}')
        with open('Seldovia.json', 'r') as infile:
            wxvar_json = infile.read()
            infile.close()
    return wxvar_json
