# create & update final data output for HWITW
#

import numpy
import h5py
from data_settings import data_settings
from data_groups import data_groups, all_variables

WXDB_START_YEAR = 1950
WXDB_END_YEAR   = 2030
WXDB_NUM_YEARS  = WXDB_END_YEAR - WXDB_START_YEAR
WXDB_NUM_WEEKS  = 52
WXDB_NUM_LONGIDX_GLOBAL = 1440
WXDB_NUM_LATIDX_GLOBAL  = 721

WXDB_DATASET = 'wxdb'
WXDB_FILE_ID = 'WXDB0001'
WXDB_FILE_NUMV_SZ = 2
WXDB_FILE_VNAME_SZ = 255

WXDB_VAL_SZ = 1
WXDB_WKBLOCK_MULT = WXDB_VAL_SZ
WXDB_YRBLOCK_MULT = WXDB_NUM_WEEKS * WXDB_WKBLOCK_MULT
WXDB_LONGBLOCK_MULT = WXDB_NUM_YEARS * WXDB_YRBLOCK_MULT
WXDB_LATBLOCK_MULT = WXDB_NUM_LONGIDX_GLOBAL * WXDB_LONGBLOCK_MULT

# what data processing to do for the whole globe (as opposed to specific locations)
wxdb_data_groups = ['temperature_and_humidity','wind','precipitation','cloud_cover']
wxdb_num_vars = 0
wxdb_vartable = []
wxdb_data_offset = 0  # offset in file to start of data
wxdb_wxfile = None
wxdb_ds = None


# determine the full list of variables we want to store
def get_src_vartable() -> list:
    vartable = []
    var_count = 0
    for dg_name in wxdb_data_groups:
        dg = data_groups[ dg_name ]
        for sub_var in dg['sub_vars']:
            for subsub_var in data_settings['variables'][sub_var]:
                var_count = var_count + 1
                vartable.append( f'{sub_var}.{subsub_var}' )
    return vartable


def get_latitude_index( lat_deg_n:float ) -> int:
        lat_idx = math.floor((90.0 - lat_deg_n) * 4)
        return lat_idx


def get_longitude_index( long_deg_e:float ) -> int:
        long_idx = math.floor((long_deg_e + 180.0) * 4)
        return long_idx


# create a new wxdb file, clobbers any existing file!
def create_wxdb( filename:str ):
    wxdb_vartable = get_src_vartable()
    wxdb_num_vars = len(wxdb_vartable)

    print( 'debug: allocating wxdb file' )
    #wxfile = open( filename, 'wb+' )
    wxfile = h5py.File(filename, 'w', libver='latest')
    #mega_size = WXDB_LATBLOCK_MULT * WXDB_NUM_LATIDX_GLOBAL * WXDB_VAL_SZ * wxdb_num_vars
    print( 'debug: wxdb create_dataset' )
    wxshape = (WXDB_NUM_LATIDX_GLOBAL,WXDB_NUM_LONGIDX_GLOBAL,WXDB_NUM_YEARS,WXDB_NUM_WEEKS,wxdb_num_vars)
    wxds = wxfile.create_dataset( WXDB_DATASET, wxshape, dtype='B', fillvalue=255) # B for byte
    print( 'debug: wxdb done create_dataset' )
    wxds.attrs['WXDB_FILE_ID']      = WXDB_FILE_ID
    wxds.attrs['WXDB_START_YEAR']   = WXDB_START_YEAR
    wxds.attrs['WXDB_END_YEAR']     = WXDB_END_YEAR
    wxds.attrs['WXDB_VARS']         = wxdb_vartable

    wxfile.close()
    print( 'debug: wxfile close' )


# open the wxdb file for read & write
# returns: the variable table
def open_wxdb( filename:str ) -> list:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    # open for read write
    wxdb_wxfile = h5py.File(filename, 'r+', libver='latest')
    wxdb_ds = wxdb_wxfile[ WXDB_DATASET ]

    assert wxdb_ds.attrs['WXDB_FILE_ID']    == WXDB_FILE_ID
    assert wxdb_ds.attrs['WXDB_START_YEAR'] == WXDB_START_YEAR
    assert wxdb_ds.attrs['WXDB_END_YEAR']   == WXDB_END_YEAR
    wxdb_vartable = list( wxdb_ds.attrs['WXDB_VARS'] )
    wxdb_num_vars = len(wxdb_vartable)
    assert wxdb_vartable == get_src_vartable()
    print( f'debug: wxdb_num_vars {wxdb_num_vars}' )
    return wxdb_vartable


# open the wxdb file for read only
# returns: the variable table
def open_wxdb_ro( filename:str ) -> list:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    # open for read write
    wxdb_wxfile = h5py.File(filename, 'r', libver='latest')
    wxdb_ds = wxdb_wxfile[ WXDB_DATASET ]

    assert wxdb_ds.attrs['WXDB_FILE_ID']    == WXDB_FILE_ID
    assert wxdb_ds.attrs['WXDB_START_YEAR'] == WXDB_START_YEAR
    assert wxdb_ds.attrs['WXDB_END_YEAR']   == WXDB_END_YEAR
    wxdb_vartable = list( wxdb_ds.attrs['WXDB_VARS'] )
    wxdb_num_vars = len(wxdb_vartable)
    assert wxdb_vartable == get_src_vartable()
    print( f'debug: wxdb_num_vars {wxdb_num_vars}' )
    return wxdb_vartable


def close_wxdb():
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    wxdb_wxfile.close()


# read all data for a single location
# pass latitude degrees north(+), longitude degress east(+)
def read_wxdb( lat_n:float, long_e:float, year:int, loc_data:list ) -> numpy.array:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    lat_idx = get_latitude_index(lat_n)
    long_idx = get_longitude_index(long_e)
    ldata = wxdb_ds[ lat_idx, long_idx ]
    return ldata


# calls flush!
def flush_wxdb():
    global wxdb_wxfile
    wxdb_wxfile.flush()


# write array of longitude values for one variable
def write_wxdb_lat( varname:str, lat_idx:int, year:int, week_idx:int, val_array:numpy.array ):
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    year_idx = year - WXDB_START_YEAR
    vt_idx = wxdb_vartable.index( varname )

    for long_idx in range(WXDB_NUM_LONGIDX_GLOBAL):
        wxdb_ds[ lat_idx, :, year_idx, week_idx, vt_idx ] = val_array[:]


# write 1 years worth of data at one location, however many weeks are present, all vars
# Assumes vars are in correct order.
def write_wxdb( lat_idx:int, long_idx:int, year:int, wk_var_array:numpy.array ):
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    year_idx = year - WXDB_START_YEAR
    num_wk = len(wk_var_array)
    wxdb_ds[ lat_idx, long_idx, year_idx, :num_wk ] = wk_var_array[:]

