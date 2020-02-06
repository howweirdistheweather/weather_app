from model_functions3 import *
from convert_functions3 import *

#Components

W_M = {'wind':{
        'name':'W_M',
        'type':'wind',
        'tactics':['MEC_recovery'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 20 knots; Red >= 30 knots',)
}}
W_DSP_IS_RP = {'wind':{
        'name':'W_DSP_IS_RP',
        'type':'wind',
        'tactics':['DISP_ship','DISP_plane', 'ISB_ship','RS_plane'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green < 22 knots; Red >= 27 knots',)
}}
W_Heli = {'wind':{
        'name':'W_Heli',
        'type':'wind',
        'tactics':['DISP_heli','ISB_heli','RS_heli'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green < 28 knots; Red >= 28 knots',)
}}
W_IP = {'wind':{
        'name':'W_IP',
        'type':'wind',
        'tactics':['ISB_plane'],
        'obs':('wind',),
        'logic': def_return_complex_inequality,
        'params':('Green < 15 knots; Red >= 20 knots',)
}}
H_M = {'wave':{
        'name':'H_M',
        'type':'wave',
        'tactics':['MEC_recovery'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green <= 3 ft; Red >= 6 ft',)
}}
H_D_IS_RP = {'wave':{
        'name':'H_D_IS_RP',
        'type':'wave',
        'tactics':['DISP_ship', 'DISP__plane', 'DISP_heli', 'ISB_ship', 'RS_plane'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green < 9 ft; Red >= 9 ft',)
}}
H_IPH_RH = {'wave':{
        'name':'H_IPH_RH',
        'type':'wave',
        'tactics':['ISB_plane', 'ISB_heli', 'RS_heli'],
        'obs':('wave',),
        'logic': def_return_complex_inequality,
        'params':('Green < 3 ft; Red >= 6 ft',)
}}
Vh_M_Ship = {'vis':{
        'name':'Vh_M_Ship',
        'type':'vis',
        'tactics':['MEC_recovery', 'DISP_ship', 'ISB_ship'],
        'obs':('vis','day'),
        'logic': def_GYR_plus_day_GOM,
        'params':(smart_units('0.5 nmi'), smart_units('0.125 nmi'), smart_units('0.5 nmi'))
}}
Vh_Plane = {'vis':{
        'name':'Vh_Plane',
        'type':'vis',
        'tactics':['DISP_plane', 'ISB_plane', 'RS_plane'],
        'obs':('vis', 'day'),
        'logic': def_RYG_GOM,
        'params':(smart_units('0.5 nmi'), smart_units('1 nmi'))
}}
Vh_Heli = {'vis':{
        'name':'Vh_Heli',
        'type':'vis',
        'tactics':['DISP_heli', 'ISB_heli', 'RS_heli'],
        'obs':('vis','day'),
        'logic': def_GR_GOM,
        'params':(smart_units('3 miles'),)
}}
Vv_DP_RP = {'ceil':{
        'name':'Vv_DP_RP',
        'type':'vis',
        'tactics':['DISP_plane', 'RS_plane'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green > 1200 ft; Red <= 500 ft',)
}}
Vv_Heli = {'ceil':{
        'name':'Vv_Heli',
        'type':'vis',
        'tactics':['DISP_heli', 'ISB_heli', 'RS_heli'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green > 600 ft; Red <= 600 ft',)
}}
Vv_IP = {'ceil':{
        'name':'Vv_IP',
        'type':'vis',
        'tactics':['ISB_plane'],
        'obs':('ceil',),
        'logic': def_return_complex_inequality,
        'params':('Green > 1500 ft; Red <= 800 ft',)
}}
# FOR ALL GREEN SCENARIOS
#Vv_M_Ship = {'ceil':{
#        'name':'Vv_M_Ship',
#        'type':'vis',
#        'tactics':['MEC_recovery', 'DISP_ship', 'ISB_ship'],
#        'obs':('ceil',),
#        'logic': #Needs a function,
#        'params': ('Green',)
#}}
#S_D= {'sal':{
#        'name':'S_D',
#        'type':'sal',
#        'tactics':['DISP_ship', 'DISP_plane', 'DISP_heli'],
#        'obs':('sal',),
#        'logic': def_RYGYR_GOM,
#        'params':(12, 25, 55, 75)
#}}
#FOR ALL GREEN SCENARIOS
#S_M_I_R= {'sal':{
#        'name':'S_M_I_R',
#        'type':'sal',
#        'tactics':['MEC_recovery', 'ISB_ship', 'ISB__plane', 'ISB_heli', 'RS_plane', 'RS_heli'],
#        'obs':('sal',),
#        'logic': #Needs a function,
#        'params': ('Green',)
#}}

component_list = [
    W_M,
    W_DSP_IS_RP,
    W_Heli,
    W_IP,
    H_M,
    H_D_IS_RP,
    H_IPH_RH,
    Vh_M_Ship,
    Vh_Plane,
    Vh_Heli,
    Vv_DP_RP,
    Vv_Heli,
    Vv_IP,
#    S_D,
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