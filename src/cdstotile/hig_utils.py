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

from os import (
    walk,
    makedirs
)
from os.path import (
    join,
    exists
)
import re
import collections
import datetime
import math

def check_dirs(dir_list):
    for d in dir_list:
        if not exists(d):
            print(('  Creating directory: ' + d))
            makedirs(d)

def filename_no_suffix(input_file_string):
    dir_list = input_file_string.split('/')
    if len(dir_list[-1]) > 0: filename = dir_list[-1]
    else: filename = dir_list[-2]
    pieces = filename.split('.')
    return pieces[0]

def get_filename_list(root_path, suffix = None, test_string = None):
    files_raw = []
    file_paths_raw = []
    for (dirpath, dirnames, filenames) in walk(root_path):
        files_raw.extend(filenames)
        file_paths_raw.extend(join(dirpath, filename) for filename in filenames)
    if suffix:
        re_suffix = re.compile('.*\.{0}'.format(suffix))
        subset_files = []
        for name in file_paths_raw:
            if re.match(re_suffix,name):
                subset_files.append(name)
    else: subset_files = files_raw
    if test_string:
        re_test = re.compile('.*{0}.*'.format(test_string))
        smaller_subset = []
        for name in subset_files:
            if re.match(re_test,name):
                smaller_subset.append(name)
    else: smaller_subset = subset_files
    print(smaller_subset)
    return smaller_subset

def constrain(value,mini,maxi):
    if value < mini: return mini
    elif value > maxi: return maxi
    else: return value

def approximately(value1, value2, tolerance):
    min = float(value1) * (tolerance-1)
    max = float(value1) * (tolerance+1)
    if value2 > min and value2 < max: return True
    else: return False

def safe_float(value):
    try: return float(value)
    except (ValueError, TypeError): return 0.0

def safe_strip(value):
    try: return value.strip()
    except: return value

def sort_layered_dict_by_key(dict_to_sort, forced_orders = {}, depth = 0, inner_key=None): #recursive
    if isinstance(dict_to_sort, dict):
        if depth in forced_orders:
            ordered_dict = collections.OrderedDict([])
            for category in forced_orders[depth]:
                try:
                    ordered_dict.update([(category,dict_to_sort[category])])
                    #print '.',
                except KeyError:
                    pass #Nothing in that category, so leave it out.
                    #print ',',
            #print dict_to_sort.keys()
            dict_to_sort = ordered_dict
            #print  "AFTER", dict_to_sort.keys()
        else: dict_to_sort = collections.OrderedDict(sorted(iter(dict_to_sort.items()), key=lambda x: x[0])) #Alphabetize things without forced orders.
    else: return None #It's not a dictionary, so you must be at the innermost layer.
    for key,layer in dict_to_sort.items():
        sorted_layer = sort_layered_dict_by_key(layer, forced_orders, depth+1)
        if sorted_layer: dict_to_sort[key] = sorted_layer
        elif inner_key: dict_to_sort[key] = sorted(layer, key = lambda x: x[inner_key])#Innermost loop.
        else: dict_to_sort[key] = layer

    #print depth, dict_to_sort.keys()
    return dict_to_sort

def invert_dict(input_dict):
    output_dict = {}
    for key,value in input_dict.items():
        output_dict.update([(value,key)])
    return output_dict

def Mean(X):
    n = len(X)
    if n > 0: return float(sum(X))/n
    else: return None

def m_per_s_to_knots(mps):
    if mps: return float(mps)/0.514444
    else: return None

def datestring_Nuka(precision='Day', date_time_object= datetime.datetime.now()):
    if precision in ['Day','Days','day','days']:
        return date_time_object.strftime('%y%m%d')
    elif precision in ['Minute','Minutes','minute','minutes']:
        return date_time_object.strftime('%y%m%d-%H%M')
    elif precision in ['Second','Seconds','second','seconds']:
        return date_time_object.strftime('%y%m%d-%H%M%S')

def filesafe_string(input_string):
    input_string = str(input_string)
    try:
        valid_chars = '.-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join([c for c in input_string if c in valid_chars])
    except: return ''

def safe_string(input_string):
    input_string = str(input_string)
    try:
        input_string = str(input_string)
        valid_chars = '.-_()&/:;!#$%^*+=[]~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' #Doesn't have \`<>@{}
        return ''.join([c for c in input_string if c in valid_chars])
    except: return ''

def pretty_duration(seconds):
    if seconds < 1: return "{0:.0f} milliseconds".format(seconds*1000)
    elif seconds < 10: return "{0:.2f} seconds".format(seconds)
    elif seconds < 20: return "{0:.1f} seconds".format(seconds)
    elif seconds < 100: return "{0:.0f} seconds".format(seconds)
    elif seconds < 60 * 20: return "{0:.0f} minutes, {1:.0f} seconds".format(seconds/60,seconds%60)
    elif seconds < 60 * 60: return "{0:.0f} minutes".format(seconds/60)
    elif seconds < 3600 * 24: return "{0:.0f} hours, {1:.0f} minutes".format(math.floor(seconds/3600),math.floor((seconds%3600)/60))
    elif seconds < 3600 * 24 * 10: return "{0:.0f} days, {1:.0f} hours".format(math.floor(seconds/(3600*24)), math.floor(seconds%(3600*24)/3600))  #math.floor((seconds-math.floor(seconds/(3600*24)))/3600%24))
    elif seconds < 3600 * 24 * 100: return "{0:.0f} days".format(seconds/3600/24)
    elif seconds < 3600 * 24 * 500: return "{0:.2f} years".format(seconds/3600/24/365.256363004) #In Siberian years
    else: return "{0:.1f} years".format(seconds/3600/24/365.256363004) #In Siberian years

def pretty_number(value):
    pass