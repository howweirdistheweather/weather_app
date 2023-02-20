# open and read a wxdb file
# !! This is basically copy paste code from cdstotile/wxdb.py because i'm not sure
# how to have python imports from different folders! :) Lets find a way to fix it
# so we dont have to duplicate code.
#

import math
import numpy
import h5py

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


def get_latitude_index( lat_deg_n:float ) -> int:
        lat_idx = math.floor((90.0 - lat_deg_n) * 4)
        return lat_idx


def get_longitude_index( long_deg_e:float ) -> int:
        long_idx = math.floor((long_deg_e + 180.0) * 4)
        return long_idx


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
    #assert wxdb_vartable == get_src_vartable()
    print( f'debug: wxdb_num_vars {wxdb_num_vars}' )
    return wxdb_vartable


def close_wxdb():
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    wxdb_wxfile.close()


# read all data for a single location
# pass latitude degrees north(+), longitude degress east(+)
def read_wxdb( lat_n:float, long_e:float ) -> numpy.array:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    lat_idx = get_latitude_index(lat_n)
    long_idx = get_longitude_index(long_e)
    ldata = wxdb_ds[ lat_idx, long_idx ]
    return ldata
