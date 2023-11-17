# open and read a wxdb file
#
# !! This is basically copy paste code from cdstotile/wxdb.py because i'm not sure
# how to have python imports from different folders! :) Lets find a way to fix it
# so we dont have to duplicate code!!
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
WXDB_VAL_SZ = 1

# what data processing to do for the whole globe (as opposed to specific locations)
wxdb_data_groups = ['temperature_and_humidity','wind','precipitation','cloud_cover']
wxdb_num_vars = 0
wxdb_vartable = []
wxdb_data_offset = 0  # offset in file to start of data
wxdb_wxfile = None
wxdb_ds = None


def get_latitude_index( lat_deg_n:float ) -> int:
        lat_idx = int( math.floor((90.0 - lat_deg_n) * 4) )
        lat_idx += 1
        return lat_idx


def get_longitude_index( long_deg_e:float ) -> int:
        long_deg_eabs = long_deg_e if long_deg_e >= 0 else 360.0 + long_deg_e
        long_idx = int( math.floor(long_deg_eabs * 4) )
        return long_idx


# Get the 'data_settings' object used in the creation of this wxdb
def read_src_datasettings_json() -> dict:
    return wxdb_ds.attrs['WXDB_SRC_DATAS_JSON']
    #return '{"data_specs": {"start_year": 1950, "Name": "Seldovia"}, "compression": {"temperature": {"min": -60, "scale": 0.5, "type": "linear", "units": "C"}, "temperature_range": {"min": 0, "scale": 0.1, "type": "linear", "units": "C"}, "temperature_range_sensitive": {"min": 0, "scale": 0.03, "type": "linear", "units": "C"}, "wind_speed_HiFi": {"min": 0, "scale": 0.1, "type": "linear", "units": "m/s"}, "wind_speed_LoFi": {"min": 0, "scale": 0.4, "type": "linear", "units": "m/s"}, "direction": {"min": 0, "scale": 1.5, "type": "linear", "units": "degrees"}, "proportion": {"min": 0, "scale": 0.00394, "type": "linear", "units": ""}, "precipitation": {"min": 0, "scale": 0.003, "type": "parabolic", "units": "m"}, "precipitation_sensitive": {"min": 0, "scale": 0.001, "type": "parabolic", "units": "m"}, "precipitation_very_sensitive": {"min": 0, "scale": 0.0005, "type": "parabolic", "units": "m"}, "water_temperature": {"min": -10, "scale": 0.2, "type": "linear", "units": "C"}, "water_flux": {"scale": 0.005, "type": "signed_parabolic", "units": "m"}, "water_flux_sensitive": {"scale": 0.0005, "type": "signed_parabolic", "units": "m"}, "water_flux_very_sensitive": {"scale": 0.0001, "type": "signed_parabolic", "units": "m"}, "cloud_ceiling": {"min": 0, "scale": 30, "type": "linear", "units": "m"}, "wave_height": {"min": 0, "scale": 0.1, "type": "linear", "units": "m"}, "wave_period": {"min": 0, "scale": 0.1, "type": "linear", "units": "s"} } }'


# open the wxdb file for read only
# returns: the variable table
def open_wxdb_ro( filename:str ) -> list:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    # open for read
    wxdb_wxfile = h5py.File(filename, 'r', libver='latest')
    wxdb_ds = wxdb_wxfile[ WXDB_DATASET ]
    #print( f'shape {wxdb_ds.shape}' )
    #print( f'chunks {wxdb_ds.chunks}' )
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
# pass latitude degrees north(+), longitude degrees east(+)
def read_wxdb( lat_n:float, long_e:float ) -> numpy.array:
    global wxdb_wxfile, wxdb_ds, wxdb_num_vars, wxdb_vartable
    lat_idx = get_latitude_index(lat_n)
    long_idx = get_longitude_index(long_e)
    print( f'debug: lat_idx {lat_idx}, long_idx {long_idx}' )
    ldata = wxdb_ds[ lat_idx, long_idx ]
    # debug:
    #ldata = numpy.copy( ldata )
    # for a in range(WXDB_NUM_YEARS):
    #     for b in range(WXDB_NUM_WEEKS):
    #         for c in range(wxdb_num_vars):
    #             ldata[a,b,c] = (a+b+c)
    #print( ldata )
    return ldata
