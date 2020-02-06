from model_functions3 import *
from convert_functions3 import *

#Components

W_Boom_OWR = {'wind':{
        'name':'W_Boom_OWR',
        'type':'wind',
        'tactics':['MEC1','MEC1c'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 35 knots',)
}}
W_Boom_OW = {'wind':{
        'name':'W_Boom_OW',
        'type':'wind',
        'tactics':['MEC2','MEC2c'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 33 knots',)
}}
W_MEC3_DISP2_3 = {'wind':{
        'name':'W_MEC3_DISP2_3',
        'type':'wind',
        'tactics':['MEC3','DISP2','DISP3','MEC3c','DISP2c','DISP3c'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 30 knots',)
}}
W_DISP1 = {'wind':{
        'name':'W_DISP1',
        'type':'wind',
        'tactics':['DISP1','DISP1c'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 21 knots; Red >= 39 knots',)
}}
W_ISB1 = {'wind':{
        'name':'W_ISB1',
        'type':'wind',
        'tactics':['ISB1','ISB1c'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 knots; Red >= 20 knots',)
}}

H_MEC1_2_ISB1 = {'wave':{
        'name':'H_MEC1_2_ISB1',
        'type':'wave',
        'tactics':['MEC1','MEC2','ISB1','MEC1c','MEC2c','ISB1c'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 3 ft; Red >= 6 ft',)
}}
H_MEC3 = {'wave':{
        'name':'H_MEC3',
        'type':'wave',
        'tactics':['MEC3','MEC3c'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 2 ft; Red >= 3 ft',)
}}
H_DISP1_2_3 = {'wave':{
        'name':'H_DISP1_2_3',
        'type':'wave',
        'tactics':['DISP1','DISP2','DISP3','DISP1c','DISP2c','DISP3c'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 ft; Red >= 16 ft',)
}}

L_Mec = {'day':{
        'name':'L_Mec',
        'type':'day',
        'tactics':['MEC1','MEC2','MEC3','DISP1','ISB1','MEC1c','MEC2c','MEC3c','DISP1c','ISB1c'],
        'obs':('day',),
        'logic':def_dayGY,
        'params':()
}}
L_Airc = {'day':{
        'name':'L_Airc',
        'type':'day',
        'tactics':['DISP2','DISP3','DISP2c','DISP3c'],
        'obs':('day',),
        'logic':def_dayGR,
        'params':()
}}


Vh_Mec = {'vis':{
        'name':'Vh_Mec',
        'type':'vis',
        'tactics':['MEC1','MEC2','MEC3','DISP1','ISB1','MEC1c','MEC2c','MEC3c','DISP1c','ISB1c'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 0.5 nmi; Red <= 0.1 nmi',)
}}
Vh_DISP2 = {'vis':{
        'name':'Vh_DISP2',
        'type':'vis',
        'tactics':['DISP2','DISP2c'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 3 nmi; Red < 1 nmi',)
}}
Vh_DISP3 = {'vis':{
        'name':'Vh_DISP3',
        'type':'vis',
        'tactics':['DISP3','DISP3c'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 1 nmi; Red < 0.5 nmi',)
}}

Vv_Mec = {'ceil':{
        'name':'Vv_Mec',
        'type':'vis',
        'tactics':['MEC1c','MEC2c','MEC3c','DISP1c','ISB1c'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 500 ft; Red <= 33 ft',)
}}
Vv_DISP2 = {'ceil':{
        'name':'Vv_DISP2',
        'type':'vis',
        'tactics':['DISP2c'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 5000 ft; Red <= 1000 ft',)
}}
Vv_DISP3 = {'ceil':{
        'name':'Vv_DISP3',
        'type':'vis',
        'tactics':['DISP3c'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 1000 ft; Red <= 500 ft',)
}}


component_list = [
    W_Boom_OWR,
    W_Boom_OW,
    W_MEC3_DISP2_3,
    W_DISP1,
    W_ISB1,
    H_MEC1_2_ISB1,
    H_MEC3,
    H_DISP1_2_3,
    L_Mec,
    L_Airc,
    Vh_Mec,
    Vh_DISP2,
    Vh_DISP3,
    Vv_Mec,
    Vv_DISP2,
    Vv_DISP3
]
'''
obs_adjustment_dict = {
    ('wind',):'1 m/s',
    ('wave',):'0.2 m',
    ('temp',):'-5 C'
}
new_components = []
modified_tactics = {}
for component in component_list:
    if len(component) == 1:
        for kind in component.values(): #There will only be one item in this loop
            if kind['obs'] in obs_adjustment_dict:
                print '.',
                new_component = copy.deepcopy(component)
                for new_kind in new_component.values():
                    print ',',
                    new_kind['name'] += '+' + kind['type']
                    #new_kind['tactics'] = []
                    for i,tactic in enumerate(new_kind['tactics']):
                        new_tactic = tactic + '+'+ kind['type']
                        new_kind['tactics'][i] = new_tactic
                        try: modified_tactics[tactic].append(new_tactic)
                        except KeyError: modified_tactics.update([(tactic,[new_tactic])])
                    new_kind['params'] = (kind['params'][0],obs_adjustment_dict[kind['obs']])
                    new_components.append(new_component)
        print new_component #DEBUG
    else: print "WARNING: multiple 'kind' component may confuse things."

for component in component_list:
    for kind in component.values():
        for tactic in kind['tactics']:
            if tactic in modified_tactics:
                kind['tactics'] += modified_tactics[tactic]
    print component
component_list += new_components
'''

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