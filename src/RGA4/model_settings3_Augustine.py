from model_functions3 import *
from convert_functions3 import *

#Components

exclude_night = {'day':{'obs':('day',), 'logic': def_exclude_night, 'params':()}}

Nice_Temperatures = {'temp':{
    'obs':('temp',),
    'logic':def_reverse_simpleGYR,
    'params':(temperature(60,'F'),temperature(45,'F'))
}}

Nice_Wind = {'wind':{
    'obs':('wind',),
    'logic':def_simpleGYR,
    'params':(velocity(10,'MPH'),velocity(20,'MPH'))
}}

#RGAs

primary_RGAs = {
    'Nice':append_dicts([
        Nice_Temperatures,
        Nice_Wind
    ]),
    'Nice_temperature_in_day':append_dicts([
        Nice_Temperatures,
        exclude_night
    ])
}


component_RGAs = {
    "Nice_Temperatures":Nice_Temperatures,
    "Nice_Wind":Nice_Wind
}

primary_RGA_list = [key for key in primary_RGAs]

component_RGA_list = [key for key in component_RGAs]

all_RGAs = primary_RGA_list + component_RGA_list

raw_model_dict = append_dicts([primary_RGAs, component_RGAs])
