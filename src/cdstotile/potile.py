# HWITW Copyright (C) 2021
#
# a class to contain processed output tile data

# Processed Output for Tiles
POT_TEMP_AVG       = 'temperature_avg'
POT_TEMP_AVG_N     = 'temperature_avg_night'
POT_TEMP_AVG_D     = 'temperature_avg_day'
#POT_SP_AVG     = 'surface_pressure_avg'
#POT_SP_MAX     = 'surface_pressure_max'
#POT_SP_MIN     = 'surface_pressure_min'

POT_VARIABLES = [
    POT_TEMP_AVG,
    POT_TEMP_AVG_N,
    POT_TEMP_AVG_D
#    POT_SP_AVG,
#    POT_SP_MIN,
#    POT_SP_MAX
]

class POTile:

    def __init__( self ):
        self.TempAvg:dict = {}        
        pass            

    def add_temp_avg( self, year:int, weekly_ta:list ):
        self.TempAvg[year] = weekly_ta

