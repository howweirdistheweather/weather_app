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

import csv
import time
import math
import random as rand
import collections
import copy
from hig_utils import pretty_duration

default_keys = [] #functionality not used, but not removed

def order_list(original_list, ordered_items):
    try:
        new_list = ordered_items
        for key in original_list:
            if key not in new_list:
                new_list.append(key)
        new_list = [x for x in new_list if x in original_list]
    except AttributeError:
        print("WARNING: bad data sent to order_list:")
        print("original list:", original_list)
        print("ordered items:", ordered_items)
        print("new list:", new_list)
    return new_list

def write_csv_from_list_of_dicts(file_name, data, keys=False, strict_keys=False, options='wb'):
    start_time = time.time()
    if len(data) > 0:
        print("  Writing data: " + file_name, end=' ')
        if strict_keys: print_keys = keys
        else:
            key_set = set([])
            for row in data:
                key_set.update(list(row.keys()))
            key_set = sorted(list(key_set))
            if keys:
                print_keys = order_list(keys, default_keys)
                print_keys = order_list(key_set, print_keys)
            else:
                print_keys = order_list(key_set, default_keys)
        with open(file_name, options) as out_file:
            dw = csv.DictWriter(out_file, dialect=csv.excel, fieldnames=print_keys)
            dw.writeheader()
            for row in data:
                dw.writerow(row)
        print('({})'.format(pretty_duration(time.time()-start_time)))
    else:
        print("\nWARNING:  No data in list, " + file_name + " not written")

def write_csv_from_dict_of_lists(file_name, data, options='w'):
    start_time = time.time()
    print(f"  Writing data: {file_name}", end=' ')
    length_mismatch = False
    for key,list in data.items():
        try: 
            if len(list) != len_0: length_mismatch = True
        except NameError:
            len_0 = len(list)
    if length_mismatch: print("ERROR: Writing failed - all lists must be the same length.")
    else:
        out_dict = []
        for key,list in data.items():
            for i,value in enumerate(list):
                try: out_dict[i].update([(key,value)])
                except IndexError: out_dict.append({key:value})
        with open(file_name, options) as out_file:
            dw = csv.DictWriter(out_file, dialect=csv.excel, fieldnames=data.keys())
            dw.writeheader()
            for row in out_dict:
                dw.writerow(row)
        print(pretty_duration(time.time()-start_time))
    

def write_csv_from_list_of_dicts_simple(file_name, data, keys=False, options='w', exclude_keys = []):
    start_time = time.time()
    if len(data) > 0:
        print("  Writing data: " + file_name, end=' ')
        remove_fields = False
        if not keys:
            keys = list(data[0].keys())
            for row in data:
                for key,value in row.items():
                    if key not in keys: keys.append(key)
            for key in exclude_keys:
                if key in keys:
                    keys.remove(key)
                    remove_fields = True
        with open(file_name, options) as out_file:
            dw = csv.DictWriter(out_file, dialect=csv.excel, fieldnames=keys)
            dw.writeheader()
            if remove_fields:
                for row in data:
                    new_row = collections.OrderedDict([(key,value) for key,value in row.items()])
                    for key in list(new_row.keys()):
                        if key not in keys:
                            del new_row[key]
                    dw.writerow(new_row)
            else:
                for row in data:
                    dw.writerow(row)
        print('({})'.format(pretty_duration(time.time()-start_time)))
    else:
        print("\nWARNING:  No data in list, " + file_name + " not written")

def add_data_to_csv(file_name,data):
    try:
        f = open(file_name, 'rU')
        exists = True
    except (TypeError, IOError):
        exists = False
    if exists:
        reworked_data = []
        old_data = csv.DictReader(f)
        keys = list(data[0].keys())

        for row in old_data:
            reworked_data.append(row)
            for key,value in row.items():
                if key not in keys: keys.append(key)
        for row in data:
            new_row = collections.OrderedDict([])
            for key in keys:
                try: new_row.update([(key,row[key])])
                except KeyError: new_row.update([(key,None)])
            for key,value in row.items():
                if key not in keys:
                    keys.append(key)
                    for old_row in reworked_data:
                        old_row.update([(key,None)])
                    new_row.update([(key,value)])
            reworked_data.append(new_row)
        write_csv_from_list_of_dicts_simple(file_name,reworked_data,keys)
    else: write_csv_from_list_of_dicts_simple(file_name,data)

def update_last_csv_row(file_name,new_data):
    f = open(file_name, 'rU')
    old_data = csv.DictReader(f)
    keys = old_data.fieldnames
    reworked_data = []
    for row in old_data:
        reworked_data.append(row)
        last_row = row
    for key,value in new_data.items():
        if key not in keys:
            keys.append(key)
            for old_row in reworked_data:
                old_row.update([(key,None)])
        last_row.update([(key,value)])
    write_csv_from_list_of_dicts_simple(file_name,reworked_data,keys)


def subset_list(data, column, compare_value, operator, verbose = False):
    start_time = time.time()
    subset = []
    n = 0
    for row in data:
        try: value = row[column]
        except KeyError:
            print(row)
            print(column)
            raise Exception
        if operator == "=":
            if value == compare_value:
                subset.append(row)
                n += 1
        elif operator == "!=":
            if value != compare_value:
                subset.append(row)
                n += 1
        else:
            value = float(value)
            if operator == ">":
                if value > compare_value:
                    subset.append(row)
                    n += 1
            elif operator == "<":
                if value < compare_value:
                    subset.append(row)
                    n += 1
            elif operator == ">=":
                if value >= compare_value:
                    subset.append(row)
                    n += 1
            elif operator == "<=":
                if value <= compare_value:
                    subset.append(row)
                    n += 1
            else:
                print("ERROR: operator {0} unknown.".format(operator))
                return subset
    if verbose:
        print("  Subset created with {0} data rows where {1} {2} {3} in {4:.3f} seconds".format(n, column, operator, compare_value, time.time()-start_time))
    return subset

def subset_dict(data, column, compare_value, operator, verbose = False):
    start_time = time.time()
    subset = {}
    n = 0
    for key,row in data.items():
        try: value = row[column]
        except KeyError:
            print(row)
            print(column)
            raise Exception
        if operator == "=":
            if value == compare_value:
                subset.update([(key,row)])
                n += 1
        elif operator == "!=":
            if value != compare_value:
                subset.update([(key,row)])
                n += 1
        else:
            value = float(value)
            if operator == ">":
                if value > compare_value:
                    subset.update([(key,row)])
                    n += 1
            elif operator == "<":
                if value < compare_value:
                    subset.update([(key,row)])
                    n += 1
            elif operator == ">=":
                if value >= compare_value:
                    subset.update([(key,row)])
                    n += 1
            elif operator == "<=":
                if value <= compare_value:
                    subset.update([(key,row)])
                    n += 1
            else:
                print("ERROR: operator {0} unknown.".format(operator))
                return subset
    if verbose:
        print("  Subset created with {0} data rows where {1} {2} {3} in {4:.3f} seconds".format(n, column, operator, compare_value, time.time()-start_time))
    return subset


def partition_dict_on_column(data, column):
    values = set([])
    for key,row in data.items():
        values.add(row[column])
    values = sorted(list(values))
    partitioned_data = {}
    for value in values:
        partitioned_data.update([ (value,subset_dict(data,column,value,"=")) ])
    return partitioned_data

def random_subset(filename, rand_P):
    start_time = time.time()
    try:
        f = open(filename, 'rU')
    except TypeError:
        raise Exception("Invalid file name: " + filename)
    csv_file = csv.DictReader(f)
    keys = {'row_id'}
    subset_rows = []
    rand_per = int(math.ceil(1.0/rand_P))
    for i,row in enumerate(csv_file):
        if rand.randint(1,rand_per) == 1:
            row.update([('row_id',i)])
            subset_rows.append(row)
            for key in row:
                keys.add(key)
    outfile = filename + '_subset.csv'
    with open(outfile, 'wb') as out_file:
        dw = csv.DictWriter(out_file,fieldnames=keys, dialect=csv.excel)
        dw.writeheader()
        for row in subset_rows:
            dw.writerow(row)
    f.close()
    print('Generated random subset for {0} with {1} of original source rows in {2:.0f} seconds:'.format(filename, rand_P, time.time() - start_time), end=' ')

def truncated_subset(filename, n):
    start_time = time.time()
    try:
        f = open(filename, 'rU')
    except TypeError:
        raise Exception("Invalid file name: " + filename)
    csv_file = csv.DictReader(f)
    keys = {'row_id'}
    subset_rows = []
    for i,row in enumerate(csv_file):
        if i < n:
            row.update([('row_id',i)])
            subset_rows.append(row)
            for key in row:
                keys.add(key)
    outfile = filename + '_truncated.csv'
    with open(outfile, 'wb') as out_file:
        dw = csv.DictWriter(out_file,fieldnames=keys, dialect=csv.excel)
        dw.writeheader()
        for row in subset_rows:
            dw.writerow(row)
    f.close()
    print('Generated subset for {0} with {1} of original source rows in {2:.0f} seconds:'.format(filename, i, time.time() - start_time), end=' ')