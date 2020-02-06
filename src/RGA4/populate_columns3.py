#Functions that populate derived columns

import time
import math

def blank_is_zero(dataset, column):
    count = 0
    for row in dataset['data']:
        if row[column] == 'none':
            row[column] = 0.0
            count += 1
    print "  Assuming blank valuse for {0} are actually zero: {1} values populated".format(column, count)

def populate_gusts(dataset):
    print "  Populating blank gusts for " + dataset['name']
    for row in dataset['data']:
        if row['wind'] != 'none' and row['gust'] == 'none':
            row['gust'] = row['wind']

def populate_ceiling(dataset,ceil_max):
    print "  Populating blank ceilings for " + dataset['name']
    suspect_count = 0
    for row in dataset['data']:
        if row['cover'] != 'none' and row['ceil'] == 'none':
            if row['cover'] < 0.625: row['ceil'] = ceil_max
            else:
                row['ceil'] = "none" #Default value for suspect rows
                suspect_count += 1
    if suspect_count > 0: print "WARNING:",suspect_count,"cases where cloud cover is >0.625 but no ceiling is listed."

def populate_steepness(dataset):
    print "  Adding steepness for",dataset['name']
    for row in dataset['data']:
        period = row['period']
        if period != "none" and row['wave'] != "none" and period > 0:
            row['steep'] = row['wave'] / (9.81 * period * period)
        else: row['steep'] = 'none' #this shouldn't be necessary


def populate_wind_chill_english(dataset):
    start_time = time.time()

    def CtoF(C):
        return C * 1.8 + 32

    def FtoC(F):
        return (F-32) / 1.8

    def mPStoMPH(mPS): #convert m/s to mph
        return mPS * 2.23694

    #Old Source:  http://www.crh.noaa.gov/ddc/?n=windchill
    #New Source:  http://www.srh.noaa.gov/images/epz/wxcalc/windChill.pdf (Haven't checked to make sure they're the same.)
    #T(wc) = 35.74 + 0.6215T - 35.75(V^0.16) + 0.4275T(V^0.16) (in F)
    print "  Adding wind chill for",dataset['name'],
    for row in dataset['data']:
        if row['temp'] != 'none' and row['wind'] != 'none':
            wind_mph = mPStoMPH(row['wind'])
            temp_F = CtoF(row['temp'])
            wind_chill_F = 35.74 + 0.6215*temp_F - 35.75*math.pow(wind_mph,0.16) + 0.4275*temp_F*math.pow(wind_mph,0.16)
            wind_chill_C = FtoC(wind_chill_F)
            if wind_chill_C < row['temp']: row['wind_chill'] = wind_chill_C #Otherwise not in domain of wind chill calculation - too light of wind
        else: row['icing_cat'] = 'none'
    print "took","{0:.3f}".format(time.time()-start_time),"seconds"


def populate_wind_chill_metric(dataset):
    #T(wc) = 13.12 + 0.6215 * T - 11.37 * (V*3.6)^0.16 + 0.3965 * T * (V*3.6)^0.16 (V in m/s, T in C)
    start_time = time.time()
    print "  Adding wind chill for",dataset['name'],
    for row in dataset['data']:
        if row['temp'] != 'none' and row['wind'] != 'none':
            V = row['wind']
            T = row['temp']
            wind_chill = 13.12 + 0.6215 * T - 11.37 * math.pow((V*3.6),0.16) + 0.3965 * T * math.pow((V*3.6),0.16)
            if wind_chill < row['temp']: row['wind_chill'] = wind_chill #Otherwise not in domain of wind chill calculation - too light of wind
            else: row['wind_chill'] = row['temp']
        else: row['wind_chill'] = 'none'
    print "took","{0:.3f}".format(time.time()-start_time),"seconds"


def populate_vessel_icing(dataset):
    #Source: http://www.met.nps.edu/~psguest/polarmet/vessel/predict.html
    #Original paper: Overland 1990
    start_time = time.time()

    def model_wtemp(temp):
        return 2.0 #Assume water is 2 C

    def calculate_vessel_icing(wind,temp,wtemp):
        water_freeze = -1.7 #Temperature at which saltwater freezes
        if wtemp == "none": wtemp = model_wtemp(temp)
        ppr = wind*(water_freeze - temp)/(1 + 0.3*(wtemp - water_freeze)) #h14 = (ws*(Tf-Ta))/(1.+0.3*(Ts-Tf))
        thresholds = {"no_icing":0.0, "light":22.4,"moderate":53.3, "heavy":83.0}
        if ppr < thresholds['no_icing']: category = "no_icing"
        elif ppr < thresholds['light']: category = "light"
        elif ppr < thresholds['moderate']: category = "moderate"
        elif ppr < thresholds['heavy']: category = "heavy"
        else: category = "extreme"
        return (ppr,category)


    print "  Adding vessel icing for",dataset['name'], "using NPS forumla",
    for row in dataset['data']:
        if row['temp'] != 'none' and row['wind'] != 'none':
            (ppr,category) = calculate_vessel_icing(row['wind'],row['temp'], row['wtemp'])
            row['icing_cat'] = category
        else: row['icing_cat'] = 'none'
    print "took",'{0:.1f}'.format(time.time() - start_time),"seconds"


def populate_shear(dataset):
    print "  Adding shear for",dataset['name']
    neg_shear_count = 0
    for row in dataset['data']:
        if row['wind'] != 'none' and row['gust'] != 'none':
            shear = row['gust'] - row['wind']
            if shear < 0:
                neg_shear_count += 1
                shear = 'none'
                row['gust'] = 'none'
            row['shear'] = shear
        else: row['shear'] = 'none'
    if neg_shear_count > 0: print "WARNING, {0} negative shear values and low gust values discarded".format(neg_shear_count)


def interpolate_var_wrapper(dataset, var):
    interpolate_var(dataset['data'],var,dataset['name'])
    

def interpolate_var(data, var, name):
    start_time = time.time()

    def linear_interpolate(list, var, A, B):
        A_y = list[A][var]
        B_y = list[B][var]
        A_x_time = list[A]['datetime']
        B_x = (list[B]['datetime'] - A_x_time).total_seconds()
        slope = (B_y-A_y)/B_x
        for X in range(A+1,B):
            x = (list[X]['datetime']-A_x_time).total_seconds()
            list[X][var] = A_y + slope * x #linear interpolation equation

    data_iter = iter(data)
    previous = data_iter.next()
    prev_pointer = 0
    go = True
    while previous[var] == 'none' and go:
        try:
            previous = data_iter.next() #get the first instance where there is a value in the var column
            prev_pointer += 1
        except StopIteration:
            print "WARNING: No {0} data in {1} - not possible to interpolate.".format(var,name)
            go = False
    if go:
        pointer = prev_pointer
        for row in data_iter:
            pointer += 1
            try:
                if row[var] != 'none':
                    linear_interpolate(data,var, prev_pointer,pointer)
                    prev_pointer = pointer
            except TypeError:
                print name, pointer,row,data[pointer]
        print "  Interpolating {0} for {1} took {2:.3f} seconds".format(var, name, time.time() - start_time)


def normalize_interpolate_ice(dataset):
    print "  Normalizing and interpolating ice for", dataset['name']
    ct_interpretation = { #All the CT codes that actually occur, with their interpretation in terms of proportion ice cover (ie 0.2 = 20%)
        0:0.0,
        1:0.05,
        13:0.2,
        20:0.2,
        30:0.3,
        35:0.4,
        40:0.4,
        46:0.5,
        50:0.5,
        57:0.6,
        60:0.6,
        70:0.7,
        79:0.8,
        80:0.8,
        81:0.9,
        90:0.9,
        91:0.95,
        92:1.0
    }
    for row in dataset['data']:
        ct = row['ice']
        if ct != 'none':
            row['ice'] = ct_interpretation[ct]
    interpolate_var_wrapper(dataset, 'ice')

