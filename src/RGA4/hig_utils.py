import os
import random as rand

def safe_count(index, dict): #Incrementally count, but if there's no counter set up, start it with a value of 1
    try: dict[index] += 1
    except KeyError: dict.update([ (index,1) ])

def safe_get_float(index, dict):
    try: return float(dict[index])
    except KeyError: return 0.0

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.exists(d):
            print('  Creating directory: ' + d)
            os.makedirs(d)

def merge_rows(prev_row, new_row, prev_count = 1, omit_rows = []):
    all_keys = set(prev_row.keys() + new_row.keys()) - omit_rows
    merged_row = {}
    for key in all_keys:
        if key in prev_row and prev_row[key] != 'none':
            if key in new_row and new_row[key] != 'none':
                try: value = (prev_row[key] * prev_count + new_row[key]) / (prev_count + 1) #It may be that this row has already been merged with other rows - allow for that case.
                except ValueError: value = rand.choice([prev_row[key],new_row[key]]) #Choose randomly amongst random values - biased toward later rows if more than 2.
                except TypeError as error_text:
                    print error_text
                    print "Something wrong? Comparing {1} to {2}".format(prev_row,new_row)
                    print "Specific values: {1} and {2}".format(prev_row[key],new_row[key])
                    raise Exception
            elif key in prev_row: value = prev_row[key]
            else: value = 'none'
        elif key in new_row: value = new_row[key]
        else: value = 'none'
        merged_row.update([(key,value)])
    return merged_row

