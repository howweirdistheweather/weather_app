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

import math
import numpy

from data_settings import data_settings_internal


# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
WEEKS_PER_YEAR = 52
HOURS_PER_YEAR = WEEKS_PER_YEAR * HOURS_PER_WEEK #this is actually 364 days, so we miss one day most years, and two days on leap years


# PASS: data_arrays is list of variables's arrays containing 1 week of data
def process_data( data_arrays, func, results, data_consts=[] ):
    try:
        result = func( data_arrays, data_consts )
        for variable, variable_info in result.items():
            for stat, value in variable_info.items():
                results[ variable ][ stat ] = value
                
    except( IndexError, ValueError ): #Assume this is because the array isn't long enough - ie it's the current year and ends short
        print( f'Filling with null value: {results.keys()}' )
        for variable, variable_info in results.items(): #Note results as opposed to result
            for stat in variable_info:
                results[ variable ][ stat ] = 255 #Null value

#################################################
#    Temperature and RH data processing
#################################################

# Latitude-correct solar half-day
# Pass latitude
# returns tuple with day_start, day_end, and a boolean day_split that is true if daytime is split into two segments
def lat_correct_solar_half_day(lon):
    day_start = (6  - math.floor(lon/15))%24
    day_end   = (18 - math.floor(lon/15))%24
    return day_start, day_end, day_end < day_start #should this be strict inequality or non-strict?

def K_to_C(K):
    return K - 273.15

def RH(T, D): #T = temperature, D = dewpoint
    #Source: https: // bmcnoldy.rsmas.miami.edu / Humidity.html
    #Constants
    A = 17.625
    B = 243.04
    #Proportional relative humidity: e ^ (A D / (B+D)) / e ^ (A T / (B+T))
    return math.exp(A*D / (B+D)) / math.exp(A*T / (B+T))

def do_week_temp_dp( data_arrays, data_consts ):
    #Take in a week worth of temperature and dewpoint data
    #Return all 11 temp and RH stats
    temperatures = data_arrays[0]
    dewpoints = data_arrays[1]
    day_start, day_end, day_split = data_consts[0]
    day_temps = numpy.zeros((int(HOURS_PER_WEEK/2)), dtype = numpy.float32)
    night_temps = numpy.zeros((int(HOURS_PER_WEEK/2)), dtype = numpy.float32)
    relative_humidities = numpy.zeros((HOURS_PER_WEEK), dtype = numpy.float32)
    temp_ranges = numpy.zeros((7), dtype = numpy.float32)
    day_index = 0
    day_temp_index = 0
    night_temp_index = 0
    for i in range(HOURS_PER_WEEK):
        temperature = temperatures[i]
        dewpoint = dewpoints[i]
        relative_humidities[i] = RH(temperature,dewpoint)
        hour_of_day = i%24
        if day_split:
            if day_end < hour_of_day <= day_start:
                night_temps[night_temp_index] = temperature
                night_temp_index += 1
            else:
                day_temps[day_temp_index] = temperature
                day_temp_index += 1
        elif day_start <= hour_of_day < day_end:
            day_temps[day_temp_index] = temperature
            day_temp_index += 1
        else:
            night_temps[night_temp_index] = temperature
            night_temp_index += 1
        if hour_of_day == 0:
            day_min = temperature
            day_max = -temperature
        else:
            if day_min > temperature: day_min = temperature
            elif day_max < temperature: day_max = temperature #I think we can use elif here safely
            if hour_of_day == 23:
                temp_ranges[day_index] = day_max-day_min
                day_index += 1
    relative_humidities = numpy.sort(relative_humidities)
    p10_RH = data_settings_internal['variables']['relative_humidity']['p10']['compression_function'](relative_humidities[17])
    p50_RH = data_settings_internal['variables']['relative_humidity']['p50']['compression_function'](relative_humidities[84])
    p90_RH = data_settings_internal['variables']['relative_humidity']['p90']['compression_function'](relative_humidities[151])
    ave_day_temp_raw = numpy.average(day_temps)
    ave_night_temp_raw = numpy.average(night_temps)
    ave_temp_raw = (ave_day_temp_raw+ave_night_temp_raw)/2
    ave_day_temp = data_settings_internal['variables']['temperature']['day_avg']['compression_function'](K_to_C(ave_day_temp_raw))
    ave_night_temp = data_settings_internal['variables']['temperature']['night_avg']['compression_function'](K_to_C(ave_night_temp_raw))
    ave_temp = data_settings_internal['variables']['temperature']['avg']['compression_function'](K_to_C(ave_temp_raw))
    ave_temp_range = data_settings_internal['variables']['temperature']['range_avg']['compression_function'](numpy.average(temp_ranges))
    temperatures = numpy.sort(temperatures)
    min_temp = data_settings_internal['variables']['temperature']['min']['compression_function'](K_to_C(temperatures[0]))
    p10_temp = data_settings_internal['variables']['temperature']['p10']['compression_function'](K_to_C(temperatures[17]))
    p90_temp = data_settings_internal['variables']['temperature']['p90']['compression_function'](K_to_C(temperatures[151]))
    max_temp = data_settings_internal['variables']['temperature']['max']['compression_function'](K_to_C(temperatures[-1]))
    return {
               "temperature":{
                   "min":min_temp, 
                   "p10":p10_temp, 
                   "avg":ave_temp,
                   "p90":p90_temp, 
                   "max":max_temp, 
                   "day_avg":ave_day_temp, 
                   "night_avg":ave_night_temp, 
                   "range_avg":ave_temp_range
               },
               "relative_humidity":{
                   "p10":p10_RH, 
                   "p50":p50_RH, 
                   "p90":p90_RH
               }
    }

def do_temp_dp( raw_temp_dp_data:numpy.array((2,HOURS_PER_WEEK),dtype=numpy.float32), lon):
    #Takes in 1 year of temperature and dewpoint data
    #Returns one compressed statistic per 52 weeks in the year
    #Statistics to return:
        #Minimum temperature
        #10th percentile temperature
        #Average temperature
        #90th percentile temperature
        #Maximum temperature
        #Average daytime temperature
        #Average nighttime temperature
        #Average temperature range
        #10th percentile relative humidity
        #Median relative humidity
        #90th percentile relative humidity
    #Ultimately nice to get deviation from seasonal average temperature, but not yet
    day_info = lat_correct_solar_half_day(lon)
    results = {
           "temperature":{
               "min":0,
               "p10":0,
               "avg":0,
               "p90":0,
               "max":0,
               "day_avg":0,
               "night_avg":0,
               "range_avg":0
           },
           "relative_humidity":{
               "p10":0,
               "p50":0,
               "p90":0
           }
    }
    process_data( data_arrays=raw_temp_dp_data, func=do_week_temp_dp, results=results, data_consts=[day_info])
    return results

#################################################
# Wind data processing
#################################################

def plane_bearing_trig(dX,dY): #Always positive radians between 0 and 2*pi, using trig directions not compass directions.
    if dX > 0 and dY >= 0: return math.atan(dY/dX)
    elif dX < 0: return math.atan(dY/dX) + 3.14159265
    elif dX != 0: return math.atan(dY/dX) + 6.2831853 #6.2831853 = math.pi*2
    else: return 1.5707963 #1.5707963 = math.pi/2

def bearing_from_radians_wind_dir(angle):#The direction the wind comes FROM, so it's going 180 degrees different than this.
    #angle = angle % (2*math.pi) #Only needed if directions outside [0,2pi] are possible. Shouldn't be the case here - remove for optimization.
    #if angle > math.pi/2: return 450.0 - math.degrees(angle) #direction toward, rather than from
    #else: return 90.0 - math.degrees(angle) #direction toward, rather than from
    if angle < 4.71238898: return 270.0 - math.degrees(angle) #4.71238898 = 3*math.pi/2
    else: return 630.0 - math.degrees(angle)

def wind_speed_and_dir(u, v): #Report direction in compass degrees
    speed = math.sqrt(u*u + v*v)
    return speed, bearing_from_radians_wind_dir(plane_bearing_trig(u,v))

def do_week_wind( data, discard):
    #Takes one week of data and generates specific results
    U = data[0]
    V = data[1]
    speed_array = numpy.zeros((HOURS_PER_WEEK), dtype=float)
    dir_precision = data_settings_internal['compression']['direction']['scale']
    dir_bins = int(360/dir_precision)
    dir_histogram = numpy.zeros((dir_bins), dtype=int)
    max_speed_raw = 0.0
    for i in range(HOURS_PER_WEEK):
        speed, direction = wind_speed_and_dir(U[i], V[i])
        speed_array[i]= speed
        if speed > max_speed_raw: max_speed_raw = speed
        direction_2_deg_increments = int(direction/dir_precision)
        dir_histogram[direction_2_deg_increments] += 1
    speed_avg_raw = numpy.average(speed_array)
    speed_avg = data_settings_internal['variables']['wind']['speed_avg']['compression_function'](speed_avg_raw)
    dir_modal, count = 0,0
    #Option 1:
    for i in range(dir_bins):
        if dir_histogram[i] > count:
            count = dir_histogram[i]
            dir_modal = i #Already effectively compressed
    #Option 2: #Too vulnerable to random mistakes. Could add more complexity...
#    for i in range(0,dir_bins,3):
#        if dir_histogram[i] > count:
#            count = dir_histogram[i]
#            dir_modal = i #Already effectively compressed
#    check_list = [i,(i+1)%dir_bins,(i+2)%dir_bins,(i-1)%dir_bins,(i-2)%dir_bins]
#    for i in check_list:
#        if dir_histogram[i] > count:
#            count = dir_histogram[i]
#            dir_modal = i #Already effectively compressed
    net_speed_raw, net_dir_raw = wind_speed_and_dir(numpy.average(U), numpy.average(V))
    speed_net = data_settings_internal['variables']['wind']['speed_net']['compression_function'](net_speed_raw)
    dir_net = data_settings_internal['variables']['wind']['dir_net']['compression_function'](net_dir_raw)
    speed_max = data_settings_internal['variables']['wind']['speed_max']['compression_function'](max_speed_raw)
    return {
        "wind":{
            "speed_avg":speed_avg,
            "speed_max":speed_max,
            "speed_net":speed_net,
            "dir_net":dir_net,
            "dir_modal":dir_modal
        }
    }


def do_wind( raw_wind_data:numpy.array((2,HOURS_PER_WEEK),dtype=numpy.float32)):
    #Returns the following stats:
        #modal wind direction
        #net transport direction
        #net transport distance or speed
        #average wind speed
        #maximum wind speed
    results = {
        "wind":{
            "speed_avg":0,
            "dir_modal":0,
            "speed_net":0,
            "dir_net":0,
            "speed_max":0
        }
    }
    process_data( data_arrays=raw_wind_data, func=do_week_wind, results=results)
    return results

#################################################
# Precipitation data processing
#################################################

def do_week_precip( data, discard ):
    amounts = data[0]
    types = data[1]
    total_raw = 0.0
    total_rain_raw = 0.0
    total_snow_raw = 0.0
    total_wet_snow_raw = 0.0
    total_freezing_rain_raw = 0.0
    total_ice_pellets_raw = 0.0
    sorted_nonzero_precip = [] #Presumably globally there's relatively few hours with nonzero precip, so sorting a short py list will be faster than a 168 cell numpy array
    for i in range(HOURS_PER_WEEK):
        type = int(types[i] + 0.001)
        if type: #no need to do anything if it's type zero, since that indicates no precip.
            amount = amounts[i]
            if amount > 0: #Toss garbage negative numbers.
                if type == 1: total_rain_raw += amount
                elif type == 5: total_snow_raw += amount
                elif type in [6,7]: total_wet_snow_raw += amount
                elif type == 8: total_ice_pellets_raw += amount
                elif type == 3: total_freezing_rain_raw += amount
                sorted_nonzero_precip.append(amount)
                total_raw += amount
    sorted_nonzero_precip = numpy.sort(sorted_nonzero_precip)
    try: max_raw = sorted_nonzero_precip[-1]
    except IndexError: max_raw = 0
    try: p90_raw = sorted_nonzero_precip[-17]
    except IndexError: p90_raw = 0
    total = data_settings_internal['variables']['precipitation']['total']['compression_function'](total_raw)
    total_rain = data_settings_internal['variables']['precipitation']['total_rain']['compression_function'](total_rain_raw)
    total_snow = data_settings_internal['variables']['precipitation']['total_snow']['compression_function'](total_snow_raw)
    total_wet_snow = data_settings_internal['variables']['precipitation']['total_wet_snow']['compression_function'](total_wet_snow_raw)
    total_ice_pellets = data_settings_internal['variables']['precipitation']['total_ice_pellets']['compression_function'](total_ice_pellets_raw)
    total_freezing_rain = data_settings_internal['variables']['precipitation']['total_freezing_rain']['compression_function'](total_freezing_rain_raw)
    p90 = data_settings_internal['variables']['precipitation']['p90']['compression_function'](p90_raw)
    max = data_settings_internal['variables']['precipitation']['max']['compression_function'](max_raw)
    return {
        "precipitation":{
            "total":total,
            "total_rain":total_rain,
            "total_snow":total_snow,
            "total_wet_snow":total_wet_snow,
            "total_ice_pellets":total_ice_pellets,
            "total_freezing_rain":total_freezing_rain,
            "p90":p90,
            "max":max
        }
    }

def do_precip( raw_precip_data:numpy.array((2,HOURS_PER_WEEK),dtype=numpy.float32) ):
    #Takes precip amount and type data as 1-year 1D arrays
    #Returns the following compressed values:
        #Total precip
        #Total rain
        #Total snow
        #Total wet snow
        #Total ice pellets
        #Total freezing rain
        #90th percentile precip
        #Maximum precip
        #I wonder about maximum for some of the other variables too?
    results = {
        "precipitation":{
            "total":0,
            "p90":0,
            "max":0,
            "total_rain":0,
            "total_snow":0,
            "total_wet_snow":0,
            "total_freezing_rain":0,
            "total_ice_pellets":0,
        }
    }
    process_data( data_arrays=raw_precip_data, func=do_week_precip, results=results )
    return results

################################################################
#  Cloud cover data processing
################################################################

def do_week_cloud_cover( data, discard ):
    raw_cloud_cover_data = data[0]
    sorted_data = numpy.sort(raw_cloud_cover_data)
    p25_raw = sorted_data[42]
    p50_raw = sorted_data[84]
    p75_raw = sorted_data[126]
    i = 0
    try:
        while sorted_data[i] < 0.1: i+=1
    except IndexError: i = 168
    p_sunny_raw = float(i)/168
    i = 167
    try:
        while sorted_data[i] > 0.9: i-=1
    except IndexError: i = -1 #Is this right? Seems like it should be 100%, so it would have to be -1.
    p_cloudy_raw = float(167-i)/168
    p25 = data_settings_internal['variables']['cloud_cover']['p25']['compression_function'](p25_raw)
    p50 = data_settings_internal['variables']['cloud_cover']['p50']['compression_function'](p50_raw)
    p75 = data_settings_internal['variables']['cloud_cover']['p75']['compression_function'](p75_raw)
    p_sunny = data_settings_internal['variables']['cloud_cover']['p_sunny']['compression_function'](p_sunny_raw)
    p_cloudy = data_settings_internal['variables']['cloud_cover']['p_cloudy']['compression_function'](p_cloudy_raw)
    return {
        "cloud_cover":{
            "p25":p25,
            "p50":p50,
            "p75":p75,
            "p_sunny":p_sunny,
            "p_cloudy":p_cloudy
        }
    }

def do_cloud_cover( raw_cloud_cover_data ):
    #Takes the cloud cover data and produces:
        #25th percentile cloud cover
        #median cloud cover
        #75th percentile cloud cover
        #Proportion of time clear-ish (<10% cloud cover)
        #Proportion of time cloudy (>90% cloud cover)
    results = {
        "cloud_cover":{
            "p25":0,
            "p50":0,
            "p75":0,
            "p_sunny":0,
            "p_cloudy":0
        }
    }
    process_data( data_arrays=raw_cloud_cover_data, func=do_week_cloud_cover, results=results )
    return results
