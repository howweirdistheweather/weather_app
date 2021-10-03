# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
import sys
import io
import re
import json
import random
import statistics
import math
import pandas as pd
import numpy as np


# from potile.py:
# Processed Output for Tiles
POT_TEMP_AVG       = 'temperature_avg'
POT_TEMP_AVG_N     = 'temperature_avg_night'
POT_TEMP_AVG_D     = 'temperature_avg_day'

POT_VARIABLES = [
    POT_TEMP_AVG,
    POT_TEMP_AVG_N,
    POT_TEMP_AVG_D
]


def get_wxvar_list():
    return POT_VARIABLES

def get_wxvar( var_name:str, var_lat:float, var_long:float ):
    with open( 'gn862673-temp_avg.json', 'r') as infile:        
        wxvar_json = infile.read()
        infile.close()
    return wxvar_json
