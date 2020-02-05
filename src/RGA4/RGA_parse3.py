import csv
import re
import datetime
from RGA_output3 import write_csv_from_list_of_dicts
from project_specifics3 import output_root, data_root

from column_lists3 import prime_vars
from convert_functions3 import smart_units

#Possible changes
#Modify NBDC input to take the alternate multi-column date format

blank_values = ['',None,'null','none','null']

def update_summary(row, summary):
    for key in prime_vars:
        if row[key] != "none": summary[key] += 1


def init_summary(csv_name, lat, lon):
    return_dict = dict((var, 0) for var in prime_vars + ['start', 'end', 'total_hours'])
    return_dict.update([('name', csv_name), ('lat', lat), ('lon', lon)])
    return return_dict


def write_parsed(name, dataset):
    write_csv_from_list_of_dicts(output_root+'/Text/Parsed/{0}_parsed.csv'.format(name), dataset['data'], ['datetime'] + prime_vars + ['steep'])


def assign_value(this_row, exclude_value, var, column, scaler=1, unit="none"):
    if column == 'null':
        return "none"
    else:
        try:
            value_string = this_row[column].strip()
            if value_string == exclude_value or value_string.lower() in blank_values:
                return "none"
            elif unit == "none":
                value = float(value_string) * scaler
                return value
            else:
                #value = convert_dict[var](float(value_string),unit)
                try: value = smart_units('{0} {1}'.format(value_string, unit))
                except NameError as error_text:
                    print value_string
                    print unit
                    print this_row
                    print error_text
                    raise Exception
                return value
        except TypeError:
            return "none"
        except ValueError:
            return "none"
        except KeyError as error_text:
            print '***ERROR*** Column {0} not found in {1}'.format(column,this_row.keys())
            print error_text
            raise Exception
            #return "none"


def get_parsed_row(row, reader_list, obs_time, ignore_values): #initialize the row with no data other than time.
    parsed_row = dict((var, 'none') for var in prime_vars)
    parsed_row.update([('datetime', obs_time)])
    for key in reader_list:
        parsed_row[key] = assign_value(row, ignore_values[key], *reader_list[key])
    return parsed_row


def calculate_steepness(dataset):
    for row in dataset['data']:
        if row['wave'] != "none" and row['period'] != "none":
            try:
                row['steep'] = row['wave'] / (9.81 * row['period'] * row['period'])
            except TypeError:
                print "***ERROR*** Couldn't calculate steepness. ", row['wave'], row['period']
        else:
            row['steep'] = "none"


def get_reader_list(station):
    reader_list = {}
    for var in prime_vars:
        try: column = station[var+'_column']
        except KeyError: column = 'null'
        try: convert = float(station[var+'_convert'])
        except KeyError: convert = 1.0
        try: unit = station[var+'_unit']
        except KeyError: unit = 'none'
        reader_list.update([(var,(var, column,convert,unit))])
    return reader_list


def init_for_inupt(file_name, station):
    lat = station['lat']
    lon = station['lon']
    in_timeoffset = station['time_offset']
    Weather = []
    Years = set([])
    summary = init_summary(file_name, lat, lon)
    time_adjust = datetime.timedelta(hours=in_timeoffset)
    min_datetime = datetime.datetime(2100, 1, 1, 0, 0)
    max_datetime = datetime.datetime(1900, 1, 1, 0, 0)
    reader_list = get_reader_list(station)
    return Weather, Years, summary, time_adjust, min_datetime, max_datetime, reader_list


def set_ignore_values(station):
    if 'ignore_values' not in station:
        if 'ignore_value' in station:
            return dict((var, station['ignore_value']) for var in prime_vars)
        else:
            return dict((var, 'null') for var in prime_vars)
    else:
        for var in prime_vars:
            if var not in station['ignore_values']: station['ignore_values'].update([(var,'null')])
        return station['ignore_values']

def normalize_identical_columns(f, file_name):
    header_line = f.readline()
    headers = header_line.split(',')
    changed = False
    duplicated_headers = []
    for i, header in enumerate(headers):
        if header in headers[i+1:]:
            changed = True
            duplicated_headers.append(header)
            j=0
            for k,item in enumerate(headers):
                if item == header:
                    item = '{0}_{1}'.format(header,j)
                    headers[k] = item
                    j += 1
    if changed:
        print "WARNING: {0} file contains multiple columns with the same name - appending _0, _1, etc. to make them unique.".format(file_name)
        temp_filename = '{0}.tmp'.format(file_name)
        with open(temp_filename, 'w') as temp_file:
            temp_file.write(','.join(headers))
            next_line = f.readline()
            while next_line:
                temp_file.write(next_line)
                next_line = f.readline()
        try:
            temp_file = open(temp_filename, 'rU')
        except TypeError:
            raise Exception("Invalid file name: " + temp_filename)
        return temp_file
    else:
        f.seek(0)
        return f

def extract_csv_data(station, years_in):
    if 'file_name' in station:
        file_names = [data_root+station['file_name']]
    else:
        file_names = [data_root+file for file in station['file_names']]
    first = True
    for file_name in file_names:
        Weather = []
        try:
            f = open(file_name, 'rU')
        except TypeError:
            raise Exception("Invalid file name: " + file_name)
        f= normalize_identical_columns(f, file_name)
        header = [h.strip() for h in f.next().split(',')] #Removes whitespace from header row
        reader = csv.DictReader(f, delimiter=',', quotechar='"', fieldnames=header)
        if first:
            all_Weather, Years, summary, time_adjust, min_datetime, max_datetime, reader_list = init_for_inupt(file_name,station)
            first = False
        try:
            qual_column = station['qual_column']
            qual_control = True
        except KeyError:
            qual_column = "null"
            qual_control = False
        reject_rows = 0
        for row in reader:
            if not qual_control or row[qual_column] not in station['qual_reject']:
                if station['time_single_column']:
                    try:
                        date_text = row[station['time_column']]
                    except KeyError:
                        print '***ERROR*** Time column ' + station['time_column'] + ' not found, file not processed.	"null" is not an option for time.'
                        return summary
                    try:
                        obs_time = datetime.datetime.strptime(date_text, station['date_format']) + time_adjust #date and time stored in local time from the start
                        time_success = True
                    except ValueError:
                        print 'WARNING: Row without any time-value detected - not read'
                        time_success = False
                else:
                    try:
                        year = int(float(row[station['time_column']['Year']]))
                        month = int(float(row[station['time_column']['Month']]))
                        day = int(float(row[station['time_column']['Day']]))
                        hour = int(float(row[station['time_column']['Hour']]))
                        if station['time_column']['Minute'] == "null": minute = 0
                        else: minute = int(float(row[station['time_column']['Minute']]))
                    except KeyError as error_text:
                        print '***ERROR*** Time columns not found,',file_name,'file not processed.	"null" is not an option for time.'
                        print row
                        print row[station['time_column']['Year']]
                        print error_text
                        raise Exception
                    obs_time = datetime.datetime(year, month, day,hour,minute) + time_adjust #date and time stored in local time from the start
                    time_success = True

                if time_success:
                    year = obs_time.year
                    if year in years_in:
                        if obs_time > max_datetime: max_datetime = obs_time
                        if obs_time < min_datetime: min_datetime = obs_time
                        Years.add(year)
                        ignore_values = set_ignore_values(station)
                        parsed_row = get_parsed_row(row, reader_list, obs_time, ignore_values)
                        update_summary(parsed_row, summary)
                        Weather.append(parsed_row)
            else: reject_rows += 1
        all_Weather += Weather
    if reject_rows > 0: print "Warning: {0} rows rejected based on quality flag in column {1}.".format(reject_rows,qual_column)
    date_period = datetime.timedelta(0)
    date_period += max_datetime - min_datetime
    summary['start'] = min_datetime
    summary['end'] = max_datetime
    summary['total_hours'] = date_period.total_seconds() / 3600 #number of hours between the first and last observation
    return {'summary': summary, 'data': all_Weather, 'Years': Years}


def extract_Weatherspark_data(station, years_in):
    file_name = data_root+station['file_name']
    try:
        f = open(file_name, 'rU')
    except TypeError:
        raise Exception("Invalid file name: " + file_name)
    reader = csv.DictReader(f, delimiter=',', quotechar='"')
    (Weather, Years, summary, time_adjust, min_datetime, max_datetime, reader_list) = init_for_inupt(file_name,station)
    for row in reader:
        year = int(float(row['Year Local'])) #Weatherspark stores some numbers in float format, like "1948.0" and if you directly convert it to an int it throws an error, so instead we convert first to a float, then to an int.
        month = int(float(row['Month Local']))
        day = int(float(row['Day Local']))
        hour = int(float(row['Hour Local']))
        obs_time = datetime.datetime(year, month, day,hour) + time_adjust #date and time stored in local time from the start
        year = obs_time.year #why do we do this?
        if year in years_in:
            if obs_time > max_datetime: max_datetime = obs_time
            if obs_time < min_datetime: min_datetime = obs_time
            Years.add(year)
            ignore_values = set_ignore_values(station)
            parsed_row = get_parsed_row(row, reader_list, obs_time, ignore_values)
            update_summary(parsed_row, summary)
            Weather.append(parsed_row)
    date_period = datetime.timedelta(0)
    date_period += max_datetime - min_datetime
    summary['start'] = min_datetime
    summary['end'] = max_datetime
    summary['total_hours'] = date_period.total_seconds() / 3600 #number of hours between the first and last observation
    return {'summary': summary, 'data': Weather, 'Years': Years}


def extract_onlns_data(station, years_in):
    file_name = data_root+station['file_name']
    try:
        f = open(file_name, 'r')
    except TypeError:
        raise Exception("Invalid file name: " + file_name)
    reader = f.readlines()
    (Weather, Years, summary, time_adjust, min_datetime, max_datetime, reader_list) = init_for_inupt(file_name,station)
    for row_string in reader:
        row_list = row_string.split() #Each word in the row will be an item in the list.
        row = dict((i, row_list[i]) for i in range(len(row_list)))
        try:
            date_text = row_list[station['time_column']]
        except KeyError:
            print '***ERROR*** Time column ' + station[
                'time_column'] + ' not found, file not processed.	"null" is not an option for time.'
            return summary
        try:
            obs_time = datetime.datetime.strptime(date_text, station['date_format']) + time_adjust #date and time stored in local time from the start
            time_success = True
        except ValueError:
            print 'WARNING: Row without any time-value detected - not read'
            time_success = False
        if time_success:
            year = obs_time.year
            if year in years_in:
                if obs_time > max_datetime: max_datetime = obs_time
                if obs_time < min_datetime: min_datetime = obs_time
                Years.add(year)
                ignore_values = set_ignore_values(station)
                parsed_row = get_parsed_row(row, reader_list, obs_time, ignore_values)
                update_summary(parsed_row, summary)
                Weather.append(parsed_row)
    date_period = datetime.timedelta(0)
    date_period += max_datetime - min_datetime
    summary['start'] = min_datetime
    summary['end'] = max_datetime
    summary['total_hours'] = date_period.total_seconds() / 3600 #number of hours between the first and last observation
    return {"summary": summary, "data": Weather, "Years": Years}


def extract_NBDC_data(station, years_in):
    first = True
    try: year_two_digit = station['year_two_digit']
    except KeyError: year_two_digit = False #Default is 4-digit years.
    for file_name in station['file_names']:
        file_name = data_root+file_name
        try:
            f = open(file_name, 'r')
        except TypeError:
            raise Exception("Invalid file name: " + file_name)
        reader = f.readlines()
        reader_iter = iter(reader)
        header_line = reader_iter.next()
        headers = re.split('\s*', header_line.strip())
        column_numbers = dict((headers[i], i) for i in range(len(headers)))
            #dict of form {"col0_name":0, "col1_name":1, ...}
        skip = False
        for var in prime_vars:
            if var+'_column' not in station: station.update([(var+'_column','null')])
        for var in prime_vars:
            var_column = station[var + '_column']
            if var_column != "null" and var_column not in column_numbers:
                print "WARNING:", file_name, "has misnamed column.", var_column, "not in", column_numbers.keys()
                skip = True
        date_col_nums = {}
        for var in ['year_column', 'month_column', 'day_column', 'hour_column']:
            if station[var] != "null" and station[var] not in column_numbers:
                print "WARNING:", file_name, "has misnamed time-column, file not processed.", station[var], "not in", column_numbers.keys()
                skip = True
            else:
                date_col_nums.update([(var,column_numbers[station[var]])])
        if station['minute_column'] != 'null': date_col_nums.update([('minute_column',column_numbers[station['minute_column']])])
        if not skip:
            #need a better way to handle calls like column_numbers[station['wind_column']] so that it can deal with null columns
            Weather = []
            #columns = ( e.g. column_numbers[station['wind_column']]
            if first:
                (all_Weather, Years, summary, time_adjust, min_datetime, max_datetime, reader_list) = init_for_inupt(file_name, station)
                for (var,column,convert,unit) in reader_list.itervalues():
                    if column != 'null':
                        reader_list[var] = (var,column_numbers[column],convert,unit) #Might work?  Not really a hack?
                ignore_values = set_ignore_values(station)
                first = False
            if station['discard_2nd_line']: units_line = reader_iter.next() #throw away second line, it is just listing the units.
            for row_string in reader_iter:
                row_list = re.split('\s*', row_string.strip()) #Each word in the row will be an item in the list.
                row = dict((i, row_list[i]) for i in range(len(row_list)))
                year = int(row[date_col_nums['year_column']])
                if year_two_digit: year += 1900 #NDBC files up to and including 1998
                month = int(row[date_col_nums['month_column']])
                day = int(row[date_col_nums['day_column']])
                hour = int(row[date_col_nums['hour_column']])
                if station['minute_column'] != "null":
                    minute = int(row[date_col_nums['minute_column']])
                else:
                    minute = 0 #Some files don't include a column for minutes
                obs_time = datetime.datetime(year, month, day, hour, minute)
                if year in years_in:
                    if obs_time > max_datetime: max_datetime = obs_time
                    if obs_time < min_datetime: min_datetime = obs_time
                    Years.add(year)
                    parsed_row = get_parsed_row(row, reader_list, obs_time,ignore_values)
                    update_summary(parsed_row, summary)
                    Weather.append(parsed_row)
            date_period = datetime.timedelta(0)
            date_period += max_datetime - min_datetime
            summary['start'] = min_datetime
            summary['end'] = max_datetime
            summary['total_hours'] = date_period.total_seconds() / 3600 #number of hours between the first and last observation
            all_Weather += Weather
    return {"summary": summary, "data": all_Weather, "Years": Years}


def set_limits(input_string, limit_dict):
    values = input_string.rstrip('\n').split('\t')
    RGA_type = values[0]
    parameter = values[1]
    value_list = []
    for value in values[2:]:
        value_list.append(float(value))
    limit_dict[RGA_type].update([[parameter, value_list]])