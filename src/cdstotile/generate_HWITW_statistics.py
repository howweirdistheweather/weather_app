import math
import numpy

from data_settings import data_settings_internal


# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
HOURS_PER_WEEK = 24 * 7
WEEKS_PER_YEAR = 52
HOURS_PER_YEAR = WEEKS_PER_YEAR * HOURS_PER_WEEK #this is actually 364 days, so we miss one day most years, and two days on leap years
KtoC_DIFFERENCE = 273

# Latitude-correct solar half-day
# Pass latitude
# returns tuple with day_start, day_end, and a boolean day_split that is true if daytime is split into two segments
def lat_correct_solar_half_day(lon):
    day_start = (6  - math.floor(lon/15))%24
    day_end   = (18 - math.floor(lon/15))%24
    return day_start, day_end, day_end < day_start #should this be strict inequality or non-strict?

def RH(T, D): #T = temperature, D = dewpoint
    #Source: https: // bmcnoldy.rsmas.miami.edu / Humidity.html
    #Constants
    A = 17.625
    B = 243.04
    #Proportional relative humidity: e ^ (A D / (B+D)) / e ^ (A T / (B+T))
    return math.exp(A*D / (B+D)) / math.exp(A*T / (B+T))

def do_week_temp_dp(temperatures:numpy.array((HOURS_PER_WEEK), dtype=numpy.float32), dewpoints:numpy.array((HOURS_PER_WEEK), dtype=numpy.float32), day_info):
    #Take in a week worth of temperature and dewpoint data
    #Return all 11 temp and RH stats
    day_start, day_end, day_split = day_info
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
    ave_day_temp = data_settings_internal['variables']['temperature']['day_avg']['compression_function'](ave_day_temp_raw-KtoC_DIFFERENCE)
    ave_night_temp = data_settings_internal['variables']['temperature']['night_avg']['compression_function'](ave_night_temp_raw-KtoC_DIFFERENCE)
    ave_temp = data_settings_internal['variables']['temperature']['avg']['compression_function'](ave_temp_raw-KtoC_DIFFERENCE)
    ave_temp_range = data_settings_internal['variables']['temperature']['range_avg']['compression_function'](numpy.average(temp_ranges))
    temperatures = numpy.sort(temperatures)
    min_temp = data_settings_internal['variables']['temperature']['min']['compression_function'](temperatures[0]-KtoC_DIFFERENCE)
    p10_temp = data_settings_internal['variables']['temperature']['p10']['compression_function'](temperatures[17]-KtoC_DIFFERENCE)
    p90_temp = data_settings_internal['variables']['temperature']['p90']['compression_function'](temperatures[151]-KtoC_DIFFERENCE)
    max_temp = data_settings_internal['variables']['temperature']['max']['compression_function'](temperatures[-1]-KtoC_DIFFERENCE)
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

def do_temp_dp(ds:numpy.array((2,HOURS_PER_YEAR),dtype=numpy.float32), lon):
    #Takes in 1 year of temperature and dewpoint data
    #Returns a tuple of arrays, each array with one compressed statistic per 52 weeks in the year
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
               "min":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "p10":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "avg":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "p90":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "max":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "day_avg":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "night_avg":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "range_avg":numpy.zeros((WEEKS_PER_YEAR),dtype=int)
           },
           "relative_humidity":{
               "p10":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "p50":numpy.zeros((WEEKS_PER_YEAR),dtype=int), 
               "p90":numpy.zeros((WEEKS_PER_YEAR),dtype=int)
           }
    }
    for week in range(WEEKS_PER_YEAR):
        start = week*HOURS_PER_WEEK
        end = (week+1)*HOURS_PER_WEEK
        result = do_week_temp_dp(ds[0][start:end], ds[1][start:end], day_info)
        for variable,variable_info in result.items():
            for stat,value in variable_info.items():
                results[variable][stat][week] = value
    return results
