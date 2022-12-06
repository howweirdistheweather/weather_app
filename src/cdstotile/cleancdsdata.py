# get rid of the expver stuff or otherwise clean up downloaded cds data..
# newest ERA5 data has an experiment version dimension with 2 coordinates.
# the data is spread across the 2 columns. we merge them
import os
import xarray


def remove_expver( filename:str ):
    #print( 'debug: remove_expver' )
    temp_filename = filename + '.rexpver'
    #ERA5 = xarray.open_mfdataset( filename, combine='by_coords', chunks={'time': 52} )
    ERA5 = xarray.open_dataset( filename, chunks={'time': 52} )

    if 'expver' not in ERA5.dims.keys():
        return

    # our files should have just 1 variable. get its name.
    the_var = list(ERA5.data_vars.keys())[0]
    ERA5_combine = ERA5.sel(expver=1).combine_first(ERA5.sel(expver=5))
    #ERA5_combine.load()
    #e5int = ERA5_combine.astype( 'int16' )
    ERA5_combine.to_netcdf(temp_filename, format='NETCDF3_64BIT',
                           encoding={the_var:{'dtype':'int16','_FillValue': -32767, 'missing_value':-32767} } )
    ERA5.close()
    ERA5_combine.close()
    print( f'debug: merged expver {the_var} ' + filename )
    os.rename( temp_filename, filename )
    pass
