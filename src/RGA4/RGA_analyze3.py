import math
import time
import copy
import datetime
import collections

from astral import Astral, AstralError

from column_lists3 import (
    prime_vars,
    gap_vars,
    merge_columns,
    numerical_merge_columns,
    gap_values
)

from hig_utils import (
    safe_count,
    safe_get_float,
    merge_rows
)

from hig_stats import (
    Mean
)

from populate_columns3 import (
    interpolate_var
)

from project_specifics3 import (
    output_root,
    end_summer,
    end_winter
)
from hig_stats import *

#Could improve the code by finding commonality between monthly averages and the cycle code.  They're similar but currently totally separate.


source_columns = [x for x in merge_columns if x in prime_vars]

twilight_module = Astral() #Using 'Astral' module for civil twilight (http://pypi.python.org/pypi/astral/0.6.2)
twilight_module.solar_depression = 'civil'

####Move this function to hig_stats
def value_counts(X):
    counts = {}
    for value in X:
        try:
            counts[value] += 1
        except KeyError:
            counts.update([(value, 1)])
    return counts

#Test whether it's day, based on a start and end hour
def day_test(start, end, hour): #start is the start of light, end is the end, and hour is the decimal hour of the day. Values precise to 1 minute.
    if start < end:
        if start > hour or hour > end:
            day = False
        else:
            day = True
    else: #Civil night is entirely after midnight
        if hour > end and start > hour:
            day = False
        else:
            day = True
    return day

#Calculate response gap - a count of green, yellow, red, and exclusional components
#Also determine if the observation is sufficiently complete
def get_gap_and_completeness(hour, model):
    gaps = {}
    RG_dict = {
        "Green":0,
        "Yellow":0,
        "Red":0,
        "Exclude":0,
        "complete":True,
        "conditions":None,
    }
    obs_complete = True
    for key, component in model.iteritems():
        input_obs = [] #To populate with a list of observation values from the weather data table row
        for obs in component['obs']: input_obs.append(hour[obs])
        input_obs = tuple(input_obs) #Convert the list to a tuple so it can be passed by *
        (RG, complete) = component['logic'](*input_obs) #Send the relevant data pulled from the data row to the relevant model function pulled from the model
        RG_dict[RG] += 1
        if not complete or RG == 'Exclude':
            obs_complete = False
            gaps.update([(key, 'none')])
        else:
            gaps.update([(key, RG)])
    if RG_dict['Exclude'] > 0: RG_dict['conditions'] = 'Exclude'
    elif RG_dict['Red'] > 0: RG_dict['conditions'] = 'Red'
    elif RG_dict['Yellow'] > 0: RG_dict['conditions'] = 'Yellow'
    else: RG_dict['conditions'] = 'Green'
    #Function ultimately returns a total RG, a list of specific gap values for each key, and information on the completeness of the data
    return (RG_dict, gaps, obs_complete)


def update_summary(summary, (RG, gaps, complete)): #Bookkeeping to summarize response gaps.
    if RG['Exclude'] > 0:
        try: summary['Exclude'] += 1
        except KeyError: summary.update([ ('Exclude',1) ])
    else:
        for var in gap_vars:
            try:
                if var in gaps.keys(): summary[var + " " + gaps[var]] += 1
            except KeyError:
                summary.update([(var+" "+gaps[var],1)])
    return (summary, RG, gaps, complete) #passing these through is slightly messy... could rewrite better.


def annual_percentile_wind_rose(merged, dir_bins, P_list):
    #Make a wind rose where the radial axis is speed threshold for various percentiles
    start_time = time.time()
    data_lists = [[] for i in range(dir_bins)]
    for hour in merged['data']:
        wind = hour['wind']
        direction = hour['dir']
        if wind is not 'none' and direction is not 'none':
            i=0
            index = int(math.floor(direction * dir_bins / 360))
            data_lists[index].append(wind)
    percentile_rose_data = []
    for bin in data_lists:
        percentile_rose_data.append(Percentiles(bin,P_list))
    #then reorganize - not sure why there's so much re-organizing in this function.
    n_P = len(P_list)
    reorg_data = [[P,[]] for P in P_list]
    reorg_data = collections.OrderedDict(reorg_data)
    for i,P in enumerate(P_list):
        for bin in percentile_rose_data:
            if bin is not 'none':
                reorg_data[P].append(bin[i])
            else:
                reorg_data[P].append(0)
    writeable_data = []
    for i,P in enumerate(P_list):
        writeable_data.append({'P':P})
        for j,value in enumerate(reorg_data[P]):
            direction = j*360/dir_bins
            writeable_data[i].update([(direction,value)])
    return reorg_data, writeable_data


def component_velocity_exceedance_rose(merged, dir_bins, thresholds, component = True):
    start_time = time.time()
    print "  Component Velocity Exceedance for {0}...".format(merged['name']),
    directions_D = [360*i/dir_bins for i in range(dir_bins)]
    directions_R = [math.radians(d) for d in directions_D]
    dR_2 = math.radians(360.0/dir_bins/2) #Half a bin width in radians
    velocity_lists = collections.OrderedDict([(k,[]) for k in directions_R])
    i = 0
    for hour in merged['data']:
        wind = hour['wind']
        dir = hour['dir']
        if wind is not "none" and dir is not "none":
            if component:
                for direction in directions_R:
                        delta_direction = math.fabs((direction+dR_2) - math.radians(dir))
                        test = math.cos(delta_direction)
                        if test < 0:
                            velocity_lists[direction].append(0)
                        else:
                            velocity_lists[direction].append(test * wind)
            else: #Only record directions that lie within the bin
                for direction in directions_R: velocity_lists[direction].append(0)
                velocity_lists[directions_R[int(math.floor(dir * dir_bins / 360))]][i] = wind #replace the zero with actual wind in the correct bin
            i += 1
    data = collections.OrderedDict([(t,[]) for t in reversed(thresholds)])
    writeable_data = [collections.OrderedDict([('name',t)]) for t in thresholds]
    P_list = [1.0-x for x in thresholds] #convert thresholds (e.g. 0.01) to percentiles (e.g. 0.99)
    for i,direction in enumerate(directions_D):
        P = Percentiles(velocity_lists[directions_R[i]], P_list)
        for i,t in enumerate(thresholds):
            if P is not "none":
                data[t].append(P[i])
                writeable_data[i].update([(direction,P[i])])
            else:
                data[t].append(0)
                writeable_data[i].update([(direction,0)])
    print "took {0:.3f} seconds.".format(time.time()-start_time)
    return data, writeable_data

def summer_winter_rose_data(merged, thresholds, dir_bins):
    summer_winter_roses = [[],[]]
    for i in range(2): #2 seasons
        for threshold in thresholds:
            summer_winter_roses[i].append({'data':[0]*dir_bins, 'n':0})
    summer_winter_roses[0][0].update([('name','winter_{0}'.format(merged['name']))])
    summer_winter_roses[1][0].update([('name','summer_{0}'.format(merged['name']))])
    for hour in merged['data']:
        wind = hour['wind']
        direction = hour['dir']
        if wind != "none" and direction != 'none':
            day = hour['datetime'].timetuple().tm_yday
            if day < end_winter or day > end_summer: season = 0
            else: season = 1
            i=0
            index = int(math.floor(direction * dir_bins / 360))
            while i < len(thresholds) and wind > thresholds[i]:
                summer_winter_roses[season][i]['data'][index] += 1
                summer_winter_roses[season][i]['n'] += 1 #maybe easier to calculate this with sum at the end?
                i += 1
    return summer_winter_roses

def monthly_rose_data(merged, thresholds, dir_bins):
    #thresholds is a list, like [0, 11.3178, 17.4911, 24.6933]
    start_time = time.time()
    blank_month = []
    for threshold in thresholds:
        blank_month.append({'data': [0]*dir_bins, 'n': 0})
    monthly_rose_data_dicts = []
    for month in range(12):
        monthly_rose_data_dicts.append(copy.deepcopy(blank_month))
        for threshold in range(len(thresholds)):
            monthly_rose_data_dicts[month][threshold].update([('name',merged['name']+'_mon_'+str(month+1))])
    for hour in merged['data']:
        wind = hour['wind']
        direction = hour['dir']
        if wind != "none" and direction != 'none':
            month = hour['datetime'].timetuple().tm_mon - 1
            i=0
            index = int(math.floor(direction * dir_bins / 360))
            while i < len(thresholds) and wind > thresholds[i]:
                monthly_rose_data_dicts[month][i]['data'][index] += 1
                monthly_rose_data_dicts[month][i]['n'] += 1 #maybe easier to calculate this with sum at the end?
                i += 1
    print "  Getting data for monthly roses took {0:.3f} seconds".format(time.time()-start_time)
    return monthly_rose_data_dicts


def monthly_averages(merged):
    start_time = time.time()
    print("  Calculating monthly averages for " + merged['name']),
    default_month = {}
    for key in numerical_merge_columns:
        default_month.update([(key, dict([(stat_key,None) for stat_key in ["max", "min", "ave", "n", "stdev", "median","p25", "p75", "p2", "p5", "p95", "p98"]]))])
        default_month[key].update([('list',[])])
    detail_keys = sorted(default_month[numerical_merge_columns[0]].keys())
    monave = []
    for month in range(12):
        monave.append(copy.deepcopy(default_month)) #initializing the array of dictionaries of dictionaries
    for hour in merged['data']:
        month = hour['datetime'].timetuple().tm_mon - 1
        for key in numerical_merge_columns:
            if hour[key] != 'none':
                monave[month][key]['list'].append(hour[key])
    t = open(output_root+'/Text/Monthly_Averages/' + merged['name'] + "_monthly_averages.txt", "w")
    vis_months = []
    ceil_months = []
    for month in range(12):
        vis_months.append(value_counts(monave[month]['vis']['list']))
        ceil_months.append(value_counts(monave[month]['ceil']['list']))
        for key in numerical_merge_columns:
            minimum, maximum, n, ave, stdev, median, p25, p75, p5, p95, p2, p98 = simple_stats(monave[month][key]['list'])
            monave[month][key].update({
            'min': minimum,
            'max': maximum,
            'ave': ave,
            'n': n,
            'stdev': stdev,
            'median': median,
            'p25': p25,
            'p75': p75,
            'p5': p5,
            'p95': p95,
            'p2': p2,
            'p98': p98
            })
    t.write('month\t')
    for key in numerical_merge_columns:
        for detail in detail_keys:
            if detail != 'list':
                t.write(key + ' ' + detail + '\t')
    t.write('\n')
    month_number = 1
    for month in monave:
        t.write(str(month_number) + '\t')
        month_number += 1
        for key in numerical_merge_columns:
            for detail in detail_keys:
                if detail != 'list':
                    t.write(str(month[key][detail]) + '\t')
        t.write('\n')
    print "took","{0:.3f}".format(time.time()-start_time),"seconds"
    return {'data': monave, 'vis_months': vis_months, 'ceil_months': ceil_months, 'name': merged['name']}


def generic_matrix(merged,X,Y):
    X_res = (X['max']-X['min']) / X['bins']
    Y_res = (Y['max']-Y['min']) / Y['bins']
    matrix = []
    lists_for_stats = []
    for i in range(X['bins']):
        matrix.append([])
        lists_for_stats.append([])
        for j in range(Y['bins']):
            matrix[i].append(0)
    for hour in merged['data']:
        x = hour[X['name']]
        y = hour[Y['name']]
        if x != 'none' and y != 'none':
            x_index = int(math.floor((x-X['min'])/ X_res))
            if x_index >= X['bins']: x_index = -1
            y_index = int(math.floor((y-Y['min'])/ Y_res))
            if y_index >= Y['bins']: y_index = -1
            matrix[x_index][y_index] += 1
            lists_for_stats[x_index].append(y)
    stats = []
    for y_values in lists_for_stats:
        stats.append(simple_stats(y_values, dictionary=True))
    return [[matrix]], stats


def merge(data_dict, name, list_of_stations = [], merge_type = 'single', subsets = {}, nonstandard = {},  lat = 0.0, lon = 0.0, UTM_offset = 0, start_year = 'earliest', end_year = 'latest', interpolate_vars = False, models = []):
    start_time = time.time() #Report the time to run this function
    start_datetime = datetime.datetime(2100, 1, 1, 0, 0)
    end_datetime = datetime.datetime(1900, 1, 1, 0, 0)
    all_stations = list(data_dict.keys())
    all_years = set([])
    for station in list_of_stations:
        try:
            all_years.update(data_dict[station]['Years'])
            ref_dict = data_dict[station]['summary']
            if ref_dict['start'] < start_datetime: start_datetime = ref_dict['start']
            if ref_dict['end'] > end_datetime: end_datetime = ref_dict['end']
        except KeyError:
            print "***ERROR***: " + station + " does not appear to be a station you defined: " + str(
                all_stations) + "\nStation skipped"
    limited_years = all_years
    if start_year != 'earliest':
        if start_datetime < datetime.datetime(int(start_year),1,1,0,0): start_datetime = datetime.datetime(start_year,1,1,0,0)
        limited_years.intersection(range(int(start_year),2100))
    if end_year != 'latest':
        if end_datetime > datetime.datetime(int(end_year),12,31,23,59): end_datetime = datetime.datetime(end_year,12,31,23,59)
        limited_years.intersection(range(1900,int(end_year)+1))
    #A_lon = lon * -1 #since Astral is confused about longitude sign
    A_lon = lon #Astral may no longer be confused???
    adjust_time_to_UTM = datetime.timedelta(hours=UTM_offset)
    whole_timespan = datetime.timedelta(0)
    whole_timespan += end_datetime - start_datetime
    total_hours = int(math.floor(whole_timespan.total_seconds() / 3600)) + 1
    merged_dataset = []    #currently this data is not preserved, only the averages are
    merged_averaged = []
    for hour in range(total_hours):
        merged_dataset.append({})
    print "  Merging stations: {0} hours in {1} Stations for {2} (merge-type = {3})".format(total_hours, list_of_stations,name,merge_type),
    if all_years != limited_years: print "Years {0} trimmed to just {1}.".format(all_years,limited_years),
    last_index, dup_count = None, 0
    for station in list_of_stations: #seems somewhat redundant with similar loop at start of function
        try:
            dataset = data_dict[station]['data']
            for row in dataset: #Dataset should already be sorted by time, but it's possible there will be multiple values in the same hour (but different exact times)
                time_increment = datetime.timedelta(0)
                time_increment += row['datetime'] - start_datetime
                index = int(math.floor(time_increment.total_seconds() / 3600))
                dup_count += 1
                if index == last_index: #Deals with cases where the input data had multiple values in the same hour. Averages numbers, but chooses randomly for categoricals.
                    merged_row = merge_rows(merged_dataset[index][station],row,dup_count-1, omit_rows = {'datetime'})
                else:
                    merged_row = row
                    dup_count = 1
                    last_index = index
                try:
                    merged_dataset[index].update([(station,merged_row)]) #A dictionary of rows with the same index
                except IndexError: pass #Sneaky! Supposedly this deals with years not covered by the input range.
        except KeyError:
            print "***ERROR***: ", station + " skipped."
    empty_row_tuples = [('datetime',0),('day',0),('empty',True)]
    extra_keys = set([])
    for in_dataset in nonstandard.values():
        extra_keys.update(in_dataset.values())
    extra_keys = list(extra_keys)
    if len(extra_keys) > 0:  print "adding extra keys:",extra_keys,
    for key in merge_columns + extra_keys:
        empty_row_tuples.append((key,'none'))
    empty_row = collections.OrderedDict(empty_row_tuples)
    overwrite_count = 0
    for hour in range(total_hours):
        date_time = start_datetime + datetime.timedelta(hours=hour)
        date = date_time.date()
        hour_of_day = date_time.timetuple().tm_hour
        decimal_hour_of_day = hour_of_day + float(date_time.timetuple().tm_min)/60
        try:
            start_light = twilight_module.dawn_utc(date, lat, A_lon) - adjust_time_to_UTM #technically should use UTC date, not local date, but error of <= 1 day won't matter for civil dawn/dusk
            end_light = twilight_module.dusk_utc(date, lat, A_lon) - adjust_time_to_UTM
            start_light_hour = float(start_light.hour) + float(start_light.minute) / 60 + float(start_light.second) / 3600
            end_light_hour = float(end_light.hour) + float(end_light.minute) / 60 + float(end_light.second) / 3600
            daylight_bool = day_test(start_light_hour, end_light_hour, decimal_hour_of_day)
        except AstralError: #It throws an error if there's no dawn/dusk.  If an error is thrown, assume it's day if it's April through September, night otherwise
            if date_time.month in range(4, 10):
                daylight_bool = True
            else:
                daylight_bool = False
        stored_data = copy.deepcopy(empty_row)
        for station in list_of_stations:
            try:
                row = merged_dataset[hour][station]
                for key in source_columns:
                    try:
                        if key in subsets[station]:
                            test = True
                        else:
                            test = False
                    except KeyError: test = True #If the station isn't mentioned in subsets, assume all rows are good.
                    try:
                        key2 = nonstandard[station][key]
                    except KeyError: key2 = key #If the station isn't mentioned, or if the key isn't mentioned, behave normally
                    if test and row[key] != 'none':
                        stored_data['empty'] = False
                        if merge_type == 'single':
                            if stored_data[key2] == 'none': stored_data[key2] = row[key]
                            else: overwrite_count += 1
                                #print 'Getting two different sources for same data in merge_single_measures_only - only first value used.\n'+'key: '+key+'  value 1: '+str(stored_data[key])+'  value 2: '+str(obs[key])
                                #raise Exception(error)
                        elif merge_type == 'average':
                            if stored_data[key2] == 'none':
                                stored_data[key2] = row[key] #list will be overwritten if there are multiple values
                            else: #A rather odd way of dealing with this situation - a temporary variable is created that allows the value to be updated
                                try:
                                    stored_data[key2] = stored_data[key2]*temp_ave_notes[key]+row[key]
                                    temp_ave_notes[key] += 1
                                    stored_data[key2] /= temp_ave_notes[key]
                                except NameError:
                                    temp_ave_notes = {key:2}
                                    stored_data[key2] = (stored_data[key2]+row[key])/2
                                except KeyError:
                                    temp_ave_notes.update([(key,2)])
                                    stored_data[key2] = (stored_data[key2]+row[key])/2
            except KeyError: pass #There was no data from this station at this hour.
        stored_data.update([
            ('datetime', date_time),
            ('day', daylight_bool)
        ])
        merged_averaged.append(stored_data)

    if interpolate_vars:
        for var in interpolate_vars:
            interpolate_var(merged_averaged,var, name)
    if overwrite_count > 0: print "\nWARNING:",overwrite_count,"cases where multiple data values fell in the same hour & column.\nUsing merge_single_measures_only, so only the first case was used."
    print "took","{0:.3f}".format(time.time()-start_time),"seconds",
    return {
        "summary": {"lat": lat, "lon": lon},
        "total_hours": total_hours,
        "data": merged_averaged,
        "Years": limited_years,
        "stations": list_of_stations,
        "name": name,
        "timezone": UTM_offset,
        "location": (lon, lat)
    }


def wind_dir(merged, dir_bins, wind_threshold, wind_type):
    dir_list = []
    wind_list = []
    for hour in merged['data']:
        dir_list.append(hour['dir'])
        wind_list.append(hour[wind_type]) #either 'wind' or 'gust'
    data_list = generate_directions_for_rose(dir_list,wind_list,wind_threshold)
    dir_array = dir_binning(data_list,dir_bins)
    return {'data': dir_array, 'name': merged['name'], 'n': len(data_list)}

def generate_directions_for_rose(dir_list,wind_list,wind_threshold):
    data_list = []
    for i in range(len(dir_list)):
        direction = dir_list[i]
        wind = wind_list[i]
        if direction != "none" and wind != "none":
            if wind > wind_threshold:
                data_list.append(direction)
    return data_list

def dir_binning(data_list,dir_bins):
    dir_array = [0]*dir_bins
    for direction in data_list:
        index = int(math.floor(direction * dir_bins / 360))
        dir_array[index] += 1
    return dir_array


summary_columns_to_initialize_float = [
    "Red_proportion_maximum", "Red_proportion_minimum", "Red_proportion_estimate", "Red_proportion_best",
    "Yellow_proportion_maximum", "Yellow_proportion_minimum", "Yellow_proportion_estimate", "Yellow_proportion_best",
    "Green_proportion_maximum", "Green_proportion_minimum", "Green_proportion_estimate", "Green_proportion_best"
]
def init_RG_summary(name, lat, lon, total_hours):
    summary_dict = {
    "name": name,
    "total_hours": total_hours,
    "lat": lat,
    "lon": lon
    }
    for var in summary_columns_to_initialize_float:
        summary_dict.update([ (var, None) ])
    for var in gap_vars: #gap_vars and gap_values are global variables in column_lists
        for gap_type in gap_values + ['none']:
            summary_dict.update([(var + " " + gap_type, 0)]) #formulaic keys like "wind Green"
    return summary_dict


def merge_RGA(data, limit_set, name): #limit_set is a complete model, like OW, with a number of components, like wind, wave...
    RGA_data = []
    summary = init_RG_summary(name, data['summary']['lat'], data['summary']['lon'], data['total_hours'])
    for hour in data['data']:
        (summary, RG, gaps, complete) = update_summary(summary, get_gap_and_completeness(hour, limit_set))
        if complete:
            safe_count('Compete',summary)
            if RG['Red'] > 0:
                conditions = "Red"
                detailed_conditions = "Red{0}".format(RG['Red']) #includes count of red conditions
                safe_count('Red',summary)
                safe_count('Red_complete',summary)
            elif RG['Yellow'] > 0:
                conditions = "Yellow"
                detailed_conditions = "Yellow{0}".format(RG['Yellow']) #includes count of yellow conditions
                safe_count('Yellow',summary)
                safe_count('Yellow_complete',summary)
            else:
                conditions = "Green"
                detailed_conditions = "Green{0}".format(RG['Green']) #Might as well count up the greens.
                safe_count('Green',summary)
                safe_count('Green_complete',summary)
        else:
            safe_count('Incomplete',summary)
            detailed_conditions = "Ambiguous"
            if RG['Red'] > 0:
                conditions = "Red"
                safe_count('Red',summary)
                safe_count('Red_incomplete',summary)
            elif RG['Yellow'] > 0:
                conditions = "Yellow"
                safe_count('Yellow',summary)
                safe_count('Yellow_incomplete',summary)
            else:
                conditions = "Green"
                safe_count('Green',summary)
                safe_count('Green_incomplete',summary)
        if hour['day']:
            safe_count('day',summary)
        else:
            safe_count('night',summary)
        RGA_hour = gaps
        RGA_hour.update({
            'datetime': hour['datetime'],
            'day': hour['day'],
            'empty': hour['empty'],
            'complete': complete,
            'conditions': conditions,
            'detailed_conditions':detailed_conditions,
            'RG': RG
        })
        RGA_data.append(RGA_hour)
    return {
        "summary": summary,
        "data": RGA_data,
        "name": name,
        "Years": data['Years']
    }


def min_max_est_best(min, max, est): #Check if an estimate lies in the accepted range. If so, return it. If not, force it in the range.
    if est > max:
        return max
    elif est < min:
        return min
    else: return est


def min_max_est_best_GYR(min_G, max_G, est_G, min_Y, max_Y, est_Y, min_R, max_R, est_R):
    first_G = min_max_est_best(min_G, max_G, est_G)
    first_Y = min_max_est_best(min_Y, max_Y, est_Y)
    first_R = min_max_est_best(min_R, max_R, est_R)
    YG = first_G + first_Y
    try: shift_ratio = (1.0-first_R)/YG
    except ZeroDivisionError: return 0.0, 0.0, 1.0
    return first_G*shift_ratio, first_Y*shift_ratio, first_R


def update_proportion_estimates(source_dict):
    try: total = source_dict['total_hours']
    except KeyError: total = 0
    yellow_complete = float(safe_get_float('Yellow_complete',source_dict))
    green_complete = float(safe_get_float('Green_complete',source_dict))
    if total > 0:
        red = float(safe_get_float('Red',source_dict))
        green = float(safe_get_float('Green',source_dict))
        source_dict['Red_proportion_minimum'] = red / total
        source_dict['Red_proportion_maximum'] = 1.0 - (green_complete + yellow_complete)/total
        source_dict['Green_proportion_minimum'] = green_complete / total
        source_dict['Green_proportion_maximum'] = green/total
        source_dict['Yellow_proportion_minimum'] = yellow_complete/total
        source_dict['Yellow_proportion_maximum'] = 1.0 - (red + green_complete)/total
    else: print "ERROR: no hours in dataset"
    red_complete = float(safe_get_float('Red_complete',source_dict))
    total_complete = red_complete + yellow_complete + green_complete
    if total_complete > 0:
        source_dict['Red_proportion_estimate'] = red_complete / total_complete
        source_dict['Yellow_proportion_estimate'] = yellow_complete / total_complete
        source_dict['Green_proportion_estimate'] = green_complete / total_complete
        source_dict['Green_proportion_best'], source_dict['Yellow_proportion_best'], source_dict['Red_proportion_best'] = min_max_est_best_GYR(
            source_dict['Green_proportion_minimum'],
            source_dict['Green_proportion_maximum'],
            source_dict['Green_proportion_estimate'],
            source_dict['Yellow_proportion_minimum'],
            source_dict['Yellow_proportion_maximum'],
            source_dict['Yellow_proportion_estimate'],
            source_dict['Red_proportion_minimum'],
            source_dict['Red_proportion_maximum'],
            source_dict['Red_proportion_estimate']

        )
    else: print "No complete data - proportion estimates undefined"

def rgi_calculations(all_summaries):
    for summary in all_summaries:
        update_proportion_estimates(summary)


def dawn_dusk((lon, lat), timezone): #returns dawn and dusk as floats between 0 and 1, where 0.5 = noon
    start_datetime = datetime.datetime(2011, 1, 1, 0, 0)
    adjust_time_to_UTM = datetime.timedelta(hours=timezone)
    #A_lon = lon * (-1) #For Astral - need to invert longitudes
    A_lon = lon #Confused no longer?
    dawn_dusk = []
    for day in range(366):
        date_time = start_datetime + datetime.timedelta(days=day)
        date = date_time.date()
        try:
            start_light = twilight_module.dawn_utc(date, lat, A_lon) - adjust_time_to_UTM
            end_light = twilight_module.dusk_utc(date, lat, A_lon) - adjust_time_to_UTM
            dawn_dusk.append({
            'dawn': (float(start_light.minute) / 60 + start_light.hour) / 24,
            'dusk': (float(end_light.minute) / 60 + end_light.hour) / 24,
            'test': True
            })
        except:
            dawn_dusk.append({
            'dawn': 0,
            'dusk': 0,
            'test': False
            })
    return dawn_dusk


def compile_summer_winter(name,cycle_output, model_name, site_name): #Cycle output should have 3 rows, one for end of winter, one for summer, and one for beginning of winter.
    if len(cycle_output['bins']) > 0:
        if len(cycle_output['bin_def']) > 3: print "WARNING: Extra data going to compile_summer_winter - maybe some problem here: {0}".format(cycle_output)
        for bin in cycle_output['bins']:
            update_proportion_estimates(bin)
        winter_red = Mean([safe_get_float('Red_proportion_best',cycle_output['bins'][0]),safe_get_float('Red_proportion_best',cycle_output['bins'][2])])
        winter_green = Mean([safe_get_float('Green_proportion_best',cycle_output['bins'][0]),safe_get_float('Green_proportion_best',cycle_output['bins'][2])])
        winter_yellow = 1.0 - winter_red - winter_green
        return {
            'name': name,
            'model':model_name,
            'site':site_name,
            'winter_red':winter_red,
            'winter_yellow':winter_yellow,
            'winter_green':winter_green,
            'summer_red':safe_get_float('Red_proportion_best',cycle_output['bins'][1]),
            'summer_yellow':safe_get_float('Yellow_proportion_best',cycle_output['bins'][1]),
            'summer_green':safe_get_float('Green_proportion_best',cycle_output['bins'][1])
        }


def RGA_timeseries_analysis(RGA,range_list):
    #Ambiguous means possibly true, but includes definitely true cases (so not really "ambiguous" per se)
    start_time = time.time()
    print "  Executing timeseries analysis for {0} with {1} hour sectioning".format(RGA['name'],range_list),
    tally_sheet = []
    n = len(RGA['data'])
    complete = 0
    total_hours = 0
    for i in range(n):
        bool_row = {'conditions':None, 'detailed_conditions':None}
        for number in range_list:
            bool_row.update({
                'Ambiguous_Green_{0:02d}'.format(number): True,
                'Green_{0:02d}'.format(number): True,
                'Ambiguous_Green_or_Yellow_{0:02d}'.format(number): True,
                'Green_or_Yellow_{0:02d}'.format(number): True
            })
        tally_sheet.append(bool_row)
    for i,row in enumerate(RGA['data']):
        total_hours += 1
        if row['complete']: complete += 1
        tally_sheet[i]['conditions'] = row['conditions']
        tally_sheet[i]['detailed_conditions'] = row['detailed_conditions']
        tally_sheet[i].update([ ('datetime',row['datetime']) ])
        for number in range_list:
            for j in range(number):
                index = i-j
                if index >= 0:
                    if row['conditions'] == 'Red':
                        tally_sheet[index]["Ambiguous_Green_{0:02d}".format(number)] = False
                        tally_sheet[index]["Green_{0:02d}".format(number)] = False
                        tally_sheet[index]["Ambiguous_Green_or_Yellow_{0:02d}".format(number)] = False
                        tally_sheet[index]["Green_or_Yellow_{0:02d}".format(number)] = False
                    else:
                        if row['conditions'] == 'Yellow':
                            tally_sheet[index]["Green_{0:02d}".format(number)] = False
                            tally_sheet[index]["Ambiguous_Green_{0:02d}".format(number)] = False
                        if row['detailed_conditions'] == 'Ambiguous': #This also includes all incompletes
                            tally_sheet[index]["Green_{0:02d}".format(number)] = False
                            tally_sheet[index]["Green_or_Yellow_{0:02d}".format(number)] = False
    for number in range_list:
        for i in range(number):
            index = -1*i #Deal with the end of the list
            tally_sheet[index]["Green_{0:02d}".format(number)] = False
            tally_sheet[index]["Green_or_Yellow_{0:02d}".format(number)] = False
    tallies = {'conditions':None, 'detailed_conditions':None}
    for key in tally_sheet[0]:
        tallies.update([ (key,0) ])
    for row in tally_sheet:
        for number in range_list:
            ambiguous_green = "Ambiguous_Green_{0:02d}".format(number)
            green = "Green_{0:02d}".format(number)
            ambiguous_green_or_yellow = "Ambiguous_Green_or_Yellow_{0:02d}".format(number)
            green_or_yellow = "Green_or_Yellow_{0:02d}".format(number)
            if row[green]: tallies[green] += 1
            elif row[ambiguous_green]: tallies[ambiguous_green] += 1
            if row[green_or_yellow]: tallies[green_or_yellow] += 1
            elif row[ambiguous_green_or_yellow]: tallies[ambiguous_green_or_yellow] += 1
    summary = {}
    for number in range_list:
        types = {
            "ambiguous_green": "Ambiguous_Green_{0:02d}".format(number),
            "green": "Green_{0:02d}".format(number),
            "ambiguous_green_or_yellow": "Ambiguous_Green_or_Yellow_{0:02d}".format(number),
            "green_or_yellow": "Green_or_Yellow_{0:02d}".format(number)
        }
        ambiguous_green_total = tallies[types["ambiguous_green"]]
        ambiguous_green_or_yellow_total = tallies[types["ambiguous_green_or_yellow"]]
        green_total = tallies[types['green']]
        green_or_yellow_total = tallies[types['green_or_yellow']]
        if total_hours > 0:
            green_max = float(green_total+ambiguous_green_total)/total_hours
            green_min = float(green_total)/total_hours
            green_or_yellow_max = float(green_or_yellow_total+ambiguous_green_or_yellow_total)/total_hours
            green_or_yellow_min = float(green_or_yellow_total)/total_hours
        else:
            green_max = 1.0
            green_min = 0.0
            green_or_yellow_max = 1.0
            green_or_yellow_min = 0.0
        if complete > 0:
            green_est = float(green_total)/complete
            green_or_yellow_est = float(green_or_yellow_total)/complete
        else:
            green_est = 0.0
            green_or_yellow_est = 0.0
        green_best = min_max_est_best(green_min, green_max, green_est)
        green_or_yellow_best = min_max_est_best(green_or_yellow_min, green_or_yellow_max, green_or_yellow_est)
        summary.update({
            "Green_{0:02d}_max".format(number):green_max,
            "Green_{0:02d}_min".format(number):green_min,
            "Green_{0:02d}_est".format(number):green_est,
            "Green_{0:02d}_best".format(number):green_best,
            "Green_or_Yellow_{0:02d}_max".format(number):green_or_yellow_max,
            "Green_or_Yellow_{0:02d}_min".format(number):green_or_yellow_min,
            "Green_or_Yellow_{0:02d}_est".format(number):green_or_yellow_est,
            "Green_or_Yellow_{0:02d}_best".format(number):green_or_yellow_best,
        })
    print " (Time: {0:.2f} seconds)".format(time.time()-start_time)
    return summary, [tallies]+tally_sheet


def add_overall_summary(simple, overall):
    n = len(overall)
    error = False
    for i in range(n):
        try:
            if simple[i]['name'] == overall[i]['name']: #Kind of a hack, though we check for errors.  Requires the two summaries to have exactly the same order and number of indices.
                simple[i].update([
                    ('overall_red', overall[i]['Red_proportion_best']),
                    ('overall_yellow', overall[i]['Yellow_proportion_best']),
                    ('overall_green', overall[i]['Green_proportion_best'])
                ])
            else:
                simple[i].update([('overall', 'ERROR')])
                error = True
        except (IndexError, TypeError):
            error = True
    if error: print "***ERROR***: Couldn't combine summaries completely - see simple_summary output"


def cycle_data(RGA_list, name, days_per_bin=None, div_bins=[]):
    #Two alternatives, either regularly spaced bins, or div_bins with specific start dates.
    #EXAMPLE: If div_bins = [0,20,100], three bins are generated, one from day 0 to day 19, one from day 20 to day 99, and one from day 100 to the end of the year.
    #If days_per_bin is non-zero, it's used and div_bins is ignored.  If both are empty, an error is returned.
    if not days_per_bin:
        print "  Calculating cycle data for " + name + " with " + str(div_bins) + " specifically assigned bins"
    else:
        print("  Calculating cycle data for " + name + " with " + str(days_per_bin) + "-day bins")
    Years = set([])
    for RGA in RGA_list:
        Years.update(RGA['Years'])
    Years = sorted(list(Years))
    if len(Years) > 0: #If there's data...
        if days_per_bin > 0:
            div_bins = []
            i = 0
            while i <= 366:
                div_bins.append(i)
                i += days_per_bin
        n_bins = len(div_bins)
        default_bin_dict = {
            'name': name,
            'start': 0,
            'end': 0,
            'complete': 0
        }
        bins = []
        for i in range(n_bins): #create empty bins.
            bins.append(copy.deepcopy(default_bin_dict))
            bins[i]['start'] = div_bins[i]
            if i < n_bins - 1:
                bins[i]['end'] = div_bins[i + 1]
            else:
                bins[i]['end'] = 367

        def get_index(day): #Would be better written as a while statement
            for i in range(n_bins):
                if bins[i]['start'] <= day < bins[i]['end']: return i
            raise LookupError("get_index in cycle_data failed")
        for RGA in RGA_list:
            for hour in RGA['data']:
                this_day = hour['datetime'].timetuple().tm_yday
                this_year = hour['datetime'].timetuple().tm_year
                index = get_index(this_day) #Figure out what bin the particular observation lies in

                safe_count('total_hours',bins[index])
                safe_count('total_hours_{0}'.format(this_year),bins[index])
                safe_count(hour['conditions'],bins[index])
                safe_count(hour['detailed_conditions'],bins[index]) #Detailed conditions include a count of the number of parameters of a certain color, so "Green3" means three parameters, all green. "Yellow2" means two yellow parameters, and the rest green. "Red5" means 5 red parameters and all the reset yellow or green.
                if hour['complete']:
                    safe_count('complete',bins[index])
                    safe_count('{0}_complete'.format(hour['conditions']),bins[index])
                    safe_count('{0}_{1}_complete'.format(this_year,hour['conditions']),bins[index])

                for var in gap_vars:
                    try: safe_count(var + "_RG_" + hour[var],bins[index])
                    except KeyError: pass #Not all gap vars are present in every RGA
        return {'name': name, 'Years': Years, 'bins': bins, 'bin_def':div_bins}
    else:
        print "WARNING: No data for cycle, empty structure returned"
        return {'name': name, 'Years': Years, 'bins': [], 'bin_def':div_bins}


def average_merge(merged, monthly_average):
    #Calculate averages in two ways - an average of hours, and an average of months.
    average_dict = collections.OrderedDict([("name",merged['name'])])
    for column in numerical_merge_columns:
        hourly_column = "hourly_"+column
        monthly_column = "monthly_"+column
        average_dict.update([(hourly_column,0.0),(monthly_column,0.0)])
        hourly_list = []
        for hour in merged['data']:
            value = hour[column]
            if value != 'none': hourly_list.append(value)
        average_dict[hourly_column] = Mean(hourly_list)
        monthly_list = []
        for month in monthly_average['data']:
            value = month[column]['ave']
            if value != 'none': monthly_list.append(value)
        average_dict[monthly_column] = Mean(monthly_list)
    return average_dict

def completeness_percentages(merged): #May be a more efficient way to do this, but this is simple.
    if len(merged['data']) > 0:
        completeness_dict = collections.OrderedDict([("name",merged['name'])])
        for column in merge_columns:
            total_rows = 0
            rows_with_data = 0
            for row in merged['data']:
                total_rows += 1
                if row[column] != "none": rows_with_data += 1
            completeness_dict.update([(column,float(rows_with_data)/total_rows)])
        return completeness_dict

