# coding: utf-8

from convert_functions3 import *
from populate_columns3 import (
    populate_wind_chill_english,
    populate_wind_chill_metric
)
from model_settings3_GOM import (
    primary_RGA_list,
    component_RGA_list
)

#Locations
#42001:		"lat":25.897,  "lon":-89.668,


#Next time - use smart_units in here.

output_root = "Clear_Seas_Output"
data_root = "data/Clear_Seas/"

wind_chill_function = populate_wind_chill_metric

NDBC_A_years = range(2005,2007)
NDBC_B_years = range(2007,2017)
NDBC_C_years = range(2005,2017)


inputs = {
    "clean": {#Provides settings for cleaning data.  Values over max are replaced, values under min become "null"
        "extremes": {#Goes through input data and cleans out unreasonable values, as set here.
            'wind': {'maximum': velocity(300,'mph'), 'minimum': 0.1},
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
    "years": range(2000,2017),
    "stations": {
       "c46147": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
           "file_name": "c46147_NukaModified.csv",
           "file_type": "csv",
           "lat":51.83,   "lon":131.23,
           "time_offset": 0,
           "UTM_offset": 0,
           "time_single_column":True,
           "date_format":"%Y-%m-%d %H:%M:%S",
           "time_column":"DATE",
           "wave_column":"VCAR",
           "wave_unit":"m",
           "period_column":"VTPK",
           "wind_column":"WSPD_best",
           "wind_unit":"m/s",
           "gust_column":"Gust_best",
           "gust_unit":"m/s",
           "dir_column":"WDIR_best",
           "temp_column":"DRYT",
           "temp_unit":"C",
       }
    },


    "merges": {
        "c46147": {
            "list_of_stations": ["c46147"],
            "merge_type":'single',
            "lat":51.83,   "lon":131.23,
            "UTM_offset": 0,
            "models": "All"
        }
    }
}
