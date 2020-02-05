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

output_root = "Yakutat_Output"
data_root = "data/Yakutat/"

wind_chill_function = populate_wind_chill_metric

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
            "file_name": "25339_long.csv",
            "file_type": "csv",
            "lat":29.73333,     "lon":-85.03333,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"WindSpeed",
            "wind_unit":"mph",
            "vis_column":"vis_miles",
            "vis_unit":"miles",
            "dir_column":"WindDirection",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"DryBulbCelsius",
            "temp_unit":"C",
            "rain_column":'HourlyPrecip',
            "rain_unit":'inches'
        },
        "12832_2": {
            "file_name": "25339_short.csv",
            "file_type": "csv",
            "lat":29.73333,     "lon":-85.03333,
            "fill_undefined_waves":False,
            "time_column":"datetime",
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_offset": 0,
            "UTM_offset":0,
            "wind_column":"Wind Speed (kt)",
            "wind_unit":"knots",
            "vis_column":"vis_miles",
            "vis_unit":"miles",
            "dir_column":"Wind Direction",
            "dir_unit":"degrees",
            "ceil_column":"ceiling_ft",
            "ceil_unit":"feet",
            "temp_column":"Dry Bulb Temp",
            "temp_unit":"F",
            "rain_column":'Precip. Total',
            "rain_unit":'inches'
        }
    },
    "merges": {
        'Yakutat_airport':{
            "list_of_stations":['12832_1','12832_2'],
            "merge_type":'single',
            "lat":29.73333,     "lon":-85.03333,
            "UTM_offset":0,
            "models": []
        }
    }
}
