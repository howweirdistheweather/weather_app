from model_functions3 import *
from convert_functions3 import *

#Components

W_Boom_OWR = {'wind':{
        'name':'W_Boom_OWR',
        'type':'wind',
        'tactics':['MEC1'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 11 m/s; Red >= 18 m/s',)
}}
W_Boom_OW = {'wind':{
        'name':'W_Boom_OW',
        'type':'wind',
        'tactics':['MEC2'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 11 m/s; Red >= 17 m/s',)
}}
W_MEC3_DISP3 = {'wind':{
        'name':'W_MEC3_DISP3',
        'type':'wind',
        'tactics':['MEC3','DISP3'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 11 m/s; Red >= 15 m/s',)
}}
W_MEC4 = {'wind':{
        'name':'W_MEC4',
        'type':'wind',
        'tactics':['MEC4'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 15 m/s; Red >= 25 m/s',)
}}
W_DISP1 = {'wind':{
        'name':'W_DISP1',
        'type':'wind',
        'tactics':['DISP1'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 11 m/s; Red >= 20 m/s',)
}}
W_DISP2 = {'wind':{
        'name':'W_DISP2',
        'type':'wind',
        'tactics':['DISP2'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 13 m/s; Red >= 15 m/s',)
}}
W_ISB1_2 = {'wind':{
        'name':'W_ISB1_2',
        'type':'wind',
        'tactics':['ISB1','ISB2'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 5 m/s; Red >= 10 m/s',)
}}
W_ISB3 = {'wind':{
        'name':'W_ISB3',
        'type':'wind',
        'tactics':['ISB3'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 4 m/s; Red >= 6 m/s',)
}}

H_MEC1 = {'wave':{
        'name':'H_MEC1',
        'type':'wave',
        'tactics':['MEC1'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 1.8 m; Red >= 3 m',)
}}
H_MEC2_ISB2 = {'wave':{
        'name':'H_MEC2_ISB2',
        'type':'wave',
        'tactics':['MEC2','ISB2'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 0.9 m; Red >= 2 m',)
}}
H_MEC3 = {'wave':{
        'name':'H_MEC3',
        'type':'wave',
        'tactics':['MEC3'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 0.6 m; Red >= 1 m',)
}}
H_DISP1 = {'wave':{
        'name':'H_DISP1',
        'type':'wave',
        'tactics':['DISP1'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 2.7 m; Red >= 5 m',)
}}
H_DISP2_3 = {'wave':{
        'name':'H_DISP2_3',
        'type':'wave',
        'tactics':['DISP2','DISP3'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green < 3 m; Red >= 5 m',) #Note strict inequality for green
}}
H_ISB1 = {'wave':{
        'name':'H_ISB1',
        'type':'wave',
        'tactics':['ISB1'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 1 m; Red >= 2 m',)
}}

I_MEC1_2_DISP2_ISB1 = {'ice':{
        'name':'I_MEC1_2_DISP2_ISB1',
        'type':'ice',
        'tactics':['MEC1','MEC2','DISP2','ISB1'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 %; Red >= 30 %',)
}}
I_MEC3 = {'ice':{
        'name':'I_MEC3',
        'type':'ice',
        'tactics':['MEC3'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 %; Red >= 20 %',)
}}
I_MEC4 = {'ice':{
        'name':'I_MEC4',
        'type':'ice',
        'tactics':['MEC4'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 90 %; Red < 70 %',)
}}
I_DISP1 = {'ice':{
        'name':'I_DISP1',
        'type':'ice',
        'tactics':['DISP1'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 %; Red >= 70 %',)
}}
I_DISP3 = {'ice':{
        'name':'I_DISP3',
        'type':'ice',
        'tactics':['DISP3'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 10 %; Red >= 50 %',)
}}
I_ISB2 = {'ice':{
        'name':'I_ISB2',
        'type':'ice',
        'tactics':['ISB2'],
        'obs':('ice',),
        'logic': def_RYGYR_ISB2,
        'params':(0.6, 0.7, 0.9, 0.95)
}}
I_ISB3 = {'ice':{
        'name':'I_ISB3',
        'type':'ice',
        'tactics':['ISB3'],
        'obs':('ice',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 30 %; Red >= 60 %',)
}}

L_Mec = {'day':{
        'name':'L_Mec',
        'type':'day',
        'tactics':['MEC1','MEC2','MEC3','MEC4','DISP1','ISB1'],
        'obs':('day',),
        'logic':def_dayGY,
        'params':()
}}
L_Airc = {'day':{
        'name':'L_Airc',
        'type':'day',
        'tactics':['DISP2','DISP3','ISB2','ISB3'],
        'obs':('day',),
        'logic':def_dayGR,
        'params':()
}}

Tsi_Mec = {'vessel_icing':{
        'name':'Tsi_Mec',
        'type':'cold',
        'tactics':['MEC1','MEC2','MEC3','MEC4','DISP1','ISB1'],
        'obs': ('icing_cat',),
        'logic': def_categorical_GYR,
        'params':(['no_icing','light'],['moderate'],['heavy','extreme'])
}}

Vh_Mec = {'vis':{
        'name':'Vh_Mec',
        'type':'vis',
        'tactics':['MEC1','MEC2','MEC3','MEC4','DISP1','ISB1'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 0.9 km; Red <= 0.2 km',) #Non-strict inequality on red
}}
Vh_DISP2 = {'vis':{
        'name':'Vh_DISP2',
        'type':'vis',
        'tactics':['DISP2'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 5.6 km; Red < 1.9 km',)
}}
Vh_Airc = {'vis':{
        'name':'Vh_Airc',
        'type':'vis',
        'tactics':['DISP3','ISB2','ISB3'],
        'obs':('vis',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 1.9 km; Red < 0.7 km',)
}}

Vv_Mec = {'ceil':{
        'name':'Vv_Mec',
        'type':'vis',
        #'tactics':['MEC1','MEC2','MEC3','MEC4','DISP1','ISB1'],
        'tactics':[],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 152 m; Red <= 10 m',)
}}
Vv_DISP2 = {'ceil':{
        'name':'Vv_DISP2',
        'type':'vis',
        #'tactics':['DISP2'],
        'tactics':[],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 1524 m; Red <= 305 m',)
}}
Vv_Airc = {'ceil':{
        'name':'Vv_Airc',
        'type':'vis',
        #'tactics':['DISP3','ISB2','ISB3'],
        'tactics':[],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green >= 305 m; Red <= 152 m',)
}}

Twc_Mec = {'wind_chill':{
        'name':'Twc_Mec',
        'type':'cold',
        'tactics':['MEC1','MEC2','MEC3','DISP1','ISB1'],
        'obs':('wind_chill',),
        'logic': def_return_complex_inequality,
        'params':('Green >= -31.7 C; Red <= -37.2 C',)
}}

T_Mec = {'temp':{
        'name':'T_Mec',
        'type':'cold',
        'tactics':['MEC1','MEC2','MEC3'],
        'obs':('temp',),
        'logic': def_return_complex_inequality,
        'params':('Green >= -5 C; Red <= -17.8 C',)
}}
T_DISP3_ISB2 = {'temp':{
        'name':'T_DISP3_ISB2',
        'type':'cold',
        'tactics':['DISP3','ISB2'],
        'obs':('temp',),
        'logic': def_return_complex_inequality,
        'params':('Green > -40 C; Red <= -40 C',)
}}
T_ISB3 = {'temp':{
        'name':'T_ISB3',
        'type':'cold',
        'tactics':['ISB3'],
        'obs':('temp',),
        'logic': def_return_complex_inequality,
        'params':('Green > -20 C; Red <= -20 C',)
}}

component_list = [
    W_Boom_OWR,
    W_Boom_OW,
    W_MEC3_DISP3,
    W_MEC4,
    W_DISP1,
    W_DISP2,
    W_ISB1_2,
    W_ISB3,
    H_MEC1,
    H_MEC2_ISB2,
    H_MEC3,
    H_DISP1,
    H_DISP2_3,
    H_ISB1,
    I_MEC1_2_DISP2_ISB1,
    I_MEC3,
    I_MEC4,
    I_DISP1,
    I_DISP3,
    I_ISB2,
    I_ISB3,
    L_Mec,
    L_Airc,
    Tsi_Mec,
    Vh_Mec,
    Vh_DISP2,
    Vh_Airc,
    Vv_Mec,
    Vv_DISP2,
    Vv_Airc,
    Twc_Mec,
    T_Mec,
    T_DISP3_ISB2,
    T_ISB3
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