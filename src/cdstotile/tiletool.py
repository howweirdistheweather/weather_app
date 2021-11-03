# utility to process downloaded netcdf files into processed output data
# HWITW (C) 2021
#
import math
import datetime
import os.path
import json
import numpy
import netCDF4

import hwxpo

# a helper class for printing color text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
HOURS_PER_YEAR = 365 * 24
WEEKS_PER_YEAR = 52

APP_VERSION = "0.50"
current_time = datetime.datetime.now()

#kelvin to fahrenheit
def kelvin_to_F( temp_k:float ):
    temp_f = (temp_k - 273.15) * 9/5 + 32
    return temp_f

#kelvin list to fahrenheit
def kelvin_to_F( temp_ka:list ):
    # use numpy for speed
    # NULL/NoneType will become NaN
    temp_np = numpy.asarray( temp_ka, dtype=float )
    temp_fa = (temp_np - 273.15) * 9/5 + 32
    # convert back to a list with NaN back to None.. we'll be outputting JSON which doesn't like NaN.
    temp_fa2 = numpy.where( numpy.isnan(temp_fa), None, temp_fa )
    return temp_fa2.tolist()

#meter list to feet
def meter_to_ft( dist_ma:list ):
    # use numpy for speed
    # NULL/NoneType will become NaN
    dist_np = numpy.asarray( dist_ma, dtype=float )
    dist_fta = (dist_np * 3.2808399)
    # convert back to a list with NaN back to None.. we'll be outputting JSON which doesn't like NaN.
    dist_fta2 = numpy.where( numpy.isnan(dist_fta), None, dist_fta )
    return dist_fta2.tolist()

# flatten, reshape, rearrange out netcdf dataset variable data into a 2D array
# pass: netcdf dataset, short var name present in the dataset
def reshape_nds( ds:netCDF4.Dataset, short_vn:str ):
    # the netcdf array is a 3 dim array [time][lat][long]
    # lat and long are always index 0 (assuming our cdf files have only one grid cell present)
    # 
    # get the variable of interest, we will call it 'x'
    # ..flatten the array, truncate it to 52 weeks, and reshape it.
    flat_x = ds[short_vn][0:HOURS_PER_YEAR,0,0]
    flat_x = numpy.ma.resize( flat_x, WEEKS_PER_YEAR * HOURS_PER_WEEK )
    array_x = numpy.reshape( flat_x, ( WEEKS_PER_YEAR, HOURS_PER_WEEK ))
    return array_x  # array is now [week][hour]

# calculate weekly average of a variable
# pass: netcdf dataset, short var name present in the dataset
# returns: list
def do_hwxpo_avg( ds:netCDF4.Dataset, short_vn:str ):
    array_x = reshape_nds( ds, short_vn )    
    weekly_results = [0.0] * 52
    for week_num in range( 0, 52 ):
        avg_x = numpy.average( array_x[ week_num ] )
        weekly_results[ week_num ] = avg_x.tolist() # convert to list

    # old code, manual calc. of average. We are now using numpy stuff!
    #
    # array_x = ds[short_vn]    
    # weekly_results = [0.0] * 52
    
    # for week_num in range(0,52):
    #     # calc start and end hour for week_num        
    #     start_hour = week_num * hours_per_week
    #     end_hour = (week_num+1) * hours_per_week 

    #     # calc. average for the week
    #     total_x = 0.0;
    #     for hour_num in range(start_hour, end_hour):
    #         total_x += array_x[hour_num, 0, 0]

    #     avg_x = total_x / hours_per_week
    #     weekly_results[ week_num ] = avg_x
    #     #print( f"{week_num} avg: {avg_x}" )

    return weekly_results

# calculate weekly-NIGHTLY average of a variable
# pass: netcdf dataset, short var name present in the dataset
# returns: list
def do_hwxpo_avg_night( ds:netCDF4.Dataset, short_vn:str ):
    array_x = reshape_nds( ds, short_vn )
    
    # todo: adjust for local time
    # a simplistic definition of 'night'? 18:00 to 06:00
    weekly_results = [0.0] * 52
    for week_num in range( 0, 52 ):
        night_array_x = numpy.empty(0);
        for day_num in range( 0, 7 ):
            hrd = day_num * 24
            hr0 = 0 + hrd       # early morning
            hr1 = 6 + hrd
            hr2 = 18 + hrd      # late night
            hr3 = 24 + hrd
            night_array_x = numpy.append( night_array_x, array_x[week_num][hr0:hr1] )
            night_array_x = numpy.append( night_array_x, array_x[week_num][hr2:hr3] )
            
        avg_x = numpy.average( night_array_x )
        weekly_results[ week_num ] = avg_x

    return weekly_results

# calculate weekly-DAYTIME average of a variable
# pass: netcdf dataset, short var name present in the dataset
# returns: list
def do_hwxpo_avg_day( ds:netCDF4.Dataset, short_vn:str ):
    array_x = reshape_nds( ds, short_vn )
    
    # todo: adjust for local time
    # a simplistic definition of 'day'? 06:00 to 18:00
    weekly_results = [0.0] * 52
    for week_num in range( 0, 52 ):
        day_array_x = numpy.empty(0);
        for day_num in range( 0, 7 ):
            hrd = day_num * 24
            hr0 = 6 + hrd
            hr1 = 18 + hrd
            day_array_x = numpy.append( day_array_x, array_x[week_num][hr0:hr1] )
            
        avg_x = numpy.average( day_array_x )
        weekly_results[ week_num ] = avg_x

    return weekly_results


def load_netcdfs( hpo:hwxpo.HWXPO(), dir_name, start_year, end_year, area_lat_long ):
    # calculate a unique number for each quarter degree on the planet.
    # makes having a unique filename for the coordinates simpler.
    grid_num = CalcQtrDegGridNum( area_lat_long )

    years = list( range( start_year, end_year + 1 ) )
    yearly_results = [None] * len(years)

    for year in years:
        yidx = year - start_year

        for vnames in cds_variables:
            var_name = vnames[0]
            short_var_name = vnames[1]

            # file naming scheme
            pathname = f'./{dir_name}/{year}/'
            filename = f'gn{grid_num}-{year}-{var_name}.nc'
            fullname = pathname + filename

            # make sure file already exists and load it
            already_exists = os.path.isfile( fullname ) #and os.path.getsize( fullname ) > 500
            if not already_exists:
                print( bcolors.WARNING + f'{filename} is missing!' + bcolors.ENDC )
                continue
            
            # NOTE: dataset should have 3 dimensions. time as hour, a single lat, a single long
            print( f'processing {filename}' )
            try:
                ds = netCDF4.Dataset( fullname )
            except OSError:
                print( bcolors.FAIL + f'{filename} could not be opened!' + bcolors.ENDC )
                exit(-1)
  
            # process it
            if short_var_name == CDSVAR_T2M[1]:
                temp_avg = do_hwxpo_avg( ds, short_var_name )
                temp_avg = kelvin_to_F( temp_avg )
                hpo.add_temp_avg( year, temp_avg )                
                
                temp_avg_n = do_hwxpo_avg_night( ds, short_var_name )
                temp_avg_n = kelvin_to_F( temp_avg_n )
                hpo.add_temp_avg_n( year, temp_avg_n )

                temp_avg_d = do_hwxpo_avg_day( ds, short_var_name )
                temp_avg_d = kelvin_to_F( temp_avg_d )
                hpo.add_temp_avg_d( year, temp_avg_d )

            if short_var_name == CDSVAR_CBH[1]:
                ceiling_avg = do_hwxpo_avg( ds, short_var_name )
                ceiling_avg = meter_to_ft( ceiling_avg )
                hpo.add_ceiling_avg( year, ceiling_avg )

            else:
                print( bcolors.WARNING + f'Unhandled variable type! {var_name} {short_var_name}' + bcolors.ENDC )

def CalcQtrDegGridNum( area_lat_long ):
    grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    return grid_num
    
##########################################################
# main

print( f'** HWITW tile tool v{APP_VERSION} **\n')

inp_lat = 59.64 # homer ak
inp_long = -151.54

# todo Zoom level 11 tile number
# get the containing cell 
lat0 = math.ceil( inp_lat * 4 ) / 4
lat1 = (math.floor( inp_lat * 4 ) / 4) #+ 0.01 # edge is not inclusive
long0 = math.floor( inp_long * 4 ) / 4
long1 = (math.ceil( inp_long * 4 ) / 4) #- 0.01

area0 = [ lat0, long0, lat1, long1 ]

# the variables we are interested, long name and short name.
# short name is used inside the netcdf files
CDSVAR_U10 =    ['10m_u_component_of_wind', 'u10' ]
CDSVAR_V10 =    ['10m_v_component_of_wind', 'v10' ]
CDSVAR_D2M =    ['2m_dewpoint_temperature', 'd2m' ]
CDSVAR_T2M =    ['2m_temperature',          't2m' ]
CDSVAR_CBH =    ['cloud_base_height',       'cbh' ]
CDSVAR_PTYPE =  ['precipitation_type',      'ptype' ]
#CDSVAR_SP =     ['surface_pressure',        'sp' ]
CDSVAR_TCC =    ['total_cloud_cover',       'tcc' ]
CDSVAR_TP =     ['total_precipitation',     'tp' ]

cds_variables = [
    CDSVAR_U10,
    CDSVAR_V10,
    CDSVAR_D2M,
    CDSVAR_T2M,
    CDSVAR_CBH,
    CDSVAR_PTYPE,
#    CDSVAR_SP,
    CDSVAR_TCC,
    CDSVAR_TP
]

# load and process netcdf files for this area0
hpo = hwxpo.HWXPO()

# era5 goes from 1979 to present
load_netcdfs(   hpo,
                'cds_era5',
                1979, current_time.year,
                area0 )

# era5 back extension goes from 1950 to 1978
load_netcdfs(   hpo,
                'cds_era5_backext',
                1950, 1978,
                area0 )

# dump json
gnum = CalcQtrDegGridNum( area0 )
outname = f'gn{gnum}-hwxpo.json'
print( f'Output {outname}' )
with open( outname, 'w') as outfile:
    json.dump( hpo.get_jodict(), outfile )

# temporary: dump temp average to a json text file
#gnum = CalcQtrDegGridNum( area0 )
#outname = f'gn{gnum}-temp_avg.json'
#print( f'Output {outname}' )
#with open( outname, 'w') as outfile:
#    json.dump( hpo.TempAvg, outfile )

# dump ceiling avg to json text
#outname = f'gn{gnum}-ceiling_avg.json'
#print( f'Output {outname}' )
#with open( outname, 'w') as outfile:
#    json.dump( hpo.CeilingAvg, outfile )
