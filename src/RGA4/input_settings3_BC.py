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
        "c46132": {
            "file_name": "c46132_NukaModified.csv",
            "file_type": "csv",
            "lat":49.74,   "lon":127.93,
            "time_offset": 0, #not sure this is right.
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
        },
        "c46132_alt1": {
            "file_name": "c46132_NukaModified.csv",
            "file_type": "csv",
            "lat":49.74,   "lon":127.93,
            "time_offset": 0, #not sure this is right.
            "UTM_offset": 0,
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_column":"DATE",
            "wave_column":"VCAR",
            "wave_unit":"m",
            "period_column":"VTPK",
            "wind_column":"WSPD_0",
            "wind_unit":"m/s",
            "gust_column":"GSPD_0",
            "gust_unit":"m/s",
            "dir_column":"WDIR_0",
            "temp_column":"DRYT",
            "temp_unit":"C",
        },
        "c46132_alt2": {
            "file_name": "c46132_NukaModified.csv",
            "file_type": "csv",
            "lat":49.74,   "lon":127.93,
            "time_offset": 0, #not sure this is right.
            "UTM_offset": 0,
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M:%S",
            "time_column":"DATE",
            "wave_column":"VCAR",
            "wave_unit":"m",
            "period_column":"VTPK",
            "wind_column":"WSPD_1",
            "wind_unit":"m/s",
            "gust_column":"GSPD_1",
            "gust_unit":"m/s",
            "dir_column":"WDIR_1",
            "temp_column":"DRYT",
            "temp_unit":"C",
        },
        "c46145": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46145_NukaModified.csv",
            "file_type": "csv",
            "lat":54.38,   "lon":132.42,
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
        },
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
       },
        "c46183": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46183_NukaModified.csv",
            "file_type": "csv",
            "lat":53.57,   "lon":131.14,
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
        },
        "c46185": {
            "file_name": "c46185_NukaModified.csv",
            "file_type": "csv",
            "lat":52.42,   "lon":129.79,
            "time_offset": 0, #not sure this is right.
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
        },
        "c46204": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46204_NukaModified.csv", # 2007 to present
            "file_type": "csv",
            "lat":51.38,   "lon":128.77,
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
        },
        "c46205": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46205_NukaModified.csv",
            "file_type": "csv",
            "lat":54.3,   "lon":133.4,
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
        },
        "c46206": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46206_NukaModified.csv",
            "file_type": "csv",
            "lat":48.83,   "lon":126,
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
        },
        "c46207": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46207_NukaModified.csv",
            "file_type": "csv",
            "lat":50.88,   "lon":129.91,
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
        },
        "c46208": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_name": "c46208_NukaModified.csv",
            "file_type": "csv",
            "lat":52.51,   "lon":132.69,
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
        },
    },


    "merges": {
        "c46132": {
            "list_of_stations": ["c46132"],
            "merge_type":'single',
            "lat":49.74,   "lon":127.93,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46132_alt": {
            "list_of_stations": ["c46132_alt1","c46132_alt2"],
            "merge_type":'single',
            "lat":49.74,   "lon":127.93,
            "UTM_offset": 0,
            "models": "All",
            "nonstandard":{"c46132_alt2":{"wind":"wind2", 'gust':'gust2', 'dir':'dir2'}}, #Renames these columns - used for characterization, but not for RGAs
        },
        "c46145": {
            "list_of_stations": ["c46145"],
            "merge_type":'single',
             "lat":54.38,   "lon":132.42,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46147": {
            "list_of_stations": ["c46147"],
            "merge_type":'single',
            "lat":51.83,   "lon":131.23,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46183": {
            "list_of_stations": ["c46183"],
            "merge_type":'single',
            "lat":53.57,   "lon":131.14,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46185": {
            "list_of_stations": ["c46185"],
            "merge_type":'single',
            "lat":52.42,   "lon":129.79,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46204": {
            "list_of_stations": ["c46204"],
            "merge_type":'single',
            "lat":51.38,   "lon":128.77,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46205": {
            "list_of_stations": ["c46205"],
            "merge_type":'single',
            "lat":54.3,   "lon":133.4,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46206": {
            "list_of_stations": ["c46206"],
            "merge_type":'single',
            "lat":48.83,   "lon":126,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46207": {
            "list_of_stations": ["c46207"],
            "merge_type":'single',
            "lat":50.88,   "lon":129.91,
            "UTM_offset": 0,
            "models": "All"
        },
        "c46208": {
            "list_of_stations": ["c46208"],
            "merge_type":'single',
            "lat":52.51,   "lon":132.69,
            "UTM_offset": 0,
            "models": "All"
        }
    }
}
