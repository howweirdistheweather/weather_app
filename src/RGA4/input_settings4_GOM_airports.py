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


#Apalachicola (12382):      "lat":29.73333,     "lon":-85.03333,
#Petersburg (12873):        "lat":27.91056,     "lon":-82.6875,
#Scholes (12923):           "lat":29.2733,      "lon":-94.8592,
#Louis_Armstrong (12916):   "lat":29.997528,    "lon":-90.277806,

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
        "12832_1": {
            "file_name": "Airport_data/12832_long.csv",
            "file_type": "csv",
            "lat":29.73333,     "lon":-85.03333,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"WindSpeed",
            "wind_unit":"mph",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"WindDirection",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"DryBulbCelsius",
            "temp_unit":"C",
        },
        "12832_2": {
            "file_name": "Airport_data/12832_short.csv",
            "file_type": "csv",
            "lat":29.73333,     "lon":-85.03333,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"Wind Speed (kt)",
            "wind_unit":"knots",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"Wind Direction",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"Dry Bulb Temp",
            "temp_unit":"F",
        },
        "12832_3": {
            "file_name": "Model_data/airport_12832.txt",
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
        "12873_1": {
            "file_name": "Airport_data/12873_long.csv",
            "file_type": "csv",
            "lat":27.91056,     "lon":-82.6875,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"WindSpeed",
            "wind_unit":"mph",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"WindDirection",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"DryBulbCelsius",
            "temp_unit":"C"
        },
        "12873_2": {
            "file_name": "Airport_data/12873_short.csv",
            "file_type": "csv",
            "lat":27.91056,     "lon":-82.6875,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"Wind Speed (kt)",
            "wind_unit":"knots",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"Wind Direction",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"Dry Bulb Temp",
            "temp_unit":"F"
        },
        "12873_3": {
            "file_name": "Model_data/airport_12873.txt",
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
        "12923_1": {
            "file_name": "Airport_data/12923_long.csv",
            "file_type": "csv",
            "lat":29.2733,      "lon":-94.8592,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"WindSpeed",
            "wind_unit":"mph",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"WindDirection",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"DryBulbCelsius",
            "temp_unit":"C"
        },
        "12923_2": {
            "file_name": "Airport_data/12923_short.csv",
            "file_type": "csv",
            "lat":29.2733,      "lon":-94.8592,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"Wind Speed (kt)",
            "wind_unit":"knots",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"Wind Direction",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"Dry Bulb Temp",
            "temp_unit":"F"
        },
        "12923_3": {
            "file_name": "Model_data/airport_12923.txt",
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
        "12916_1": {
            "file_name": "Airport_data/12916_long.csv",
            "file_type": "csv",
            "lat":29.997528,    "lon":-90.277806,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"WindSpeed",
            "wind_unit":"mph",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"WindDirection",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"DryBulbCelsius",
            "temp_unit":"C"
        },
        "12916_2": {
            "file_name": "Airport_data/12916_short.csv",
            "file_type": "csv",
            "lat":29.997528,    "lon":-90.277806,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"null",#"Wind Speed (kt)",
            "wind_unit":"knots",
            "vis_column":"null",#"vis_miles",
            "vis_unit":"miles",
            "dir_column":"null",#"Wind Direction",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"null",#"Dry Bulb Temp",
            "temp_unit":"F"
        },
        "12916_3": {
            "file_name": "Model_data/airport_12916.txt",
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
    },
    "merges": {
        'Apalachicola':{
            "list_of_stations":['12832_1','12832_2','12832_3'],
            "merge_type":'single',
            "lat":29.73333,     "lon":-85.03333,
            "UTM_offset":0,
            "models": "All"
        },
        'Petersburg':{
            "list_of_stations":['12873_1','12873_2','12873_3'],
            "merge_type":'single',
            "lat":27.91056,     "lon":-82.6875,
            "UTM_offset":0,
            "models": "All"
        },
        'Scholes':{
            "list_of_stations":['12923_1','12923_2','12923_3'],
            "merge_type":'single',
            "lat":29.2733,      "lon":-94.8592,
            "UTM_offset":0,
            "models": "All"
        },
        'Louis_Armstrong':{
            "list_of_stations":['12916_1','12916_2','12916_3'],
            "merge_type":'single',
            "lat":29.997528,    "lon":-90.277806,
            "UTM_offset":0,
            "models": "All"
        }
    }
}
