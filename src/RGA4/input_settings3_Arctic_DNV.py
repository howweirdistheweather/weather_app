# coding: utf-8

from convert_functions3 import *
from populate_columns3 import (
    populate_wind_chill_english,
    populate_wind_chill_metric
)
from model_settings3_Arctic_DNV import (
    primary_RGA_list,
    component_RGA_list
)

#Locations
#Barrow:		"lat":71.2834,  "lon":-156.7815,
#Central BS:	"lat":57.026,   "lon":-177.738,
#Chukchi        "lat":70.87,    "lon":-165.24,

#40783 (A):         "lat":57.094448,    "lon":-177.786774, #A
#58146 (B):         "lat":70.780769,    "lon":-165.37912,  #B
#70291 (C):         "lat":69.996246,    "lon":-136.636581, #C
#74923 (D):         "lat":85.407059,    "lon":-96.115501,  #D
#99236 (E):         "lat":68.28392,     "lon":-58.671307,  #E
#112606 (F):        "lat":58.59824,     "lon":-56.79343,   #F
#94144 (G):         "lat":68.878151,    "lon":-9.67826,    #G
#80463 (H):         "lat":76.054482,    "lon":14.845452,   #H
#72595 (I):         "lat":69.754631,    "lon":42.089161,   #I
#50312 (J):         "lat":74.276672,    "lon":137.090164,  #J
#45054 (K):         "lat":61.509029,    "lon":-177.747955, #K

#Next time - use smart_units in here.

output_root = "DNV_Arctic"
data_root = "data/"+output_root+"/"

wind_chill_function = populate_wind_chill_metric


inputs = {
    "clean": {#Provides settings for cleaning data.  Values over max are replaced, values under min become "null"
        "extremes": {#Goes through input data and cleans out unreasonable values, as set here.
            'wind': {'maximum': velocity(300,'mph'), 'minimum': 0},
            'gust': {'maximum': velocity(300,'mph'), 'minimum': 0},
            'wave': {'maximum': wave_height(150,'ft'), 'minimum': 0},
            'temp': {'maximum': temperature(100,'c'), 'minimum': temperature(-100,'c')},
            'wtemp': {'maximum': temperature(100,'c'), 'minimum': temperature(-10,'c')},
            'period': {'maximum': period(2,'min'), 'minimum': period(0.1,'second')},
            'vis': {'maximum': smart_units('10 nmi'), 'minimum': 0},#Some older data includes very large visibility estimates (at least 100 km) but we're cutting these down to 16 km ~ 10 mi
            'ceil': {'maximum': smart_units('10 nmi'), 'minimum': 0}, #ceiling is in km
            'dir': {'maximum': 10000, 'minimum': 0},#Not limiting this, because other code handles >=360 values better.
            'cover': {'maximum': 1.0, 'minimum': 0.0} #Proportion (at least in WS)
        }
    },
    "years": range(2006,2016),
#    "years": [2008],
    "stations": {
        "A": {
            "file_name": "Loc_A_40783.txt",
            "file_type": "csv",
            "lat":57.094448,    "lon":-177.786774,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "B": {
            "file_name": "Loc_B_58146.txt",
            "file_type": "csv",
            "lat":70.780769,    "lon":-165.37912,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "C": {
            "file_name": "Loc_C_70291.txt",
            "file_type": "csv",
            "lat":69.996246,    "lon":-136.636581,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "D": {
            "file_name": "Loc_D_74923.txt",
            "file_type": "csv",
            "lat":85.407059,    "lon":-96.115501,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "E": {
            "file_name": "Loc_E_99236.txt",
            "file_type": "csv",
            "lat":68.28392,     "lon":-58.671307,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "F": {
            "file_name": "Loc_F_112606.txt",
            "file_type": "csv",
            "lat":58.59824,     "lon":-56.79343,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "G": {
            "file_name": "Loc_G_94144.txt",
            "file_type": "csv",
            "lat":68.878151,    "lon":-9.67826,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "H": {
            "file_name": "Loc_H_80463.txt",
            "file_type": "csv",
            "lat":76.054482,    "lon":14.845452,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "I": {
            "file_name": "Loc_I_72595.txt",
            "file_type": "csv",
            "lat":69.754631,    "lon":42.089161,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "J": {
            "file_name": "Loc_J_50312.txt",
            "file_type": "csv",
            "lat":74.276672,    "lon":137.090164,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "K": {
            "file_name": "Loc_K_45054.txt",
            "file_type": "csv",
            "lat":61.509029,    "lon":-177.747955,
            "fill_undefined_waves":True,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset": 0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "temp_column": "Ta",
            "temp_unit":"C",
            "wtemp_column": "Ts",
            "wtemp_unit":"C",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"km",
            "dir_column":"Wdir",
            "period_column":"Tm",
            "period_unit":"s",
            "ice_column":"Icecover",
            "ice_units":"%",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "CBS1": { #NDBC data is in UTC datetime
            "file_names": ["46035h1985.txt","46035h1986.txt","46035h1987.txt","46035h1988.txt","46035h1989.txt","46035h1990.txt","46035h1991.txt","46035h1992.txt","46035h1993.txt","46035h1994.txt","46035h1995.txt","46035h1996.txt","46035h1997.txt","46035h1998.txt"],
            "file_type": "NBDC",
            "lat":57.026,   "lon":-177.738,
            "time_offset": 0,
            "UTM_offset": 0,
            "time_single_column":False,
            "year_two_digit":True,
            "year_column":"YY",
            "month_column":"MM",
            "day_column":"DD",
            "hour_column":"hh",
            "minute_column":"null",
            "discard_2nd_line":False,
            "wave_column":"WVHT",
            "wave_unit":"m",
            "period_column":"DPD",
            "wind_column":"WSPD",
            "wind_unit":"m/s",
            "gust_column":"GST",
            "gust_unit":"m/s",
            "dir_column":"WD",
            "temp_column":"ATMP",
            "temp_unit":"C",
            "ignore_values":{'dir':'999', 'wind':'99.0', 'wave':'99.00', 'period':'99.00', 'gust':'99.0','temp':'999.0','wtemp':'999.0'}
        },
        "CBS2": {
            "file_names": ["46035h1999.txt","46035h2000.txt","46035h2001.txt","46035h2002.txt","46035h2003.txt","46035h2004.txt"],
            "file_type": "NBDC",
            "lat":57.026,   "lon":-177.738,
            "time_offset": 0, #not sure this is right.
            "UTM_offset": 0,
            "time_single_column":False,
            "year_column":"YYYY",
            "month_column":"MM",
            "day_column":"DD",
            "hour_column":"hh",
            "minute_column":"null",
            "discard_2nd_line":False,
            "wave_column":"WVHT",
            "wave_unit":"m",
            "period_column":"DPD",
            "wind_column":"WSPD",
            "wind_unit":"m/s",
            "gust_column":"GST",
            "gust_unit":"m/s",
            "dir_column":"WD",
            "temp_column":"ATMP",
            "temp_unit":"C",
            "ignore_values":{'dir':'999', 'wind':'99.0', 'wave':'99.00', 'period':'99.00', 'gust':'99.0','temp':'999.0','wtemp':'999.0'}
        },
        "CBS3": {
            "file_names": ["46035h2005.txt","46035h2006.txt"],
            "file_type": "NBDC",
            "lat":57.026,   "lon":-177.738,
            "time_offset": 0, #not sure this is right.
            "UTM_offset": 0,
            "time_single_column":False,
            "year_column":"YYYY",
            "month_column":"MM",
            "day_column":"DD",
            "hour_column":"hh",
            "minute_column":"mm",
            "discard_2nd_line":True,
            "wave_column":"WVHT",
            "wave_unit":"m",
            "period_column":"DPD",
            "wind_column":"WSPD",
            "wind_unit":"m/s",
            "gust_column":"GST",
            "gust_unit":"m/s",
            "dir_column":"WD",
            "temp_column":"ATMP",
            "temp_unit":"C",
            "ignore_values":{'dir':'999', 'wind':'99.0', 'wave':'99.00', 'period':'99.00', 'gust':'99.0','temp':'999.0','wtemp':'999.0'}
        },
        "CBS4": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_names": ["46035h2007.txt","46035h2008.txt","46035h2009.txt","46035h2010.txt","46035h2011.txt","46035h2012.txt","46035h2014.txt","46035h2015.txt"],
            "file_type": "NBDC",
            "lat":57.026,   "lon":-177.738,
            "time_offset": 0,
            "UTM_offset": 0,
            "time_single_column":False,
            "year_column":"#YY",
            "month_column":"MM",
            "day_column":"DD",
            "hour_column":"hh",
            "minute_column":"mm",
            "discard_2nd_line":True,
            "wave_column":"WVHT",
            "wave_unit":"m",
            "period_column":"DPD",
            "wind_column":"WSPD",
            "wind_unit":"m/s",
            "gust_column":"GST",
            "gust_unit":"m/s",
            "dir_column":"WDIR",
            "temp_column":"ATMP",
            "temp_unit":"C",
            "wtemp_column":"WTMP",
            "wtemp_unit":"C",
            "ignore_values":{'dir':'999', 'wind':'99.0', 'wave':'99.00', 'period':'99.00', 'gust':'99.0','temp':'999.0','wtemp':'999.0'}
        },
        "MOB2": { #Are these local or UTC time?
            "file_name": "Joint_MetBuoy_MOB2_2011.csv",
            "file_type": "csv",
            "lat":70.87,    "lon":-165.24,
            "date_format":"~%Y-%m-%d %H:%M",
            "time_offset":0,
            "UTM_offset":0,
            "time_single_column":True,
            "time_column":"DATE_TIME_LOC",
            "wind_unit":"kts",
            "wind_column":"WSPD_ KTS",
            "gust_unit":"kts",
            "gust_column":"WSPD_MAX_KTS",
            "wave_column":"WAVE_SIG_M",
            "wave_unit":"m",
            "temp_column": "ATMP_C",
            "temp_unit":"C",
            "wtemp_column": "WTMP_SB_C",
            "wtemp_unit":"C",
            "period_column":"WAVE_PRD_S",
            "period_unit":"s",
            "dir_column":"WDIR_T",
            "ignore_values":{'dir':'999', 'wave':'999', 'wind':'999', 'gust':'999','temp':'999','wtemp':'999','period':'999'} #Could use "ignore_value" instead, but an unused column (air pressure) uses 999 as an actual value (ignore 9999)
        },
        "CS": {#Are these local or UTC time?
            "file_name": "COP_Stat_MetBuoy_2010.csv",
            "file_type": "csv",
            "lat":70.87,    "lon":-165.24,
            "date_format":"~%Y-%m-%d %H:%M",
            "time_offset":0,
            "UTM_offset":0,
            "time_single_column":True,
            "time_column":"DATE_TIME_ADT",
            "wind_unit":"kts",
            "wind_column":"WSPD_KTS",
            "gust_unit":"kts",
            "gust_column":"WSPD_MAX_KTS",
            "wave_column":"WAVE_SIG_M",
            "wave_unit":"m",
            "temp_column": "ATMP_C",
            "temp_unit":"C",
            "wtemp_column": "WTMP_SB_C",
            "wtemp_unit":"C",
            "period_column":"WAVE_PRD_S",
            "period_unit":"s",
            "dir_column":"WDIR_T",
            "ignore_value":"-999"
        }
    },
    "merge_order":['A','B','C','D','E','F','G','H','I','J','K'],
    "merges": {

#40783 (A):         "lat":57.094448,    "lon":-177.786774, #A
#58146 (B):         "lat":70.780769,    "lon":-165.37912,  #B
#70291 (C):         "lat":69.996246,    "lon":-136.636581, #C
#74923 (D):         "lat":85.407059,    "lon":-96.115501,  #D
#99236 (E):         "lat":68.28392,     "lon":-58.671307,  #E
#112606 (F):        "lat":58.59824,     "lon":-56.79343,   #F
#94144 (G):         "lat":68.878151,    "lon":-9.67826,    #G
#80463 (H):         "lat":76.054482,    "lon":14.845452,   #H
#72595 (I):         "lat":69.754631,    "lon":42.089161,   #I
#50312 (J):         "lat":74.276672,    "lon":137.090164,  #J
#45054 (K):         "lat":61.509029,    "lon":-177.747955, #K
        "A": {
            "list_of_stations": ["A"],
            "merge_type":'single',
            "lat":57.094448,    "lon":-177.786774, #A
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models": "All"
        },
        "B": {
            "list_of_stations": ["B"],
            "merge_type":'single',
            "lat":70.780769,    "lon":-165.37912,  #B
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "C": {
            "list_of_stations": ["C"],
            "merge_type":'single',
            "lat":69.996246,    "lon":-136.636581, #C
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "D": {
            "list_of_stations": ["D"],
            "merge_type":'single',
            "lat":85.407059,    "lon":-96.115501,  #D
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "E": {
            "list_of_stations": ["E"],
            "merge_type":'single',
            "lat":68.28392,     "lon":-58.671307,  #E
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "F": {
            "list_of_stations": ["F"],
            "merge_type":'single',
            "lat":58.59824,     "lon":-56.79343,   #F
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "G": {
            "list_of_stations": ["G"],
            "merge_type":'single',
            "lat":68.878151,    "lon":-9.67826,    #G
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "H": {
            "list_of_stations": ["H"],
            "merge_type":'single',
            "lat":76.054482,    "lon":14.845452,   #H
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "I": {
            "list_of_stations": ["I"],
            "merge_type":'single',
            "lat":69.754631,    "lon":42.089161,   #I
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "J": {
            "list_of_stations": ["J"],
            "merge_type":'single',
            "lat":74.276672,    "lon":137.090164,  #J
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        },
        "K": {
            "list_of_stations": ["K"],
            "merge_type":'single',
            "lat":61.509029,    "lon":-177.747955, #K
            "UTM_offset": 0,
            "interpolate_vars":['wind','temp','wtemp','dir','wave','ice', 'vis'],
            "models":  "All"
        }
    },
}
'''
    'comparisons':{
        'DISP1_comparison':{
            'merges':['A','B','C','D','E','F','G','H','I','J','K'],
            'models':['DISP1']
        }
    }
}'''