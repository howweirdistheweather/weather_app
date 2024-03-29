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

import sys
import datetime
import json
import pathlib


HOURS_PER_WEEK      = 24 * 7
HOURS_PER_YEAR      = 364 * 24
WEEKS_PER_YEAR      = 52
NUM_LONGIDX_GLOBAL  = 1440
NUM_LATIDX_GLOBAL   = 721
HWITW_START_YEAR    = 1950  # hardcoded in the web client

current_time        = datetime.datetime.now()
#global_data_groups  = ['temperature_and_humidity','wind','precipitation','cloud_cover']

def prompt_for_continue():
    the_inp = input('     Continue? (y,n enter): ')
    if the_inp != 'y' and the_inp != 'Y':
        exit( -1 )

##########################################################
# main

def main():
    print( f'JSON data comparison tool. Checks file arg1 against file arg2. ..So there can be things in arg2 that are not present in arg1.')
    if len( sys.argv ) != 3:
        print( 'Takes 2 filenames as arguments!' )
        exit( -1 )

    fn1 = sys.argv[1]
    fn2 = sys.argv[2]

    with open( fn1, 'r') as file1, open( fn2, 'r') as file2:
        js1 = file1.read()
        js2 = file2.read()

    loc_data1 = json.loads( js1 )
    loc_data2 = json.loads( js2 )

    # compare variables
    for var_key, var_val in loc_data1['variables'].items():

        for subv_key, subv_val in var_val.items():
            print( var_key + ' - ' + subv_key )

            for year_i in range( len( subv_val['data'] ) ):

                for week_i in range( len( subv_val['data'][year_i] ) ):
                    val0 = subv_val['data'][year_i][week_i]
                    val1 = loc_data2['variables'][var_key][subv_key]['data'][year_i][week_i]
                    if val0 != val1:
                        print( f'    mismatch! year {year_i} week {week_i}: {val0},{val1}', end='' )
                        print('')
                        #prompt_for_continue()

            print( ' ok' )
    print('done.')

if __name__ == '__main__':
    main()
