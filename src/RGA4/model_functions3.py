#Each function here returns three items:
#The RG number, typically 0 for green, 1 for yellow, and 2 for red.
#A boolean, True for complete data, False for incomplete data
#A boolean, True unless the entire data row should be exclude.  Right now only used for exclude_night

import copy
from column_lists3 import gap_values
from convert_functions3 import smart_units

def init_model_dict(raw_model_dict):
    md = {}
    for model_key, model in raw_model_dict.iteritems():
        md.update([(model_key, {})])
        for comp_key, comp in model.iteritems():
            try:
                md[model_key].update([(comp_key, {
                'obs': comp['obs'],
                'logic': comp['logic'](*comp['params'])
                })])
            except TypeError as error_text:
                print comp
                print error_text
                raise TypeError
    return md


def append_dicts(list_of_dicts):
    new_dict = {}
    for dictionary in list_of_dicts:
        new_dict.update(copy.deepcopy(dictionary))
    return new_dict

def mod_dict(original, add_dicts, subtract_keys):
    new_dict = copy.deepcopy(original)
    for key in subtract_keys:
        new_dict.pop(key)
    new_dict = append_dicts([new_dict, add_dicts])
    return new_dict


#New standard: Return "Green", "Yellow", "Red", or "Exclude"
acceptable_values = ["Green","Yellow","Red","Exclude"]
#After returning this, then return True/False for row_complete

def clean_string_list(input_list):
    empty_strings = ['',' ','\n','\t','  ']
    output_list = []
    for item in input_list:
        if item not in empty_strings:
            output_list.append(item)
    return output_list

def def_return_complex_inequality(input_string, adjust = 0): # input_string like "Exclude = 0; Green <= 2 m; Red > 2.5 meters"
    #Only one (or zero) conditional per part, must be a comparison to a number (float)
    zero = [0,0.0,'0','zero','ZERO','Zero','0.0']
    used_values = []
    inequalities = ['<','>','=','<=','>=','!=']
    input_parts = input_string.split(';')
    function_list = []
    for part in input_parts:
        items = clean_string_list(part.split(' '))
        if items[0] not in acceptable_values: raise RuntimeError('Nonsense: {0} is not a possible output'.format(items[0]))
        else: used_values.append(items[0])
        if items[1] not in inequalities: raise RuntimeError('Bad inequality: {0}'.format(items[1]))
        if items[2] in zero: comparison_value = 0.0 + smart_units(adjust)
        else: comparison_value = smart_units('{0} {1}'.format(items[2],items[3])) + smart_units(adjust)

        func_template = "def hidden_function(value):\n\tif value {0} {1}: return '{2}'\n".format(items[1],comparison_value,items[0])
        exec func_template in globals(), locals()

        function_list.append(hidden_function)
    if "Yellow" not in used_values: default_return = "Yellow"
    else: default_return = None

    def return_complex_inequality(value):
        try: value = float(value)
        except ValueError: return 'Green', False
        for funct in function_list:
            test = funct(value)
            if test: return test, True
        return default_return, True

    return return_complex_inequality


def def_return_constant(K):
    if K not in gap_values:
        print "ERROR: {0} is not in {1}".format(K,acceptable_values)
        raise Exception("Constant value must be an acceptable value")

    def return_constant(value):
        return K, True

    return return_constant


def def_simpleGYR(GY, YR): #Takes two thresholds, one between green and yellow, one between yellow and red
    if GY > YR:
        print GY,"is not <",YR
        raise Exception("Green-Yellow transition must be less than or equal to Yellow-Red transition")

    def simpleGYR(value):
        if value == 'none': return "Green", False #Assume the best, but communicate the data isn't complete
        elif value < GY: return "Green", True
        elif value < YR: return "Yellow", True
        else: return "Red", True

    return simpleGYR

def def_YGR(YG, GR): #Takes two thresholds, one between yellow and green, one between green and red. Unusual model
    if GR < YG:
        print GR,"is not >",YG
        raise Exception("Yellow-Green transition must be less than or equal to Green-Red transition")

    def YGR(value):
        if value == 'none': return "Green", False #Assume the best, but communicate the data isn't complete
        elif value < YG: return "Yellow", True
        elif value < GR: return "Green", True
        else: return "Red", True

    return YGR


def def_reverse_simpleGYR(GY, YR):
    if GY < YR: raise Exception("Green-Yellow transition must be greater than or equal to Yellow-Red transition")

    def reverse_simpleGYR(value):
        if value == 'none': return "Green", False #Assume the best - RG=0, but communicate the data isn't complete
        elif value > GY: return "Green", True
        elif value > YR: return "Yellow", True
        else: return "Red", True

    return reverse_simpleGYR


def def_simpleGR(GR): #Takes one threshold, between green and red
    def simpleGR(value):
        if value == 'none': return "Green", False
        elif value < GR: return "Green", True
        else: return "Red", True

    return simpleGR


def def_reverse_simpleGR(RG): #Takes one threshold, between green and red
    def reverse_simpleGR(value):
        if value == 'none': return "Green", False
        elif value > RG: return "Green", True
        else: return "Red", True

    return reverse_simpleGR


def def_simpleGY(GY): #Takes one threshold, between green and yellow
    def simpleGY(value):
        if value == 'none': return "Green", False
        if value < GY: return "Green", True
        else: return "Yellow", True

    return simpleGY


def def_reverse_simpleGY(GY): #Takes one threshold, between green and yellow
    def reverse_simpleGY(value):
        if value == 'none': return "Green", False
        if value > GY: return "Green", True
        else: return "Yellow", True

    return reverse_simpleGY


def def_RGR(RG, GR): #A slice of green with red on either side.
    def RGR(value):
        if value == 'none': return "Green", False
        if value > RG and value < GR: return "Green", True
        else: return "Red", True

    return RGR


def def_GYRYG(GY,YR,RY,YG): #Middle values bad, extreme values good
    def GYRYG(value):
        if GY < YR and YR < RY and RY < YG:
            if value == 'none': return "Green", False
            elif value < GY: return "Green", True
            elif value < YR: return "Yellow", True
            elif value < RY: return "Red", True
            elif value < YG: return "Yellow", True
            else: return "Green", True
        else: raise RuntimeError("RYGYR passed values that don't make sense")

    return GYRYG

def def_RYGYR_ISB2(RY,YG,GY,YR): #Middle values good - specific inequalities defined by ISB2
    if RY < YG and YG < GY and GY < YR: pass
    else: raise RuntimeError("RYGYR_ISB2 passed values that don't make sense")

    def RYGYR_ISB2(value):
        if value == 'none': return "Green", False
        elif value < RY: return "Red", True
        elif value < YG: return "Yellow", True
        elif value <= GY: return "Green", True
        elif value <= YR: return "Yellow", True
        else: return "Red", True

    return RYGYR_ISB2

def def_RYGYR_GOM(RY,YG,GY,YR): #Middle values good - specific inequalities defined by DISP_Ship_plane_heli
    if RY < YG and YG < GY and GY < YR: pass
    else: raise RuntimeError("RYGYR_DISP_ship_plane_heli passed values that don't make sense")
    def RYGYR_GOM(value):
        if value == 'none': return "Green", False
        elif value < RY: return "Red", True
        elif value <= YG: return "Yellow", True
        elif value <= GY: return "Green", True
        elif value < YR: return "Yellow", True
        else: return "Red", True

    return RYGYR_GOM

def def_RYGYR(RY,YG,GY,YR): #Middle values good - specific inequalities defined by DISP_Ship_plane_heli
    def RYGYR_ISB2(value):
        if RY < YG and YG < GY and GY < YR:
            if value == 'none': return "Green", False
            elif value < RY: return "Red", True
            elif value < YG: return "Yellow", True
            elif value <= GY: return "Green", True
            elif value <= YR: return "Yellow", True
            else: return "Red", True
        else: raise RuntimeError("RYGYR_ISB2 passed values that don't make sense")

    return RYGYR_ISB2

def def_GYR_plus_threshold(GY,YR,threshold):
    if GY > YR: raise Exception('ERROR: GYR_plus_threshold inequality not satisfied',GY,"not <=",YR)

    def GYR_plus_threshold(value1, value2):
        if value1 == 'none' or value2 == 'none': return "Green", False
        elif value2 < threshold:
            if value1 < GY: return "Green", True
            elif value1 < YR: return "Yellow", True
            else: return "Red", True
        else: return "Green", True #If value2 (usually ice) is greater than the threshold, it's all green.

    return GYR_plus_threshold



def def_GYR_x_threshold(GY_low, YR_low, threshold, GY_high, YR_high):
    if GY_low > YR_low or GY_high > YR_high: raise Exception('ERROR: GYR_plus_threshold inequality not satisfied.')

    def GYR_x_threshold(value1, value2):
        if value1 == 'none' or value2 == 'none': return "Green", False
        elif value2 < threshold:
            if value1 < GY_low: return "Green", True
            elif value1 < YR_low: return "Yellow", True
            else: return "Red", True
        else:
            if value1 < GY_high: return "Green", True
            elif value1 < YR_high: return "Yellow", True
            else: return "Red", True

    return GYR_x_threshold


def def_GR_plus_threshold(GR,threshold):

    def GR_plus_threshold(value1, value2):
        if value1 == 'none' or value2 == 'none': return "Green", False
        elif value2 < threshold:
            if value1 < GR: return "Green", True
            else: return "Red", True
        else: return "Green", True #If value2 (usually ice) is greater than the threshold, it's all green.

    return GR_plus_threshold


def def_bathtubRYGYR(RY,YG,GY,YR): #Green in the middle, red at the extremes
    if not RY <= YG <= GY <= YR: raise Exception('ERROR: Bathtub inequality not satisified, not',RY,"<=",YG,"<=",GY,"<=",YR)

    def bathtub(value):
        if value == 'none': return "Green", False
        elif value < RY: return "Red", True
        elif value < YG: return "Yellow", True
        elif value < GY: return "Green", True
        elif value < YR: return "Yellow", True
        else: return "Red", True

    return bathtub



def def_bathtubRGR(RG, GR): #Green in the middle, red at the extremes
    if not RG < GR: raise Exception('ERROR: Bathtub inequality not satisfied, not',RG,"<",GR)

    def bathtub(value):
        if value == 'none': return "Green", False
        elif value < RG: return "Red", True
        elif value < GR: return "Green", True
        else: return "Red", True

    return bathtub


def def_humpGRG(GR, RG): #Green in the middle, red at the extremes
    if not GR < RG: raise Exception('ERROR: Bathtub inequality not satisfied, not',RG,"<",GR)

    def humpGRG(value):
        if value == 'none': return "Green", False
        elif value < GR: return "Green", True
        elif value < RG: return "Red", True
        else: return "Green", True

    return humpGRG


def def_dayGR():
    def dayGR(day):
        if day: return "Green", True
        else: return "Red", True

    return dayGR


def def_dayGY():
    def dayGY(day):
        if day: return "Green", True
        else: return "Yellow", True

    return dayGY


def def_exclude_night():
    def exclude_night(day):
        if day: return "Green", True
        else: return "Exclude", True

    return exclude_night


def def_exclude_var_gap():
    def exclude_var_gap(value):
        if value == 'none': return "Exclude", False
        else:  return "Green", True

    return exclude_var_gap


def def_categorical_GYR(green_list, yellow_list, red_list):
    #ideally check if there's overlap in any of these lists

    def categorical_GYR(value):
        if value in green_list: return "Green", True
        elif value in yellow_list: return "Yellow", True
        elif value in red_list: return "Red", True
        else: return "Green", False #It's possible that "none" could be passed as a value to this function, but usually it'd fall here.

    return categorical_GYR

def def_temperature_cludge(Warm, Cool, Cold, Windy, Breezy):
    if Warm < Cool or Cool < Cold or Windy < Breezy: raise Exception("temperature_cludge passed mis-ordered values")

    def temperature_cludge(temp, wind):
        if temp == 'none' or wind == 'none': return "Green", False
        elif temp > Warm: return "Green", True
        elif temp > Cool and wind > Windy: return "Yellow", True
        elif wind > Breezy: return "Red", True
        elif temp <= Cold: return "Red", True
        else: return "Green", True #This is an ambiguous case - the description doesn't say what RG this should be - assuming the best.

    return temperature_cludge


def def_temperature_cludge2(Warm, Cool, Windy, Breezy):
    if Warm < Cool or Windy < Breezy: raise Exception("temperature_cludge passed mis-ordered values")

    def temperature_cludge(temp, wind):
        if temp == 'none' or wind == 'none': return "Green", False
        elif temp > Warm: return "Green", True
        elif temp > Cool and wind > Windy: return "Yellow", True
        elif wind > Breezy: return "Red", True
        else: return "Green", True #This is an ambiguous case - the description doesn't say what RG this should be - assuming the best.

    return temperature_cludge


def def_steepness_cludge(too_steep, small, small_swell, big, big_swell):
    if small > small_swell or small > big or big > big_swell: raise Exception("Unreasonable values pssed to steepness cludge")

    def steepness_cludge(wave, steep):
        if wave == 'none' or steep == 'none': return "Green", False
        elif wave < small or (wave < small_swell and steep < too_steep): return "Green", True
        elif wave < big or (wave < big_swell and steep < too_steep): return "Yellow", True
        else: return "Red", True

    return steepness_cludge


def def_dispersant_wave_cludge(too_small, smallish, too_large):
    if too_small > smallish or smallish > too_large: raise Exception("dispersant_wave_cludge passed mis-ordered values")

    def dispersant_wave_cludge(wave):
        if wave == 'none': return "Green", False
        elif wave < too_small: return "Red", True
        elif wave < smallish: return "Yellow", True
        elif wave < too_large: return "Green", True
        else: return "Red", True

    return dispersant_wave_cludge


def def_GYR_plus_bool(true_GY,true_YR, False_GY, False_YR):
    if true_GY > true_YR or False_GY > False_YR: raise Exception("GYR_plus_bool got mis-ordered values")

    def GYR_plus_bool(value, bool):
        if value == "none" or bool == "none": return "Green", False
        if bool:
            if value < true_GY: return "Green", True
            elif value < true_YR: return "Yellow", True
            else: return "Red", True
        else:
            if value < False_GY: return "Green", True
            elif value < False_YR: return "Yellow", True
            else: return "Red", True

    return GYR_plus_bool


def def_GR_plus_bool(True_GR, False_GR):

    def GR_plus_bool(value, bool):
        if value == "none" or bool == "none": return "Green", False
        if bool:
            if value < True_GR: return "Green", True
            else: return "Red", True
        else:
            if value < False_GR: return "Green", True
            else: return "Red", True

    return GR_plus_bool



def def_reverse_GYR_plus_bool(true_GY,true_YR, False_GY, False_YR):
    if true_GY < true_YR or False_GY < False_YR: raise Exception("GYR_plus_bool got mis-ordered values")

    def reverse_GYR_plus_bool(value, bool):
        if value == "none" or bool == "none": return "Green", False
        if bool:
            if value > true_GY: return "Green", True
            elif value > true_YR: return "Yellow", True
            else: return "Red", True
        else:
            if value > False_GY: return "Green", True
            elif value > False_YR: return "Yellow", True
            else: return "Red", True

    return reverse_GYR_plus_bool


def def_reverse_GR_plus_bool(True_GR, False_GR):

    def reverse_GR_plus_bool(value, bool):
        if value == "none" or bool == "none": return "Green", False
        if bool:
            if value > True_GR: return "Green", True
            else: return "Red", True
        else:
            if value > False_GR: return "Green", True
            else: return "Red", True

    return reverse_GR_plus_bool


def def_GYR_plus_category(A_GY, A_YR, B_GY, B_YR, A_cat, B_cat):
    if A_GY > A_YR or B_GY > B_YR: raise Exception("GYR_plus_category got mis-ordered values")
    for cat in A_cat:
        if cat in B_cat: raise Exception("GYR_plus_category has overlapping categories")

    def GYR_plus_category(value,categorical):
        if value == "none" or categorical == "none": return "Green", False
        if categorical in A_cat:
            if value < A_GY: return "Green", True
            elif value < A_YR: return "Yellow", True
            else: return "Red", True
        elif categorical in B_cat:
            if value < B_GY: return "Green", True
            elif value < B_YR: return "Yellow", True
            else: return "Red", True
        else: return "Green", False #Ambiguous categorical value

    return GYR_plus_category


def def_GYR_plus_day_GOM(A_GY, A_YR, B_YR):
    if A_GY < A_YR: raise Exception("GYR_plus_category got mis-ordered values")

    def GYR_plus_day_GOM(value,day):
        if value == "none" or day == "none": return "Green", False
        if day:
            if value >= A_GY: return "Green", True
            elif value >= A_YR: return "Yellow", True
            else: return "Red", True
        else:
            if value >= B_YR: return "Yellow", True
            else: return "Red", True

    return GYR_plus_day_GOM

def def_RYG_GOM(A_RY, A_YG):
    if A_RY > A_YG: raise Exception("RYG_GOM got mis-ordered values")

    def RYG_GOM(value,day):
        if value == "none" or day == "none": return "Green", False
        elif value > A_RY and day: return "Green", True
        elif value > A_YG and day: return "Yellow", True
        else: return "Red", True

    return RYG_GOM

def def_GR_GOM(A_GR):

    def GR_GOM(value,day):
        if value == "none" or day == "none": return "Green", False
        if value > A_GR and day: return "Green", True
        else: return "Red", True

    return GR_GOM

def def_GR_plus_categorical(A_GR, B_GR, A_cat, B_cat):
    for cat in A_cat:
        if cat in B_cat: raise Exception("GYR_plus_category has overlapping categories")

    def GR_plus_category(value,categorical):
        if value == "none" or categorical == "none": return "Green", False
        if categorical in A_cat:
            if value < A_GR: return "Green", True
            else: return "Red", True
        elif categorical in B_cat:
            if value < B_GR: return "Green", True
            else: return "Red", True
        else: return "Green", False #Ambiguous categorical value

    return GR_plus_category

def def_vis_day_cludge_GYR(dayGY, dayYR, nightYR):
    def vis_day_cludge(vis, day):
        if vis == 'none' or day == 'none': return "Green", False
        if (day and vis <= dayYR) or (not day and vis <= nightYR):
            return "Red", True
        elif not day or vis <= dayGY:
            return "Yellow", True
        else:
            return "Green", True

    return vis_day_cludge

def def_no_wave_cludge(calm, windy, icy, v_windy, x_windy):
    if not calm <= windy or not v_windy <= x_windy or icy < 0 or icy > 1: raise Exception("Invalid input for beaufort_wave_cludge",calm,windy,icy,v_windy,x_windy)

    def beaufort_wave_cludge(wind, ice):
        if wind == "none" or ice == "none": return "Green", False
        elif ice < icy:
            if wind < calm: return "Green", True
            elif wind < windy: return "Yellow", True
            else: return "Red", True
        else: #So icy there are no waves.
            if wind < v_windy: return "Green", True
            elif wind < x_windy: return "Yellow", True
            else: return "Red", True

    return beaufort_wave_cludge

def def_beuafort_wave_windX_cludge(calm, windy, icy, v_windy, x_windy, wind_scaler):
    if not calm <= windy or not v_windy <= x_windy or icy < 0 or icy > 1 or wind_scaler < 0: raise Exception("Invalid input for beaufort_wave_windK_cludge",calm,windy,icy, wind_scaler)

    def beaufort_wave_cludge(wind, ice):
        if wind == "none" or ice == "none": return "Green", False
        else:
            wind *= wind_scaler
            if ice < icy:
                if wind < calm: return "Green", True
                elif wind < windy: return "Yellow", True
                else: return "Red", True
            else: #So icy there are no waves.
                if wind < v_windy: return "Green", True
                elif wind < x_windy: return "Yellow", True
                else: return "Red", True

    return beaufort_wave_cludge


def def_beuafort_bathtub_wave_cludge(still, calm, windy, v_windy, icy):
    if not still <= calm <= windy <= v_windy or icy < 0 or icy > 1: raise Exception("Invalid input for beaufort_bathtub_wave_cludge",still, calm, windy, v_windy, icy)

    def beaufort_bathtub_wave_cludge(wind, ice):
        if wind == 'none' or ice == 'none': return "Green", False
        elif wind >= v_windy: return "Red", True
        elif wind >= windy: return "Yellow", True
        elif ice < icy:
            if wind < still: return "Red", True
            elif wind < calm: return "Yellow", True
            else: return "Green", True
        else:
            return "Green", True

    return beaufort_bathtub_wave_cludge



def def_median_bathtub_wave_cludge(windy_no_ice, windy, v_windy, icy):
    if not windy <= v_windy or icy < 0 or icy > 1: raise Exception("Invalid input for median_bathtub_wave_cludge",windy_no_ice, windy, v_windy, icy)

    def median_bathtub_wave_cludge(wind, ice):
        if wind == 'none' or ice == 'none': return "Green", False
        if ice < icy:
            if wind > windy_no_ice: return "Red", True
            else: return "Green", True
        else:
            if wind >= v_windy: return "Red", True
            elif wind >= windy: return "Yellow", True
            else: return "Green", True

    return median_bathtub_wave_cludge

