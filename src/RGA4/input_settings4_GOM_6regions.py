# coding: utf-8

from convert_functions3 import *
from populate_columns3 import (
    populate_wind_chill_english,
    populate_wind_chill_metric
)
from model_settings4_GOMv2 import (
    primary_RGA_list,
    component_RGA_list,
    all_RGAs
)

#WARNING - it's possible to get a mismatch between models if the include here and in project_specifics don't match

#Locations
#42001:		"lat":25.897,  "lon":-89.668,


#9042       "lat":28.5,     "lon":-90.75,
#8787       "lat":28.25,    "lon":-95.5,
#8544       "lat":27.875,   "lon":-84.0,
#7800       "lat":27.125,   "lon":-89.625,
#7712       "lat":27.0,     "lon":-85.75,
#7519       "lat":26.875,   "lon":-94.75,


#Next time - use smart_units in here.

output_root = "GOM_Output"
data_root = "data/GOM/"

wind_chill_function = populate_wind_chill_metric

NDBC_A_years = range(2005,2007) #[2005,2006]
NDBC_B_years = range(2007,2017)

inputs = {
    "clean": {#Provides settings for cleaning data.  Values over max are replaced, values under min become "null"
        "extremes": {#Goes through input data and cleans out unreasonable values, as set here.
            'wind': {'maximum': velocity(300,'mph'), 'minimum': 0},
            'gust': {'maximum': velocity(300,'mph'), 'minimum': 0},
            'wave': {'maximum': wave_height(150,'ft'), 'minimum': 0},
            'temp': {'maximum': temperature(100,'c'), 'minimum': temperature(-100,'c')},
            'period': {'maximum': period(2,'min'), 'minimum': period(0.1,'second')},
            'vis': {'maximum': smart_units('10 nmi'), 'minimum': 0},#Some older data includes very large visibility estimates (at least 100 km) but we're cutting these down to 16 km ~ 10 mi
            'ceil': {'maximum': smart_units('10 nmi'), 'minimum': 0}, #ceiling is in km
            'dir': {'maximum': 10000, 'minimum': 0},#Not limiting this, because other code handles >=360 values better.
            'cover': {'maximum': 1.0, 'minimum': 0.0} #Proportion (at least in WS)
        }
    },
    "years": range(2005,2017),
    "stations": {
        "Loc1_8787": {
            "file_name": "Model_data/Loc1_8787.txt",
            "file_type": "csv",
            "lat":28.25,    "lon":-95.5,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "Loc2_7519": {
            "file_name": "Model_data/Loc2_7519.txt",
            "file_type": "csv",
            "lat":26.875,   "lon":-94.75,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "Loc3_9042": {
            "file_name": "Model_data/Loc3_9042.txt",
            "file_type": "csv",
            "lat":28.5,     "lon":-90.75,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "Loc4_7800": {
            "file_name": "Model_data/Loc4_7800.txt",
            "file_type": "csv",
            "lat":27.125,   "lon":-89.625,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "Loc5_8544": {
            "file_name": "Model_data/Loc5_8544.txt",
            "file_type": "csv",
            "lat":27.875,   "lon":-84.0,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
        "Loc6_7712": {
            "file_name": "Model_data/Loc6_7712.txt",
            "file_type": "csv",
            "lat":27.0,     "lon":-85.75,
            "fill_undefined_waves":False,
            "time_column":{"Year":"YYYY","Month":"MM","Day":"DD","Hour":"HH","Minute":"null"},
            "time_single_column":False,
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Ws",
            "wind_unit":"m/s",
            "wave_column":"Hs",
            "wave_unit":"m",
            "vis_column":"Vis",
            "vis_unit":"m",
            "dir_column":"Wdir",
            "dir_unit":"degrees",
            "period_column":"Tm",
            "period_unit":"s",
            "ignore_values":{"wave":"-9.9","period":"-9.9"}
        },
    },


    "merges": {
        'Loc1_8787':{
            "list_of_stations":['Loc1_8787'],
            "merge_type":'single',
            "lat":28.25,    "lon":-95.5,
            "UTM_offset":0,
            "models": all_RGAs
        },
        'Loc2_7519':{
            "list_of_stations":['Loc2_7519'],
            "merge_type":'single',
            "lat":26.875,   "lon":-94.75,
            "UTM_offset":0,
            "models": all_RGAs
        },
        'Loc3_9042':{
            "list_of_stations":['Loc3_9042'],
            "merge_type":'single',
            "lat":28.5,     "lon":-90.75,
            "UTM_offset":0,
            "models": all_RGAs
        },
        'Loc4_7800':{
            "list_of_stations":['Loc4_7800'],
            "merge_type":'single',
            "lat":27.125,   "lon":-89.625,
            "UTM_offset":0,
            "models": all_RGAs
        },
        'Loc5_8544':{
            "list_of_stations":['Loc5_8544'],
            "merge_type":'single',
            "lat":27.875,   "lon":-84.0,
            "UTM_offset":0,
            "models": all_RGAs
        },
        'Loc6_7712':{
            "list_of_stations":['Loc6_7712'],
            "merge_type":'single',
            "lat":27.0,     "lon":-85.75,
            "UTM_offset":0,
            "models": all_RGAs
        }
    },
    'comparisons':{
        'MEC1_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['MEC1']
        },
        'MEC2_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['MEC2']
        },
        'MEC3_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['MEC3']
        },
        'DISP1_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['DISP1']
        },
        'DISP2_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['DISP2']
        },
        'DISP3_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['DISP3']
        },
        'ISB1_comparison':{
            'merges':['Loc1_8787','Loc2_7519','Loc3_9042','Loc4_7800','Loc5_8544','Loc6_7712'],
            'models':['ISB1']
        }
    }
}
