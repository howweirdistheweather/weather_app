# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
##import sys
##import io
##import re
##import json
##import random
##import statistics
##import math
##import pandas as pd
##import numpy as np


########################
# from hpo.py:
# HWITW Processed Output
HPO_TEMP_AVG        ='temperature_avg'
HPO_TEMP_AVG_N      ='temperature_avg_night'
HPO_TEMP_AVG_D      ='temperature_avg_day'
HPO_CEILING_AVG     ='ceiling_avg'

HPO_VARIABLES = [
    HPO_TEMP_AVG,
    HPO_TEMP_AVG_N,
    HPO_TEMP_AVG_D,
    HPO_CEILING_AVG
]
#######################

def get_wxvar_list():
    return HPO_VARIABLES

def get_wxvar( var_lat, var_long ):
    with open( 'Puerto_Maldonado.json', 'r') as infile:
        wxvar_json = infile.read()
        infile.close()
    return wxvar_json
