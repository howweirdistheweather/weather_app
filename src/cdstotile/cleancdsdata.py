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
