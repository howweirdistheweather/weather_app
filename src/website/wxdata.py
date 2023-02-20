# get weather data for the webapp
#
import json
import wxdb_reader as wxdb

WXDB_FILE = './hwitw.wxdb'


def wxdata_to_dict() -> dict:
    # get the 'global site' data processing settings and setup output dictionary/structure
    global_site = site_settings['Global']
    out_data = copy.deepcopy(data_settings)
    site_name = f'location {loc_lat}, {loc_long}'
    out_data['data_specs'].update( [('Name',site_name)] )

    # process the years of interest
    years = list( range( start_year, end_year + 1 ) )
    for year in years:
        yidx = year - start_year
        print( f'{year} ', end='' )
        for dg_name in global_site['available_groups']:
            print( f'{dg_name} ', end='',flush=True )
            dg = data_groups[ dg_name ]
            read_data_group( flag_args, loc_lat, loc_long, inp_path, year, dg_name, dg, out_data );
        print( '' )


def get_wxvar_list():
    wxvt = wxdb.open_wxdb( WXDB_FILE )
    wxdb.close_wxdb()
    return wxvt


def get_wxvar( lat_n:float, long_e:float ):
    wxvt = wxdb.open_wxdb_ro( WXDB_FILE )

    #debug: force values for lat&long
    lat_n = 59.45
    long_e = -151.72

    loc_data = wxdb.read_wxdb( lat_n, long_e )
    print( 'debug: ' )
    print( loc_data )
    ld_dict = wxdata_to_dict( loc_data )
    print( 'debug: ' )
    print( ld_dict )
    wxvar_json = json.dumps( ld_dict )
    print( 'debug: ' )
    print( wxvar_json )
    wxdb.close_wxdb()
    return wxvar_json
