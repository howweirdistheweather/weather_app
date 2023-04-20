# get weather data for the webapp
#
import json
import numpy
import wxdb_reader as wxdb
from collections import defaultdict

WXDB_FILE = './hwitw.wxdb'


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
    wxvt = wxdb.open_wxdb( WXDB_FILE )
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
        wxvt = wxdb.open_wxdb_ro( WXDB_FILE )
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
