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
    #wxdb_header_size = len(WXDB_FILE_ID) + WXDB_FILE_NUMV_SZ + wxdb_num_vars * WXDB_FILE_VNAME_SZ

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

    # # use this seek and write trick to allocate the file on disk zero-filled
    # wxfile.seek(mega_size-1)
    # wxfile.write(bytearray(1))
    # #os.sync()
    #
    # print( 'debug: done alloc wxdb' )
    #
    # # write the header table
    # wxfile.seek(0)
    # # file id & version 8 bytes
    # wxfile.write( WXDB_FILE_ID.encode('ascii') )
    # # num vars
    # wxfile.write( wxdb_num_vars.to_bytes(WXDB_FILE_NUMV_SZ,'little') )
    # # var names as 255 char strings
    # for wxdb_var in wxdb_vartable:
    #     write_str_wxdb( wxfile, wxdb_var, WXDB_FILE_VNAME_SZ )
    #
    # wxdb_data_offset = wxfile.tell()
    # assert wxdb_data_offset == wxdb_header_size
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

# def seek_valvar_wxdb( varname:str, lat_idx:int, long_idx:int, year:int, week_idx:int ):
#     assert lat_idx >= 0 and lat_idx < WXDB_NUM_LATIDX_GLOBAL
#     assert long_idx >= 0 and long_idx < WXDB_NUM_LONGIDX_GLOBAL
#     assert year >= WXDB_START_YEAR and year <= WXDB_END_YEAR
#     assert week_idx >= 0 and week_idx < WXDB_NUM_WEEKS
#
#     year_idx = year - WXDB_START_YEAR
#     vartable_idx = wxdb_vartable.index( varname )
#
#     woffset = ( wxdb_data_offset + wxdb_num_vars *
#                 (lat_idx * WXDB_LATBLOCK_MULT +
#                 long_idx * WXDB_LONGBLOCK_MULT +
#                 year_idx * WXDB_YRBLOCK_MULT +
#                 week_idx * WXDB_WKBLOCK_MULT +
#                 vartable_idx * WXDB_VAL_SZ) )
#
#     wxdb_wxfile.seek( woffset )
#
#
# def seek_val0_wxdb( lat_idx:int, long_idx:int, year:int, week_idx:int ):
#     assert lat_idx >= 0 and lat_idx < WXDB_NUM_LATIDX_GLOBAL
#     assert long_idx >= 0 and long_idx < WXDB_NUM_LONGIDX_GLOBAL
#     assert year >= WXDB_START_YEAR and year <= WXDB_END_YEAR
#     assert week_idx >= 0 and week_idx < WXDB_NUM_WEEKS
#
#     year_idx = year - WXDB_START_YEAR
#     vartable_idx = 0
#
#     woffset = ( wxdb_data_offset + wxdb_num_vars *
#                 (lat_idx * WXDB_LATBLOCK_MULT +
#                 long_idx * WXDB_LONGBLOCK_MULT +
#                 year_idx * WXDB_YRBLOCK_MULT +
#                 week_idx * WXDB_WKBLOCK_MULT +
#                 vartable_idx * WXDB_VAL_SZ) )
#
#     wxdb_wxfile.seek( woffset )


# def write_str_wxdb( wxf, astr:str, max_len:int ):
#     # pad with spaces to max_len, write fixed size... no null terminator
#     assert len(astr) <= max_len
#     wxf.write( astr.ljust(max_len,' ')[:max_len].encode('ascii') )
#
#
# def read_str_wxdb( wxf, max_len:int ) -> str:
#     astr = wxf.read(max_len).decode('ascii')
#     astr = astr.strip()
#     return astr
#
#
# def write_val_wxdb( val:numpy.uint8 ):
#     #wxdb_wxfile.write( val.to_bytes(WXDB_VAL_SZ,'little') )
#     wxdb_wxfile.write( val )
#
#
# def write_wxdb_byte( varname:str, lat_idx:int, long_idx:int, year:int, week_idx:int, val:numpy.uint8 ):
#     seek_valvar_wxdb( varname, lat_idx, long_idx, year, week_idx )
#     write_val_wxdb( val )


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
    # flush to disk periodically
    #wxdb_wxfile.flush()
    #print( wxdb_ds[ lat_idx, long_idx, year_idx, :num_wk ] )
    #exit(-1)

    # week_idx = 0
    # for week_dat in loc_data:
    #     #var_skip = wxdb_num_vars - len(week_dat)
    #     assert len(week_dat) == wxdb_num_vars
    #     wxdb_ds[ lat_idx, long_idx, year_idx, week_idx, : ] = week_dat[:]
    #     week_idx=week_idx+1
    #     print( f'debug: week_idx {week_idx}' )
    #     print( wxdb_ds[ lat_idx, long_idx, year_idx, week_idx ] )
    #     exit(-1)
    # # flush to disk periodically
    # wxdb_wxfile.flush()

