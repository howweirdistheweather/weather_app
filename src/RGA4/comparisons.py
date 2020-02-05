__author__ = 'bretwoodhigman'
import copy
from column_lists3 import gap_vars



def safe_count(key,dict):
    try: dict[key] += 1
    except KeyError: dict.update([(key,1)])

def safe_add(key, value, dict):
    try: dict[key] += value
    except KeyError: dict.update([(key,value)])

def best_of_cycle(name, RGA_list, days_per_bin=None, div_bins=[]):
    #Two alternatives, either regularly spaced bins, or div_bins with specific start dates.
    #EXAMPLE: If div_bins = [0,20,100], three bins are generated, one from day 0 to day 19, one from day 20 to day 99, and one from day 100 to the end of the year.
    #If days_per_bin is non-zero, it's used and div_bins is ignored.  If both are empty, an error is returned.
    if not days_per_bin:
        if len(div_bins) > 0:
            print "  Calculating cycle data for " + name + " with " + str(div_bins) + " specifically assigned bins"
        else: raise Exception('ERROR: No specifications for bins for best_of_cycle')
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
            raise LookupError("get_index in cycle_data failed: {0} day, {1}, {2}".format(day,[(x['start'],x['end']) for x in bins], div_bins))

        current = min([RGA['data'][0]['datetime'] for RGA in RGA_list]) #Assumes hours in data are already sorted ascending
        RGA_iterators = [iter(RGA['data']) for RGA in RGA_list]
        RGA_items = []
        for RGA_hour in RGA_iterators: RGA_items.append(RGA_hour.next())
        theres_more = True
        best_order = ['Incomplete','Red','Yellow','Green']
        best_order_detailed = ['Ambiguous'] \
                     + ['Red{0}'.format(i) for i in range(1,50)] \
                     + ['Yellow{0}'.format(i) for i in range(1,50)] \
                     + ['Green{0}'.format(i) for i in range(1,50)]
        while theres_more is True:
            theres_more = False
            best_index_detailed = 0
            best_index = 0
            complete = False
            this_day = current.timetuple().tm_yday
            this_year = current.timetuple().tm_year
            index = get_index(this_day) #Figure out what bin the particular observation lies in
            for i,RGA_hour in enumerate(RGA_items):
                if RGA_hour['datetime'] <= current:
                    if RGA_hour['complete']:
                        complete = True
                    new_index = best_order_detailed.index(RGA_hour['detailed_conditions'])
                    if new_index > best_index_detailed:
                        best_index_detailed = new_index
                    new_index = best_order.index(RGA_hour['conditions'])
                    if new_index > best_index:
                        best_index = new_index
                    try:
                        RGA_items[i]=RGA_iterators[i].next()
                        theres_more = True
                    except StopIteration: pass
            safe_count(best_order[best_index],bins[index])
            safe_count(best_order_detailed[best_index_detailed],bins[index])
            safe_count('total_hours',bins[index])
            safe_count('total_hours_{0}'.format(this_year),bins[index])
            if complete:
                safe_count('complete',bins[index])
                safe_count('{0}_complete'.format(best_order[best_index]),bins[index])
                safe_count('{0}_{1}_complete'.format(this_year,best_order[best_index]),bins[index])
            #Not implementing gap_vars part of cycles at this time.
            current = min([RGA_hour['datetime'] for RGA_hour in RGA_items])
        return {'name':'{0}_best_of'.format(name), 'Years': Years, 'bins': bins, 'bin_def':div_bins}
    else:
        print "WARNING: No data for cycle, empty structure returned"
        return {'name':'{0}_best_of'.format(name), 'Years': Years, 'bins': [], 'bin_def':div_bins}
