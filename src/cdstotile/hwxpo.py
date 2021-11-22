# HWITW Copyright (C) 2021
#
# a class to contain processed output data

import json

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


class HWXPO:

    def __init__( self ):
        self.TempAvg:dict = {}
        self.TempAvgNight:dict = {}
        self.TempAvgDay:dict = {}
        self.CeilingAvg:dict = {}
        self.CloudCoverAvg:dict = {}
        self.PrecipAvg:dict = {}
        pass


    def add_temp_avg( self, year:int, weekly_ta:list ):
        self.TempAvg[year] = weekly_ta
        
    def add_temp_avg_n( self, year:int, weekly_tan:list ):
        self.TempAvgNight[year] = weekly_tan
        
    def add_temp_avg_d( self, year:int, weekly_tad:list ):
        self.TempAvgDay[year] = weekly_tad

    def add_ceiling_avg( self, year:int, weekly_ca:list ):
        self.CeilingAvg[year] = weekly_ca

    def add_cloud_cover_avg(self, year:int, weekly_cca:list):
        self.CloudCoverAvg[year] = weekly_cca

    def add_precip_avg(self, year:int, weekly_pa:list):
        self.PrecipAvg[year] = weekly_pa
    
    def get_jodict( self ):
        # get start year from tempavg. assume its the same for all!
        start_year = sorted(self.TempAvg.keys())[0]

        # convert weather variable data to 2D array. er... 'python list of lists'
        temp_avg = dict_to_slist( self.TempAvg )
        temp_avg_n = dict_to_slist( self.TempAvgNight )
        temp_avg_d = dict_to_slist( self.TempAvgDay )
        ceiling_avg = dict_to_slist( self.CeilingAvg )
        cloud_cover_avg = dict_to_slist( self.CloudCoverAvg)
        precip_avg = dict_to_slist( self.PrecipAvg )
        
        # put it together like this for the purpose of doing some json output
        jodict = {
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
        
        return jodict
        
        
