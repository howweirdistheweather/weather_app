from model_functions3 import *
from convert_functions3 import *

#Components

W_Boom_OWR = {'wind':{
        'name':'W_Boom_OWR',
        'type':'wind',
        'tactics':['MEC1'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 35 knots',)
}}
W_Boom_OW = {'wind':{
        'name':'W_Boom_OW',
        'type':'wind',
        'tactics':['MEC2'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 25 knots',)
}}


H_MEC1_2_ISB1 = {'wave':{
        'name':'H_MEC1',
        'type':'wave',
        'tactics':['MEC1', 'MEC2'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 3 ft; Red >= 6 ft',)
}}

L_Mec = {'day':{
        'name':'L_Mec',
        'type':'day',
        'tactics':['MEC1','MEC2'],
        'obs':('day',),
        'logic':def_dayGY,
        'params':()
}}


Vh_Mec = {'vis':{
        'name':'Vh_Mec',
        'type':'vis',
        'tactics':['MEC1','MEC2'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 0.5 nmi; Red <= 0.1 nmi',)
}}


component_list = [
    W_Boom_OWR,
    W_Boom_OW,
    H_MEC1_2_ISB1,
    L_Mec,
    Vh_Mec,
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