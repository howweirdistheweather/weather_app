import numpy
from generate_HWITW_stats import (
    DAYS_PER_WEEK,
    HOURS_PER_WEEK,
    HALF_HOURS_IN_WEEK,
    WEEKS_PER_YEAR,
    HOURS_PER_YEAR,
    MIN_VALID_HOURS,
    K_to_C
)

from extra_data_settings import data_settings_internal
flat_functions = data_settings_internal['flat_functions']

####################################
#                Runoff            #
####################################

def do_runoff(raw_runoff_data: numpy.array((1, HOURS_PER_WEEK), dtype=float), area_lat_long):
    #Obvious stats are total runoff, max runoff, and P90 runoff
    runoffs = raw_runoff_data[0]
    incomplete_switch = runoffs[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        total_raw = 0.0
        null_count = 0
        valid_runoffs = []
        for i in range(HOURS_PER_WEEK):
            runoff = runoffs[i]
            if runoff > -32767:
                total_raw += runoff
                valid_runoffs.append(runoff)
            else: null_count += 1
        good_hours = HOURS_PER_WEEK-null_count
        if good_hours > MIN_VALID_HOURS:
            sorted_valid_runoffs = numpy.sort(valid_runoffs)
            max_runoff_raw = sorted_valid_runoffs[-1]
            p90_runoff_raw = sorted_valid_runoffs[int((good_hours)*0.9)]
            good_hour_scaler = good_hours/HOURS_PER_WEEK
            total_raw /= good_hour_scaler
        else:
            return {
                "runoff":{
                    "total":255,
                    "p90":255,
                    "max":255
                }
            }
    else:
        total_raw    =   numpy.sum(runoffs)
        sorted_runoffs = numpy.sort(runoffs)
        max_runoff_raw = sorted_runoffs[-1]
        p90_runoff_raw = sorted_runoffs[-17]
    total = flat_functions['runoff_total'](total_raw)
    max = flat_functions['runoff_max'](max_runoff_raw)
    p90 = flat_functions['runoff_p90'](p90_runoff_raw)
    return {
        "runoff":{
            "total":total,
            "p90":p90,
            "max":max
        }
    }

####################################################
#           Drought / evaporation                  #
####################################################

def do_drought(raw_drought_data: numpy.array((3, HOURS_PER_WEEK), dtype=float), area_lat_long):
    #Perhaps total, p90, max again
    #However, PET is generally negative (except for condensation - dew I guess?) so the extremes are the lowest
    PETs = raw_drought_data[0]
    ETs = raw_drought_data[1]
    precip_amounts = raw_drought_data[2]
    incomplete_switch = PETs[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        total_PET_raw = 0.0
        total_ET_raw = 0.0
        total_P_PET_raw = 0.0
        null_count = 0
        valid_PETs = []
        for i in range(HOURS_PER_WEEK):
            PET = PETs[i]
            if PET > -32767:
                total_PET_raw += PET
                total_ET_raw += ETs[i]
                total_P_PET_raw += precip_amounts[i] + PET #PET is typically negative
                valid_PETs.append(PET)
            else: null_count += 1
        good_hours = HOURS_PER_WEEK-null_count
        if good_hours > MIN_VALID_HOURS:
            sorted_valid_PETs = numpy.sort(valid_PETs)
            max_PET_raw = sorted_valid_PETs[0]
            p90_PET_raw = sorted_valid_PETs[int(good_hours*0.1)]
            good_hours_scaler = good_hours/HOURS_PER_WEEK
            total_PET_raw /= good_hours_scaler
            total_ET_raw /= good_hours_scaler
            total_P_PET_raw /= good_hours_scaler
        else:
            return {
                "drought":{
                    "potential_evaporation":255,
                    "evaporation":255,
                    "p90":255,
                    "max":255,
                    "P-PET":255
                }
            }
    else:
        total_PET_raw = numpy.sum(PETs)
        total_ET_raw = numpy.sum(ETs)
        total_P_PET_raw = numpy.sum(precip_amounts) - total_PET_raw
        sorted_PETs = numpy.sort(PETs)
        max_PET_raw = sorted_PETs[0]
        p90_PET_raw = sorted_PETs[17]
    total_PET = flat_functions['drought_potential_evaporation'](total_PET_raw)
    total_ET = flat_functions['drought_evaporation'](total_ET_raw)
    total_P_PET = flat_functions['drought_P-PET'](total_P_PET_raw)
    max = flat_functions['drought_max'](max_PET_raw)
    p90 = flat_functions['drought_p90'](p90_PET_raw)
    return {
        "drought":{
            "potential_evaporation":total_PET,
            "evaporation":total_ET,
            "p90":p90,
            "max":max,
            "P-PET":total_P_PET
        }
    }

###############################################
#               Ocean Temperature             #
###############################################

def do_ocean_temp(raw_ocean_temp_data: numpy.array((1, HOURS_PER_WEEK), dtype=float), area_lat_long):
    #Average, max, min, range
    temps = raw_ocean_temp_data[0]
    incomplete_switch = temps[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            temp = temps[i]
            if temp > -32767:
                if i == 0:
                    min_temp_raw = max_temp_raw = total_raw = temp
                else:
                    total_raw += temp
                    if temp < min_temp_raw: min_temp_raw = temp
                    elif temp > max_temp_raw: max_temp_raw = temp
            else: null_count += 1
        if null_count < HOURS_PER_WEEK - MIN_VALID_HOURS:
            average_raw = total_raw / (HOURS_PER_WEEK-null_count)
            range_raw = max_temp_raw-min_temp_raw
        else:
            return {
                'ocean_temp':{
                    'avg':255,
                    'max':255,
                    'min':255,
                    'range':255
                }
            }
    else:
        for i in range(HOURS_PER_WEEK):
            temp = temps[i]
            if i == 0:
                min_temp_raw = max_temp_raw = total_raw = temp
            else:
                total_raw += temp
                if temp < min_temp_raw: min_temp_raw = temp
                elif temp > max_temp_raw: max_temp_raw = temp
        average_raw = total_raw / HOURS_PER_WEEK
        range_raw = max_temp_raw - min_temp_raw
    avg = flat_functions['ocean_temp_avg'](K_to_C(average_raw))
    min = flat_functions['ocean_temp_min'](K_to_C(min_temp_raw))
    max = flat_functions['ocean_temp_max'](K_to_C(max_temp_raw))
    temp_range = flat_functions['ocean_temp_range'](range_raw)
    return {
        "ocean_temp":{
            'avg':avg,
            'max':max,
            'min':min,
            'range':temp_range
        }
    }

#######################################################
#                  Waves                              #
#######################################################

def do_waves(raw_wave_data: numpy.array((3, HOURS_PER_WEEK), dtype=float), area_lat_long):
    #average wave height (average significant), maximum wave height (max max),
    #90th percentile (significant), average period, average steepness, minimum significant, maximum significant
    max_waves_raw = raw_wave_data[0]
    significant_wave_raw = raw_wave_data[1]
    period_raw = raw_wave_data[2]
    incomplete_switch = significant_wave_raw[-1] == -32767 #Deals with weeks that are incomplete - presumably just in the last year.
    if incomplete_switch:
        null_count = 0
        for i in range(HOURS_PER_WEEK):
            significant = significant_wave_raw[i]
            if significant > -32767:
                max = max_waves_raw[i]
                period = period_raw[i]
                if i == 0:
                    max_max_raw = sum_max = max
                    max_sig_raw = min_sig_raw = sum_sig = significant
                    sum_period = period
                else:
                    sum_max += max
                    sum_sig += significant
                    sum_period += period
                    if max_max_raw < max: max_max_raw = max
                    if max_sig_raw < significant: max_sig_raw = significant
                    elif min_sig_raw > significant: min_sig_raw = significant
            else: null_count += 1
        if null_count < HOURS_PER_WEEK-MIN_VALID_HOURS:
            good_hours = HOURS_PER_WEEK-null_count
            avg_max_raw = sum_max/good_hours
            avg_sig_raw = sum_sig/good_hours
            avg_period_raw = sum_period/good_hours
        else:
            return {
                "waves":{
                    "avg":255,
                    "avg_max":255,
                    "avg_period":255,
                    "max":255,
                    "max_significant":255,
                    "min_significant":255,
                }
            }
    else: #Complete week
        for i in range(HOURS_PER_WEEK):
            significant = significant_wave_raw[i]
            max = max_waves_raw[i]
            period = period_raw[i]
            if i == 0:
                max_max_raw = sum_max = max
                max_sig_raw = min_sig_raw = sum_sig = significant
                sum_period = period
            else:
                sum_max += max
                sum_sig += significant
                sum_period += period
                if max_max_raw < max: max_max_raw = max
                if max_sig_raw < significant: max_sig_raw = significant
                elif min_sig_raw > significant: min_sig_raw = significant
        avg_max_raw = sum_max/HOURS_PER_WEEK
        avg_sig_raw = sum_sig/HOURS_PER_WEEK
        avg_period_raw = sum_period/HOURS_PER_WEEK
    avg = flat_functions['waves_avg'](avg_sig_raw)
    avg_max = flat_functions['waves_avg_max'](avg_max_raw)
    avg_period = flat_functions['waves_avg_period'](avg_period_raw)
    max = flat_functions['waves_max'](max_max_raw)
    max_significant = flat_functions['waves_max_significant'](max_sig_raw)
    min_significant = flat_functions['waves_min_significant'](min_sig_raw)
    return {
        "waves":{
            "avg":avg,
            "avg_max":avg_max,
            "avg_period":avg_period,
            "max":max,
            "max_significant":max_significant,
            "min_significant":min_significant
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
