from model_functions3 import *
from convert_functions3 import *

#Components

exclude_night = {'day':{
    'name':'exclude_night',
    'type':'day',
    'tactics':['Nice_temperature_day'],
    'obs':('day',),
    'logic': def_exclude_night,
    'params':()
}}

Nice_Temperatures = {'temp':{
    'name':'Nice_Temberatures',
    'type':'cold',
    'tactics':['Nice','Nice_temperature_day'],
    'obs':('temp',),
    'logic':def_reverse_simpleGYR,
    'params':(temperature(60,'F'),temperature(45,'F'))
}}

Nice_Wind = {'wind':{
    'name':'Nice_Wind',
    'type':'wind',
    'tactics':['Nice','Nice_temperature_day'],
    'obs':('wind',),
    'logic':def_simpleGYR,
    'params':(velocity(10,'MPH'),velocity(20,'MPH'))
}}

component_list = [
    exclude_night,
    Nice_Temperatures,
    Nice_Wind
]

#RGAs
def gen_tactics(comp_list):
    tactic_coponents = {}
    for component in comp_list:
        for kind in component.values():
            for tactic in kind['tactics']:
                try: tactic_coponents[tactic].append(component)
                except KeyError: tactic_coponents.update([(tactic,[component])])
    tactics = {}
    for tactic, components in tactic_coponents.iteritems():
        tactics.update([(
            tactic,
            append_dicts(components)
        )])
    return tactics

primary_RGAs = gen_tactics(component_list)

def gen_components(comp_list):
    components = {}
    for component in comp_list:
        for kind in component.values():
            components.update([(kind['name'],component)])

    return components

component_RGAs = gen_components(component_list)
primary_RGA_list = [key for key in primary_RGAs]

component_RGA_list = [key for key in component_RGAs]
multi_cycle_dict = {'main':primary_RGA_list}
for component_tactic in component_list:
    for component in component_tactic.values():
        try: multi_cycle_dict[component['type']].append(component['name'])
        except KeyError: multi_cycle_dict.update([(component['type'],[component['name']])])


#print multi_cycle_dict
#print multi_cycle_dict_legacy

inverse_multi_cycle_keys = {}
for key,list_stuff in multi_cycle_dict.iteritems():
    for individual in list_stuff:
        try: inverse_multi_cycle_keys[individual].append(key)
        except KeyError: inverse_multi_cycle_keys.update([(individual,[key])])

all_RGAs = primary_RGA_list + component_RGA_list

raw_model_dict = append_dicts([primary_RGAs, component_RGAs])
