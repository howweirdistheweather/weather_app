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
#Generic Grays Harbor:		"lat":47,  "lon":-124,


#Next time - use smart_units in here.

output_root = "Grays_Harbor_Output"
data_root = "data/Grays_Harbor/"

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
    "years": range(2000,2020),
    "stations": {
        "Bowerman_Airport": {
            "file_names": ["Bowerman_Airport/{0}.csv".format(id) for id in [1522909,1522910,1522912,1522915,1522917,1522918,1522921]],
            "file_type": "csv",
            "lat":46.9727, "lon":-123.9302,
            "time_offset": 0, #not sure this is right.
            "UTM_offset": 0,
            "time_single_column":True,
            "date_format":"%Y-%m-%d %H:%M", #e.g. 2000-10-25 04:50
            "time_column":"DATE",
            "wind_column":"HOURLYWindSpeed",
            "wind_unit":"mph",
            "gust_column":"HOURLYWindGustSpeed",
            "gust_unit":"mph",
            "dir_column":"HOURLYWindDirection",
            "temp_column":"HOURLYDRYBULBTEMPC",
            "temp_unit":"C",
            "vis_column":"HOURLYVISIBILITY",
            "vis_unit":"miles"
        },
        "Buoy_46211_1": {
            "file_names": ["Buoy_46211/46211h2004.txt"],
            "file_type": "NBDC",
            "lat":47,  "lon":-124,
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
        "Buoy_46211_2": {
            "file_names": ["Buoy_46211/46211h2005.txt","Buoy_46211/46211h2006.txt"],
            "file_type": "NBDC",
            "lat":47,  "lon":-124,
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
        "Buoy_46211_3": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_names": ["Buoy_46211/46211h{0}.txt".format(year) for year in range(2007,2018)]+["Buoy_46211/46211{0}2018.txt".format(n) for n in range(1,10)],
            "file_type": "NBDC",
            "lat":47,  "lon":-124,
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
        "Buoy_46099": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_names": ["Buoy_46099/46099h{0}.txt".format(year) for year in range(2016,2018)]+["Buoy_46099/46099{0}2018.txt".format(n) for n in [1,3,4,5,6,7,8,9]],
            "file_type": "NBDC",
            "lat":46.986,  "lon":-124.566,
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
        "Station_WPTW1": { #Note that there may be a change in vis distance for NDBC data between 2007 and 2015 from nmi to mi. This buoy doesn't measure vis, so it's not a concern here.
            "file_names": ["Station_WPTW1/wptw1h{0}.txt".format(year) for year in range(2008,2018)]+["Station_WPTW1/wptw1{0}2018.txt".format(n) for n in range(1,10)],
            "file_type": "NBDC",
            "lat":47,  "lon":-124,
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
    },


    "merges": {
        "Bowerman_Airport": {
            "list_of_stations": ["Bowerman_Airport"],
            "merge_type":'single',
            "lat":46.9727, "lon":-123.9302,
            "UTM_offset": 0,
            "models": "All"
        },
        "Buoy_46211": {
            "list_of_stations": ["Buoy_46211_1","Buoy_46211_2","Buoy_46211_3"],
            "merge_type":'single',
            "lat":47,  "lon":-124,
            "UTM_offset": 0,
            "models": "All",
        },
        "Buoy_46099": {
            "list_of_stations": ["Buoy_46099"],
            "merge_type":'single',
            "lat":46.986,  "lon":-124.566,
            "UTM_offset": 0,
            "models": "All",
        },
        "Station_WPTW1": {
            "list_of_stations": ["Station_WPTW1"],
            "merge_type":'single',
            "lat":47,  "lon":-124,
            "UTM_offset": 0,
            "models": "All"
        }
    }
}

