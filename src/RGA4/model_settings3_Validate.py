from model_functions3 import *
from convert_functions3 import *

#constants
ice_wave_limit = 0.33  #Above this proportion ice cover, we assume no waves form

air_vis = {
    'vis':{
        'obs':('vis','day'),
        'logic':def_reverse_GYR_plus_bool,
        'params':(vis_distance(1,"NMi"), vis_distance(0.5,"NMi"), vis_distance('infinite', None), vis_distance('infinite', None))
    },
    'ceil':{
        'obs':('ceil',),
        'logic':def_reverse_simpleGYR,
        'params':(vis_distance(1200,'feet'),vis_distance(500,'feet'))
    }
}

air_cold = {'temp':{'obs':('temp',),'logic':def_reverse_simpleGR,'params':(-40,)}}

dispersant_wind_no_agitation_median = {
    'wind':{
        'obs':('wind','ice'),
        'logic':def_GYR_x_threshold,
        'params':(velocity(20,'knots'), velocity(20,'knots'), ice_wave_limit, velocity(22, 'knots'), velocity(30,'knots'))}
}


dispersants_ice_air_agitated = {
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, 0.5)
    }
}

#RGAs


RGAs_without_waves = {
    "dispersants_aerial_no_agitation_median":append_dicts([
        air_vis,
        air_cold,
        dispersant_wind_no_agitation_median,
        dispersants_ice_air_agitated
    ])
}

component_RGAs = {
    "air_vis":air_vis,
    "air_cold":air_cold,
    "dispersant_wind_no_agitation_median":dispersant_wind_no_agitation_median,
    "dispersants_ice_air_agitated":dispersants_ice_air_agitated
}

component_RGAs_list = [key for key in component_RGAs]
RGAs_without_waves_list = [key for key in RGAs_without_waves]

all_RGAs = component_RGAs_list + RGAs_without_waves_list

raw_model_dict = append_dicts([RGAs_without_waves, component_RGAs])
