# -*- coding: utf-8 -*-
from math import *
import sys

#Potential issues:
#Old horizontal visibility was in km, not m

#All these should be lower case
m_names = ['m', 'meters']
km_names = ['km', 'kilometers']
mi_names = ['mi', 'miles']
NMi_names = ['nmi', 'nautical miles']
ft_names = ['ft', 'feet']
in_names = ['in','inch','inches']
ms_names = ['m/s', 'meters per second']
mph_names = ['mph', 'miles per hour']
knots_names = ['knots', 'knot', 'nautical miles per hour', 'kts']
kph_names = ['kph', 'kilometers per hour', 'km/hr']
s_names = ['s', 'seconds', 'second']
min_names = ['min', 'minute', 'minutes']
hour_names = ['hr', 'hrs', 'hour', 'hours']
day_names = ['day','days']
year_names = ['year','yr','years']
c_names = ['c', 'celsius', '°c']
f_names = ['f', 'fahrenheit', '°f']
k_names = ['k', 'kelvin', '°k']
prop_names = ['proportion','p','prop']
percent_names = ['%','percent']
m3_names = ['m^3', 'm3', 'cubic meters', 'cubic meter']
l_names = ['l','liter','liters']
oil_bbl_names = ['bbl','barrels','bbls','barrels']
gal_names = ['gallons', 'gallon', 'gal']
m3_per_second_names = ['m^3/s', 'm^3 / s', 'm3ps', 'cubic meters per second']
liters_per_second_names = ['l/s','liters per second']
gallons_per_minute_names = ['gal/min', 'gallons per minute', 'gpm']
oil_barrels_per_hours_names = ['bbls/hr', 'bbl/hr', 'barrels per hour', 'bph']
degree_names = ['degrees', '°', 'deg']
radian_names = ['radians']

zero = [0,0.0,'0','zero','ZERO','Zero','0.0']

bad_chars = ' ,(){}[]\t\n' #To be stripped


def smart_units(input_string, verbose = False):
    try: return float(input_string) #If it's just a number, trust that it is what it's supposed to be.
    except ValueError: pass
    input_string = input_string.strip(bad_chars)
    if not verbose and input_string in zero: return 0.0
    elif input_string == 'infinite': return sys.float_info.max #maximum float value
    else:
        try: value, units = tuple(input_string.split(' ', 1))
        except ValueError: raise NameError('Not a usable string for verbose smart_units - must include units:',input_string)
        units = units.strip(bad_chars)
        units = units.lower()
        if verbose:
            if units in m_names + ft_names + km_names + NMi_names + mi_names + in_names: return length_m(value, units), 'length', "meters"
            elif units in ms_names + mph_names + knots_names + kph_names: return velocity_m_s(value, units), "velocity", "meters per second"
            elif units in s_names + min_names + hour_names + day_names + year_names: return time_s(value, units), "time", "seconds"
            elif units in m3_names + l_names + oil_bbl_names + gal_names: return volume_m3(value, units), "volume", "cubic meters"
            elif units in c_names + f_names + k_names: return temperature(value, units), "temperature", "Celsius"
            elif units in m3_per_second_names + liters_per_second_names + gallons_per_minute_names + oil_barrels_per_hours_names: return discharge_m3_s(value, units), "discharge", "m^3/s"
            elif units in prop_names + percent_names: return proportion(value, units), "proportion", "non-dimensional"
            elif units in degree_names + radian_names: return angle_rad(value, units), "angle", "radians"
            else: raise NameError('Unknown text string for smart_units: {0}\nNote that there has to be a space between the number and the unit, like "5 °F" not "5°F".'.format(input_string))
        else:
            if units in m_names + ft_names + km_names + NMi_names + mi_names + in_names: return length_m(value, units)
            elif units in ms_names + mph_names + knots_names + kph_names: return velocity_m_s(value, units)
            elif units in s_names + min_names + hour_names + day_names + year_names: return time_s(value, units)
            elif units in m3_names + l_names + oil_bbl_names + gal_names: return volume_m3(value, units)
            elif units in c_names + f_names + k_names: return temperature(value, units)
            elif units in m3_per_second_names + liters_per_second_names + gallons_per_minute_names + oil_barrels_per_hours_names: return discharge_m3_s(value, units)
            elif units in prop_names + percent_names: return proportion(value, units)
            elif units in degree_names + radian_names: return angle_rad(value, units)
            else:
                raise NameError('Unknown text string for smart_units: "{0}"\nNote that there has to be a space between the number and the unit, like "5 °F" not "5°F".'.format(input_string, ))

def length_m(value, units=None):
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in m_names: return value
    elif units.lower() in in_names: return value * 0.0254
    elif units.lower() in ft_names: return value * 0.3048
    elif units.lower() in km_names: return value * 1000
    elif units.lower() in mi_names: return value * 1609.34
    elif units.lower() in NMi_names: return value * 1852
    else: raise NameError('Unknown length units '+units)

def velocity_m_s(value, units=None):
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in ms_names: return value
    elif units.lower() in mph_names : return value * 0.44704
    elif units.lower() in knots_names: return value * 0.514444444
    elif units.lower() in kph_names: return value * 0.277778
    else: raise NameError('Unknown velocity units '+units)

def time_s(value, units=None): #returns a value in seconds
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in s_names: return value
    elif units.lower() in min_names: return 60.0 * value
    elif units.lower() in hour_names: return 3600.0 * value
    elif units.lower() in day_names: return 86400.0 * value
    elif units.lower() in year_names: return 366.0*86400*value #assumes a leap-year, so this is maximum year-length rather than true year length
    else: raise NameError('Unknown period units: '+units)

def volume_m3(value, units=None):
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in m3_names: return value
    elif units.lower() in l_names: return value / 1000
    elif units.lower() in oil_bbl_names: return value * .158987
    elif units.lower() in gal_names: return value * .00378541
    else: raise NameError('Unknown volume units: '+units)

def discharge_m3_s(value, units=None):
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in m3_per_second_names: return value
    elif units.lower() in liters_per_second_names: return value / 1000
    elif units.lower() in gallons_per_minute_names: return value * 0.0000630902
    elif units.lower() in oil_barrels_per_hours_names: return value * 0.0000441631
    else: raise NameError('Unknown discharge units: '+units)


def temperature(value, units=None): #retunrs a value in celsius
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        value = float(value)
    if units.lower() in c_names: return value
    elif units.lower() in f_names: return (value - 32) / 1.8
    elif units.lower() in k_names: return value - 273.15
    else: raise NameError('Unknown temperature units: '+units)

def proportion(value, units=None): #returns a non-dimensional value from zero to one
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in prop_names: return value
    elif units.lower() in percent_names: return value/100
    else: raise NameError('Unknown proportion units: '+units)

def angle_rad(value, units=None):
    units.strip(bad_chars)
    try: value = float(value)
    except TypeError:
        value.strip(bad_chars)
        if value == 'infinite': return sys.float_info.max #maximum float value
        elif value in zero: return 0.0
        value = float(value)
    if units.lower() in degree_names: return radians(value)
    elif units.lower() in radian_names: return value
    else: raise NameError('Unknown angle units: '+units)


################DEPRECATED?##############

def wave_height(value, units=None):
    if value == 'infinite': return 10000.0 #10,000 m is effectively infinite
    elif value in zero: return 0.0
    value = float(value)
    if units.lower() in m_names: return value
    elif units.lower() in ft_names: return value * 0.3048
    else: raise NameError('Unknown wave height units '+units)

def velocity(value, units=None):
    if value == 'infinite': return 10000.0 #10,000 m/s is effectively infinite
    elif value in zero: return 0.0
    value = float(value)
    if units.lower() in ms_names: return value
    elif units.lower() in mph_names : return value * 0.44704
    elif units.lower() in knots_names: return value * 0.514444444
    elif units.lower() in kph_names: return value * 0.277778
    else: raise NameError('Unknown velocity units '+units)

def period(value, units=None): #returns a value in seconds
    if value == 'infinite': return 10000.0 #10,000 s is effectively infinite
    elif value in zero: return 0.0
    value = float(value)
    if units.lower() in s_names: return value
    elif units.lower() in min_names: return 60.0 * value
    elif units.lower() in hour_names: return 3600.0 * value
    else: raise NameError('Unknown period units: '+units)


def interpret_categorical_ice_cover(ct_cat):
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
    return ct_interpretation[ct_cat]

def icecover(value, units = None): #returns proportion
    if value in zero: return 0.0
    if units.lower in categorical_ice_names: return interpret_categorical_ice_cover(value)
    value = float(value)
    if units.lower in prop_names or not units: return value #assume no units implies proportion
    elif units.lower in percent_names: return value/100
    else: raise NameError('Unknown icecover units: '+units)



convert_dict = {
    "vis":length_m,
    "ceil":length_m,
    "wave":length_m,
    "wind":velocity_m_s,
    "gust":velocity_m_s,
    "period":time_s,
    "temp":temperature,
    "wtemp":temperature
}
