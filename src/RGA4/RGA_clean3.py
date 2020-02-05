def clean_extremes(dataset, clean_settings):
    #Takes an input dataset, and uses a dictionary of extremes to clean the data.
    #If greater than maximum, values are set to maximum
    #If less than minimum, values are set to "null"
    count = 0
    row_count = 0
    clean_record = {}
    for row in dataset['data']:
        modified_row = False
        for key_to_clean, extremes in clean_settings.items():
            try:
                if row[key_to_clean] != "none" and row[key_to_clean] > extremes['maximum']:
                    if extremes['replace_max']:
                        row[key_to_clean] = extremes['maximum']
                    else: row[key_to_clean] = "none"
                    try: clean_record[key_to_clean] += 1
                    except KeyError: clean_record.update([(key_to_clean,1)])
                    count += 1
                    modified_row = True
                if row[key_to_clean] != "none" and row[key_to_clean] < extremes['minimum']:
                    row[key_to_clean] = "none"
                    try: clean_record[key_to_clean] += 1
                    except KeyError: clean_record.update([(key_to_clean,1)])
                    count += 1
                    modified_row = True
            except KeyError:
                continue #Siltently ignore bad keys
        if row['dir'] != "none" and (row['dir'] >= 360 or row['dir'] < 0):
            row['dir'] %= 360 #should take care of negative values and values over 360, but likely main thing is making 360 = 0
            try: clean_record['dir'] += 1
            except KeyError: clean_record.update([('dir',1)])
            count += 1
            modified_row = True
        if modified_row: row_count += 1
    if count > 0:
        n = len(dataset['data'])
        print "WARNING: {0} extreme values distributed over {1} data rows ({2:.2f}%) needed to be cleaned for this file.".format(count, row_count, 100.0*row_count/n)
        for key, count in clean_record.iteritems():
            print key,":",count
    return dataset

def clean_duplicates(name, dataset):
    #Sort the dataset, then look for rows where several are the same
    #If same timestamp, merge the values, preferring rows where there are more values filled in.
    #This is less careful than Uwe's approach - need to check what the costs are of that.
    print "  Cleaning duplicates in", name
    data = dataset['data']
    if len(data) > 0:
        data = sorted(data, key=lambda k: k['datetime'])
        cleaned_data = []
        data_iter = iter(data)
        try:
            this_row = data_iter.next()
        except:
            print "***ERROR*** Something went wrong: ", dataset
        identical_rows = [this_row]
        resolve_count = 0

        def resolve(identical_rows):
            all_keys = identical_rows[0].keys()
            max_good = 0
            for row in identical_rows:
                good_values = 0
                for key, value in row.items():
                    if value == 'none':
                        row.pop(key, None)
                    else:
                        good_values += 1
                row.update([('good', good_values)])
                if good_values > max_good: max_good = good_values #Record the number of good values in the "best" data row
            identical_rows = sorted(identical_rows, key=lambda k: k['good'])
            out_row = {}
            for key in all_keys:
                value = 'none'
                for row in identical_rows:
                    if key in row: value = row[key] #over-writes if there's more than one row with this value filled.  Rows with more values overwrite those with fewer.
                out_row.update([(key, value)])
            return out_row

        for next_row in data_iter:
            if next_row['datetime'] == this_row['datetime']:
                identical_rows.append(next_row)
            else:
                if len(identical_rows) > 1:
                    resolve_count += 1
                    this_row = resolve(identical_rows)
                cleaned_data.append(this_row)
                identical_rows = [next_row]
            this_row = next_row
        cleaned_data.append(this_row)
        dataset['data'] = cleaned_data
        if resolve_count > 0: print "WARNING: Found " + str(
            resolve_count) + " cases where two or more rows had identical timestamps.  Only 'best' data kept."
        return dataset
    else:
        print "WARNING: An empty dataset was passed to clean - probably the date range didn't include the dataset. {0}".format(name)
        return dataset

def fill_undefined_waves(dataset, name):
    data = dataset['data']
    empirical_count = 0
    if len(data) > 0:
        for row in data:
            if row['wave'] == 'none' and row['ice'] != 'none':
                if row['ice'] > 0.01:
                    row['wave'] = 0.0
                    row['period'] = 1.0
                elif row['wind'] != 'none':
                    row['wave'] = 0.0212 * row['wind']*row['wind']
                    empirical_count += 1
    if empirical_count > 0: print "WARNING: Used empirical equation for wave height {0} times in {1}".format(empirical_count,name)