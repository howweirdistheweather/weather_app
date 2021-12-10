# HWITW Copyright (C) 2021
#
# a class to contain HWITW processed output data

import json
import sys

def sizeof(obj):
    size = sys.getsizeof(obj)
    if isinstance(obj, dict): return size + sum(map(sizeof, obj.keys())) + sum(map(sizeof, obj.values()))
    if isinstance(obj, (list, tuple, set, frozenset)): return size + sum(map(sizeof, obj))
    return size

WEEKS_PER_YEAR = 52
TOTAL_NUM_LAT  = 721        # number of 1/4 degree latitude entries expected
TOTAL_NUM_LONG = 1440       # ..and 1/4 degree longitude entries

# Names of Processed Outputs
HWX_TEMP_AVG       = 'temperature_avg'
HWX_TEMP_AVG_N     = 'temperature_avg_night'
HWX_TEMP_AVG_D     = 'temperature_avg_day'
HWX_CEILING_AVG    = 'ceiling_avg'

HWX_VARIABLES = [
    HWX_TEMP_AVG,
    HWX_TEMP_AVG_N,
    HWX_TEMP_AVG_D,
    HWX_CEILING_AVG,
]

# dictionary to sorted list
def dict_to_slist( src_dict:dict ):
    result = [src_dict[key] for key in sorted(src_dict.keys())]
    return result

# class to contain all statistics for 1 week for 1 location
class HWXStats:
    
    def __init__( self ):
        self.temp_avg:float     = None
        self.temp_avg_n:float   = None
        self.temp_avg_d:float   = None
        self.ceiling_avg:float  = None
    
    def merge( self, hstat:'HWXStats' ):
        if hstat.temp_avg       != None: self.temp_avg      = hstat.temp_avg
        if hstat.temp_avg_n     != None: self.temp_avg_n    = hstat.temp_avg_n
        if hstat.temp_avg_d     != None: self.temp_avg_d    = hstat.temp_avg_d
        if hstat.ceiling_avg    != None: self.ceiling_avg   = hstat.ceiling_avg

# class to contain weekly data for 1 year for 1 location
class HWXWeeklyData:

    def __init__( self ):
        self.Weeks = [HWXStats() for i in range(WEEKS_PER_YEAR)]

    def set_week( self, week:int, hstat:HWXStats ):
        self.Weeks[ week ].merge( hstat )


# A class to contain all processed output statistics for a single location
class HWXLocation:

    def __init__( self ):
        self.WXStats:list = []
        self.TempAvg:dict = {}
        self.TempAvgNight:dict = {}
        self.TempAvgDay:dict = {}
        self.CeilingAvg:dict = {}
        self.CloudCoverAvg:dict = {}
        self.PrecipAvg:dict = {}
        pass

    def hide__merge( self, hpo_in ):
        self.TempAvg.update( hpo_in.TempAvg )
        self.TempAvgNight.update( hpo_in.TempAvgNight )
        self.TempAvgDay.update( hpo_in.TempAvgDay )
        self.CeilingAvg.update( hpo_in.CeilingAvg )

    @staticmethod
    def set_weekly( d_y:dict, year:int, week:int, x:float ):        
        if x is None:
            return
        if year not in d_y.keys():
            d_y[year] = HWXWeeklyData()
            
        d_y[year].set_week( week, x )

    def set( self, year:int, week:int, hstat:HWXStats ):
        HWXLocation.set_weekly( self.TempAvg,      year, week, hstat.temp_avg )
        HWXLocation.set_weekly( self.TempAvgNight, year, week, hstat.temp_avg_n )
        HWXLocation.set_weekly( self.TempAvgDay,   year, week, hstat.temp_avg_d )
        HWXLocation.set_weekly( self.CeilingAvg,   year, week, hstat.ceiling_avg )

    # put everything in a JSON-able dictionary and return it
    def get_jsondict( self ):
        # get start year from tempavg. assuming it is the same for all statistics
        # ..and that years are contiguous.
        assert len(self.TempAvg) > 0

    def add_ceiling_avg( self, year:int, weekly_ca:list ):
        self.CeilingAvg[year] = weekly_ca

    def add_cloud_cover_avg(self, year:int, weekly_cca:list):
        self.CloudCoverAvg[year] = weekly_cca

    def add_precip_avg(self, year:int, weekly_pa:list):
        self.PrecipAvg[year] = weekly_pa
    
    def get_jodict( self ):
        # get start year from tempavg. assume its the same for all!
        start_year = sorted(self.TempAvg.keys())[0]

        # convert weather variable data to 'python list of lists'
        temp_avg = dict_to_slist( self.TempAvg )
        temp_avg_n = dict_to_slist( self.TempAvgNight )
        temp_avg_d = dict_to_slist( self.TempAvgDay )
        ceiling_avg = dict_to_slist( self.CeilingAvg )
        cloud_cover_avg = dict_to_slist( self.CloudCoverAvg)
        precip_avg = dict_to_slist( self.PrecipAvg )
        
        # put it together like this for the purpose of doing some json output
        jdict = {
            'data_specs':{
                'start_year':start_year
            },
            'data':{
                'temperature':{
                    'avg':temp_avg,
                    'avg_n':temp_avg_n,
                    'avg_d':temp_avg_d,
                },
                'ceiling':{
                    'avg':ceiling_avg,
                },
                'cloud cover':{
                    'avg':cloud_cover_avg,
                },
                'precipitation':{
                    'avg':precip_avg,
                }
            }
        }

        return jdict


# A class to contain array of hwx processed output for whole planet for 1 year
class HWXGlobal:

    def __init__( self, year:int ):
        self.Year = year
        self.LocArray = [[HWXWeeklyData() for i in range(TOTAL_NUM_LONG)] for j in range( TOTAL_NUM_LAT )]

    def merge_stat( self, hstat:HWXStats, lat_idx:int, long_idx:int, week_idx:int ):
        # merge one-week-one-location into array
        self.LocArray[ lat_idx ][ long_idx ].set_week( week_idx, hstat )
        
    def merge( self, hg:'HWXGlobal' ):
        print( 'nothing here yet!' )
