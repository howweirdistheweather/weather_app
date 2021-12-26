import math
import numpy

from data_settings import data_settings_internal

# ignoring leap years (i.e. week 53)!
# Calculations will be off by one day after Feb 28.!
DAYS_PER_WEEK = 7
HOURS_PER_WEEK = 168 #24 * DAYS_PER_WEEK
HALF_HOURS_IN_WEEK = 84 #HOURS_PER_WEEK/2
WEEKS_PER_YEAR = 52
HOURS_PER_YEAR = WEEKS_PER_YEAR * HOURS_PER_WEEK  # this is actually 364 days, so we miss one day most years, and two days on leap years
MIN_VALID_HOURS = 24 #Applies only to the edge-week: If there are less than this many hours, stats for the week are null.

flat_functions = data_settings_internal['flat_functions']

#################################################
#    Temperature and RH data processing         #
#################################################

# Longitude-correct solar half-day
# Pass latitude
# returns tuple with day_start, day_end, and a boolean day_split that is true if daytime is split into two segments
def lon_correct_solar_half_day(lon):
    day_start = (6 - math.floor(lon / 15)) % 24
    day_end = (18 - math.floor(lon / 15)) % 24
    return day_start, day_end, day_end < day_start  # should this be strict inequality or non-strict?

def K_to_C(K):
    return K - 273.15

def RH(T, D):  # T = temperature, D = dewpoint
    # Source: https: // bmcnoldy.rsmas.miami.edu / Humidity.html
    # Constants
    A = 17.625
    B = 243.04
    # Proportional relative humidity: e ^ (A D / (B+D)) / e ^ (A T / (B+T))
    return math.exp(A * D / (B + D)) / math.exp(A * T / (B + T))


def do_temp_dp(raw_temp_dp_data: numpy.array((2, HOURS_PER_WEEK), dtype=float), area_lat_long):
    # Take in a week worth of temperature and dewpoint data
    # Return all 11 temp and RH stats
    lon = area_lat_long[1]
    day_start, day_end, day_split = lon_correct_solar_half_day(lon)
    temperatures = raw_temp_dp_data[0]
    dewpoints = raw_temp_dp_data[1]
    temp_range_sum = 0.0
    day_temp_sum = 0.0
    night_temp_sum = 0.0
    hour_of_day = 0
    incomplete_switch = temperatures[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        relative_humidities = []
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            temperature = temperatures[i]
            if temperature > -32767: #This is the costly line - what about instead branching on the value of temperatures[-1]?
                dewpoint = dewpoints[i]
                relative_humidities.append(RH(temperature,dewpoint))
                if day_split:
                    if day_end < hour_of_day <= day_start: night_temp_sum += temperature
                    else: day_temp_sum += temperature
                elif day_start <= hour_of_day < day_end: day_temp_sum += temperature
                else: night_temp_sum += temperature
                if hour_of_day == 0:
                    day_min = temperature
                    day_max = temperature
                else:
                    if day_min > temperature: day_min = temperature
                    elif day_max < temperature: day_max = temperature #I think we can use elif here safely
                    if hour_of_day == 23:
                        temp_range_sum += day_max-day_min
                        hour_of_day = -1
                hour_of_day += 1
            else: null_count += 1 #No protection against sprinkled nulls - this assumes null indicates we've overrun end of the dataset
    else:
        relative_humidities = numpy.zeros(HOURS_PER_WEEK, dtype=float)
        for i in range(HOURS_PER_WEEK):
            temperature = temperatures[i]
            dewpoint = dewpoints[i]
            relative_humidities[i] = RH(temperature, dewpoint)
            if day_split:
                if day_end < hour_of_day <= day_start:
                    night_temp_sum += temperature
                else:
                    day_temp_sum += temperature
            elif day_start <= hour_of_day < day_end:
                day_temp_sum += temperature
            else:
                night_temp_sum += temperature
            if hour_of_day == 0:
                day_min = temperature
                day_max = temperature
            else:
                if day_min > temperature:
                    day_min = temperature
                elif day_max < temperature:
                    day_max = temperature  # I think we can use elif here safely
                if hour_of_day == 23:
                    temp_range_sum += day_max - day_min
                    hour_of_day = -1
            hour_of_day += 1
    if incomplete_switch:
        if MIN_VALID_HOURS < null_count < HOURS_PER_WEEK:
            good_hours = HOURS_PER_WEEK - null_count
            relative_humidities = numpy.sort(relative_humidities)
            p10_RH = flat_functions['relative_humidity_p10'](relative_humidities[int(good_hours*0.1)])
            p50_RH = flat_functions['relative_humidity_p50'](relative_humidities[int(good_hours*0.5)])
            p90_RH = flat_functions['relative_humidity_p90'](relative_humidities[int(good_hours*0.9)])
            ave_day_temp_raw = day_temp_sum / good_hours * 2
            ave_night_temp_raw = night_temp_sum / good_hours * 2
            ave_temp_raw = (ave_day_temp_raw + ave_night_temp_raw) / 2
            ave_day_temp = flat_functions['temperature_day_avg'](K_to_C(ave_day_temp_raw))
            ave_night_temp = flat_functions['temperature_night_avg'](K_to_C(ave_night_temp_raw))
            ave_temp = flat_functions['temperature_avg'](K_to_C(ave_temp_raw))
            ave_temp_range = flat_functions['temperature_range_avg'](temp_range_sum / DAYS_PER_WEEK)
            temperatures = numpy.sort(temperatures)
            min_temp = flat_functions['temperature_min'](K_to_C(temperatures[0]))
            p10_temp = flat_functions['temperature_p10'](K_to_C(temperatures[int(good_hours*0.1)]))
            p90_temp = flat_functions['temperature_p90'](K_to_C(temperatures[int(good_hours*0.9)]))
            max_temp = flat_functions['temperature_max'](K_to_C(temperatures[-1]))
        else:
            min_temp, p10_temp, ave_temp, p90_temp, max_temp, ave_day_temp, ave_night_temp, ave_temp_range = tuple([255]*8)
            p10_RH, p50_RH, p90_RH = tuple([255]*3)
    else:
        relative_humidities = numpy.sort(relative_humidities)
        p10_RH = flat_functions['relative_humidity_p10'](relative_humidities[17])
        p50_RH = flat_functions['relative_humidity_p50'](relative_humidities[84])
        p90_RH = flat_functions['relative_humidity_p90'](relative_humidities[151])
        ave_day_temp_raw = day_temp_sum / HALF_HOURS_IN_WEEK
        ave_night_temp_raw = night_temp_sum / HALF_HOURS_IN_WEEK
        ave_temp_raw = (ave_day_temp_raw + ave_night_temp_raw) / 2
        ave_day_temp = flat_functions['temperature_day_avg'](K_to_C(ave_day_temp_raw))
        ave_night_temp = flat_functions['temperature_night_avg'](K_to_C(ave_night_temp_raw))
        ave_temp = flat_functions['temperature_avg'](K_to_C(ave_temp_raw))
        ave_temp_range = flat_functions['temperature_range_avg'](temp_range_sum / DAYS_PER_WEEK)
        temperatures = numpy.sort(temperatures)
        min_temp = flat_functions['temperature_min'](K_to_C(temperatures[0]))
        p10_temp = flat_functions['temperature_p10'](K_to_C(temperatures[17]))
        p90_temp = flat_functions['temperature_p90'](K_to_C(temperatures[151]))
        max_temp = flat_functions['temperature_max'](K_to_C(temperatures[-1]))
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


#################################################
# Wind data processing
#################################################

def plane_bearing_trig(dX, dY):  # Always positive radians between 0 and 2*pi, using trig directions not compass directions.
    if dX > 0 and dY >= 0:
        return math.atan(dY / dX)
    elif dX < 0:
        return math.atan(dY / dX) + 3.14159265
    elif dX != 0:
        return math.atan(dY / dX) + 6.2831853  # 6.2831853 = math.pi*2
    else:
        return 1.5707963  # 1.5707963 = math.pi/2


def bearing_from_radians_wind_dir(angle):
    # The direction the wind comes FROM, so it's going 180 degrees different than this.
    # angle = angle % (2*math.pi) #Only needed if directions outside [0,2pi] are possible. Shouldn't be the case here - remove for optimization.
    # if angle > math.pi/2: return 450.0 - math.degrees(angle) #direction toward, rather than from
    # else: return 90.0 - math.degrees(angle) #direction toward, rather than from
    if angle < 4.71238898:  # 4.71238898 = 3*math.pi/2
        return 270.0 - math.degrees(angle)
    else:
        return 630.0 - math.degrees(angle)


def wind_speed_and_dir(u, v):  # Report direction in compass degrees
    speed = math.sqrt(u * u + v * v)
    return speed, bearing_from_radians_wind_dir(plane_bearing_trig(u, v))


def do_wind(raw_wind_data: numpy.array((2, HOURS_PER_WEEK), dtype=float), area_lat_long):
    # Takes one week of data and generates specific results
    U = raw_wind_data[0]
    V = raw_wind_data[1]
    speed_sum = 0.0
    dir_precision = data_settings_internal['compression']['direction']['scale']
    dir_bins = int(360/dir_precision)
    dir_histogram = numpy.zeros((dir_bins), dtype=int)
    max_speed_raw = 0.0
    mode_count = 0
    u_sum = 0.0
    v_sum = 0.0
    incomplete_switch = U[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            u = U[i]
            if u > -32767:
                v = V[i]
                speed, direction = wind_speed_and_dir(u, v)
                u_sum += u
                v_sum += v
                speed_sum += speed
                if speed > max_speed_raw: max_speed_raw = speed
                dir_bin = int(direction/dir_precision)
                hist_value = dir_histogram[dir_bin] + 1
                dir_histogram[dir_bin] = hist_value
                if hist_value > mode_count:
                    mode_count = hist_value
                    dir_modal = dir_bin #This is the already-compressed value for modal wind
            else: null_count += 1
    else:
        for i in range(HOURS_PER_WEEK):
            u = U[i]
            v = V[i]
            speed, direction = wind_speed_and_dir(u, v)
            u_sum += u
            v_sum += v
            speed_sum += speed
            if speed > max_speed_raw: max_speed_raw = speed
            dir_bin = int(direction/dir_precision)
            hist_value = dir_histogram[dir_bin] + 1
            dir_histogram[dir_bin] = hist_value
            if hist_value > mode_count:
                mode_count = hist_value
                dir_modal = dir_bin #This is the already-compressed value for modal wind
    if incomplete_switch:
        if MIN_VALID_HOURS < null_count < HOURS_PER_WEEK:
            good_hours = HOURS_PER_WEEK - null_count
            speed_avg_raw = speed_sum / good_hours
            speed_avg = flat_functions['wind_speed_avg'](speed_avg_raw)
            net_speed_raw, net_dir_raw = wind_speed_and_dir(u_sum/good_hours, v_sum/good_hours)
            speed_net = flat_functions['wind_speed_net'](net_speed_raw)
            dir_net = flat_functions['wind_dir_net'](net_dir_raw)
            speed_max = flat_functions['wind_speed_max'](max_speed_raw)
        else:
            speed_avg, dir_modal, speed_net, dir_net, speed_max = tuple([255]*5)
    else:
        speed_avg_raw = speed_sum / HOURS_PER_WEEK
        speed_avg = flat_functions['wind_speed_avg'](speed_avg_raw)
        net_speed_raw, net_dir_raw = wind_speed_and_dir(u_sum/HOURS_PER_WEEK, v_sum/HOURS_PER_WEEK)
        speed_net = flat_functions['wind_speed_net'](net_speed_raw)
        dir_net = flat_functions['wind_dir_net'](net_dir_raw)
        speed_max = flat_functions['wind_speed_max'](max_speed_raw)
    return {
        "wind":{
            "speed_avg":speed_avg,
            "speed_max":speed_max,
            "speed_net":speed_net,
            "dir_net":dir_net,
            "dir_modal":dir_modal
        }
    }

#################################################
# Precipitation data processing
#################################################

def do_precip(raw_precip_data: numpy.array((2, HOURS_PER_WEEK), dtype=float), area_lat_long):
    amounts = raw_precip_data[0]
    types = raw_precip_data[1]
    total_raw = 0.0
    total_rain_raw = 0.0
    total_snow_raw = 0.0
    total_wet_snow_raw = 0.0
    total_freezing_rain_raw = 0.0
    total_ice_pellets_raw = 0.0
    sorted_nonzero_precip = [] #Presumably globally there's relatively few hours with nonzero precip, so sorting a short py list will be faster than a 168 cell numpy array
    incomplete_switch = amounts[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            amount = amounts[i]
            if amount > -32676:
                type = int(types[i] + 0.001)
                if type: #no need to do anything if it's type zero, since that indicates no precip.
                    if amount > 0: #Toss garbage negative numbers.
                        if type == 1: total_rain_raw += amount
                        elif type == 5: total_snow_raw += amount
                        elif type in (6,7): total_wet_snow_raw += amount #More efficient to use a tuple (6,7) than a list [6,7]
                        elif type == 8: total_ice_pellets_raw += amount
                        elif type == 3: total_freezing_rain_raw += amount
                        sorted_nonzero_precip.append(amount)
                        total_raw += amount
            else: null_count += 1
        if MIN_VALID_HOURS < null_count < HOURS_PER_WEEK:
            good_hours = HOURS_PER_WEEK - null_count
            sorted_nonzero_precip = numpy.sort(sorted_nonzero_precip)
            try: max_raw = sorted_nonzero_precip[-1]
            except IndexError: max_raw = 0
            try: p90_raw = sorted_nonzero_precip[-1*int(good_hours * 0.1)]
            except IndexError: p90_raw = 0
            p90 = flat_functions['precipitation_p90'](p90_raw)
            max = flat_functions['precipitation_max'](max_raw)
        else:
            p90, max = 255,255
    else:
        for i in range(HOURS_PER_WEEK):
            type = int(types[i] + 0.001)
            if type: #no need to do anything if it's type zero, since that indicates no precip.
                amount = amounts[i]
                if amount > 0: #Toss garbage negative numbers.
                    if type == 1: total_rain_raw += amount
                    elif type == 5: total_snow_raw += amount
                    elif type in (6,7): total_wet_snow_raw += amount #More efficient to use a tuple (6,7) than a list [6,7]
                    elif type == 8: total_ice_pellets_raw += amount
                    elif type == 3: total_freezing_rain_raw += amount
                    sorted_nonzero_precip.append(amount)
                    total_raw += amount
        sorted_nonzero_precip = numpy.sort(sorted_nonzero_precip)
        try: max_raw = sorted_nonzero_precip[-1]
        except IndexError: max_raw = 0
        try: p90_raw = sorted_nonzero_precip[-17]
        except IndexError: p90_raw = 0
        p90 = flat_functions['precipitation_p90'](p90_raw)
        max = flat_functions['precipitation_max'](max_raw)
    total = flat_functions['precipitation_total'](total_raw)
    total_rain = flat_functions['precipitation_total_rain'](total_rain_raw)
    total_snow = flat_functions['precipitation_total_snow'](total_snow_raw)
    total_wet_snow = flat_functions['precipitation_total_wet_snow'](total_wet_snow_raw)
    total_ice_pellets = flat_functions['precipitation_total_ice_pellets'](total_ice_pellets_raw)
    total_freezing_rain = flat_functions['precipitation_total_freezing_rain'](total_freezing_rain_raw)
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

################################################################
#  Cloud cover data processing
################################################################

def do_cloud_cover(raw_cloud_cover_data, area_lat_long):
    cloud_cover_data = raw_cloud_cover_data[0]
    incomplete_switch = cloud_cover_data[-1] == -32767
    if incomplete_switch:
        non_null_cloud_cover = []
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            cloud_cover = cloud_cover_data[i]
            if cloud_cover > -32767: non_null_cloud_cover.append(cloud_cover)
            else: null_count += 1
        if MIN_VALID_HOURS < null_count < HOURS_PER_WEEK: #The else isn't dealt with until later
            sorted_data = numpy.sort(non_null_cloud_cover)
            good_hours = HOURS_PER_WEEK - null_count
            p25_raw = sorted_data[int(good_hours*0.25)]
            p50_raw = sorted_data[int(good_hours*0.5)]
            p75_raw = sorted_data[int(good_hours*0.75)]
    else:
        sorted_data = numpy.sort(cloud_cover_data)
        p25_raw = sorted_data[42]
        p50_raw = sorted_data[84]
        p75_raw = sorted_data[126]
    if not incomplete_switch or MIN_VALID_HOURS < null_count < HOURS_PER_WEEK:
        i = 0
        try:
            while sorted_data[i] < 0.1: i+=1
        except IndexError: i = 168
        p_sunny_raw = float(i)/HOURS_PER_WEEK
        i = 167
        try:
            while sorted_data[i] > 0.9: i-=1
        except IndexError: i = -1 #Is this right? Seems like it should be 100%, so it would have to be -1.
        p_cloudy_raw = float(167-i)/HOURS_PER_WEEK
        p25 = flat_functions['cloud_cover_p25'](p25_raw)
        p50 = flat_functions['cloud_cover_p50'](p50_raw)
        p75 = flat_functions['cloud_cover_p75'](p75_raw)
        p_sunny = flat_functions['cloud_cover_p_sunny'](p_sunny_raw)
        p_cloudy = flat_functions['cloud_cover_p_cloudy'](p_cloudy_raw)
    else: p25, p50, p75, p_sunny, p_cloudy = tuple([255]*5)
    return {
        "cloud_cover":{
            "p25":p25,
            "p50":p50,
            "p75":p75,
            "p_sunny":p_sunny,
            "p_cloudy":p_cloudy
        }
    }


################################################################
#  Cloud ceiling data processing
################################################################

def do_cloud_ceiling(raw_cloud_ceiling_data, area_lat_long):
    #For now, assume null ceiling means clear - however this is only true until the end of the dataset is reached, at which time it will appear that the weather is always clear.
    cloud_ceiling_data = raw_cloud_ceiling_data[0]
    compressed_cloud_ceiling_data = numpy.full(HOURS_PER_WEEK, 254, dtype=int) #254 is max height, which is both extremely high ceilings and no ceiling at all.
    #Assume we can use the same compression function for all cloud ceiling values as we used for p50
    compression_function = data_settings_internal['variables']['cloud_ceiling']['p50']['compression_function']
    for i in range(HOURS_PER_WEEK):
        cloud_ceiling = cloud_ceiling_data[i]
        if cloud_ceiling > -32676:
            compressed_cloud_ceiling_data[i] = compression_function(cloud_ceiling)
        else: compressed_cloud_ceiling_data[i] = 254 #Null is assigned to maximum
    sorted_data = numpy.sort(compressed_cloud_ceiling_data)
    min = sorted_data[0]
    p25 = sorted_data[42]
    p50 = sorted_data[84]
    p75 = sorted_data[126]
    max = sorted_data[-1]
    return {
        "cloud_ceiling":{
            "min":min,
            "p25":p25,
            "p50":p50,
            "p75":p75,
            "max":max
        }
    }