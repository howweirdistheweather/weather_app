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
        self.CeilingAvg:dict = {}
        pass    


    def add_temp_avg( self, year:int, weekly_ta:list ):
        self.TempAvg[year] = weekly_ta

    def add_ceiling_avg( self, year:int, weekly_ca:list ):
        self.CeilingAvg[year] = weekly_ca
    
    def get_jodict( self ):
        # get start year from tempavg. assume its the same for all!
        start_year = sorted(self.TempAvg.keys())[0]

        # convert weather variable data to 2D array. er... 'python list of lists'
        temp_avg = dict_to_slist( self.TempAvg )
        ceiling_avg = dict_to_slist( self.CeilingAvg )
        
        # put it together like this for the purpose of doing some json output
        jodict = {
            'data_specs':{
                'start_year':start_year
            },
            'data':{
                'temperature':{
                    'avg':temp_avg,                    
                },
                'ceiling':{
                    'avg':ceiling_avg,
                }
                
            }
        }
        
        return jodict
        
        
