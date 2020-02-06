from model_functions3 import *
from convert_functions3 import *

#constants
ice_wave_limit = 0.33  #Above this proportion ice cover, we assume no waves form


#limit model components
vessel_vis = {'vis':{
    'obs':('vis','day'),
    'logic':def_reverse_GYR_plus_bool,
    'params':(vis_distance(0.5,"NMi"), vis_distance(0.125,"NMi"), vis_distance('infinite', None), vis_distance(0.5,"NMi"))
}}

air_vis_night_ok = {
    'vis':{
        'obs':('vis',),
        'logic':def_reverse_simpleGYR,
        'params':(vis_distance(1,"NMi"), vis_distance(0.5,"NMi"))
    },
    'ceil':{
        'obs':('ceil',),
        'logic':def_reverse_simpleGYR,
        'params':(vis_distance(1200,'feet'),vis_distance(500,'feet'))
    }

}

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

burn_air_vis = {
    'vis':{
        'obs':('vis','day'),
        'logic':def_reverse_GYR_plus_bool,
        'params':(vis_distance(1,"NMi"), vis_distance(0.5,"NMi"), vis_distance('infinite', None), vis_distance('infinite', None))
    },
    'ceil':{
        'obs':('ceil',),
        'logic':def_reverse_simpleGYR,
        'params':(vis_distance(1500,'feet'),vis_distance(800,'feet'))
    }
}

vessel_cold = {
    'wind_chill':{'obs':('wind_chill',),'logic': def_reverse_simpleGYR, 'params':(temperature(-25,'F'),temperature(-35,'F'))},
    'vessel_icing':{'obs': ('icing_cat',),'logic': def_categorical_GYR, 'params':(['no_icing','light'],['moderate'],['heavy','extreme'])}
}

air_cold = {'temp':{'obs':('temp',),'logic':def_reverse_simpleGR,'params':(-40,)}}

OW_wind_wave = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(20,'knots'),velocity(30,'knots'))
    },
    'wave':{
        'obs':('wave','steep'),
        'logic': def_steepness_cludge,
        'params':(0.0025, wave_height(3,'ft'), wave_height(4,'ft'), wave_height(6,'ft'), wave_height(8,'ft'))
    }
}

OW_wind_no_waves = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(20,'knots'),velocity(30,'knots'))
    }
}

OW_wind_wave_all_steep = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(20,'knots'),velocity(30,'knots'))
    },
    'wave':{
        'obs':('wave',),
        'logic': def_simpleGYR,
        'params':(wave_height(3,'ft'), wave_height(6,'ft'))
    }
}

boom_wind_median = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(8,'knots'),velocity(15,'knots'))
    }
}

dispersant_wind_wave_artificial_agitation = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(22,'knots'),velocity(30,'knots'))
    },
    'wave':{
        'obs':('wave',),
        'logic': def_simpleGR,
        'params':(wave_height(9,'ft'),)
    }
}

dispersant_wind_artificial_agitation_median = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGR,
        'params':(velocity(20,'knots'),)
    }
}

dispersant_wind_wave_natural_agitation = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(22,'knots'),velocity(30,'knots'))
    },
    'wave':{
        'obs':('wave',),
        'logic': def_dispersant_wave_cludge,
        'params':(wave_height(1, 'ft'), wave_height(2, 'ft'), wave_height(9,'ft'))
    }
}

dispersant_wind_natural_agitation_median = {
    'wind':{
        'obs':('wind','ice'),
        'logic':def_GYR_x_threshold,
        'params':(velocity(20,'knots'), velocity(20,'knots'), ice_wave_limit, velocity(22, 'knots'), velocity(30,'knots'))}
}


burning_wind_wave = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(15,'knots'),velocity(20,'knots'))
    },
    'wave':{
        'obs':('wave',),
        'logic': def_simpleGYR,
        'params':(wave_height(3,'ft'), wave_height(6,'ft'))
    }
}


new_burning_wind_wave = {
    'wind':{
        'obs':('wind',),
        'logic': def_simpleGYR,
        'params':(velocity(10,'knots'),velocity(20,'knots'))
    },
    'wave':{
        'obs':('wave',),
        'logic': def_simpleGYR,
        'params':(wave_height(3,'ft'), wave_height(6,'ft'))
    }
}


burning_wind_median = {
    'wind':{
        'obs':('wind','ice'),
        'logic':def_GYR_x_threshold,
        'params':(velocity(8,'knots'), velocity(10,'knots'), ice_wave_limit, velocity(10, 'knots'), velocity(20,'knots'))}
}

new_air_burning_wind_median = {
    'wind':{
        'obs':('wind','ice'),
        'logic':def_GYR_x_threshold,
        'params':(velocity(8,'knots'), velocity(10,'knots'), ice_wave_limit, velocity(10, 'knots'), velocity(20,'knots'))}
}


boom_ice = { #Can you deploy a boom for concentrating oil?
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, 0.3)
    }
}


dispersant_ice_air_artificial_agitation = {
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, 0.5)
    }
}


dispersant_ice_air_natural_agitation = {
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, ice_wave_limit)
    }
}


dispersant_ice_vessel_artificial_agitation = {
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, 0.9)
    }
}


dispersant_ice_vessel_natural_agitation = {
    'ice':{
        'obs':('ice',),
        'logic': def_simpleGYR,
        'params':(0.1, ice_wave_limit)
    }
}

burn_ice = {
    'ice':{
        'obs':('ice',),
        'logic':def_humpGRG,
        'params':(0.1, 0.9)
    }
}

new_air_burn_ice = {
    'ice':{
        'obs':('ice',),
        'logic':def_YGR,
        'params':(.7, 0.96)
    }
}


exclude_wave_gaps = {'wavetest':{'obs': ('wave',), 'logic': def_exclude_var_gap, 'params':()}}

exclude_night = {'day':{'obs':('day',), 'logic': def_exclude_night, 'params':()}}


#RGAs

RGAs_with_waves = {
    "OW":append_dicts([
        vessel_vis,
        vessel_cold,
        OW_wind_wave,
        boom_ice
    ]),
    "OW_all_steep":append_dicts([
        vessel_vis,
        vessel_cold,
        OW_wind_wave_all_steep,
        boom_ice
    ]),
    "dispersant_vessel_artificial_agitation":append_dicts([
        vessel_vis,
        vessel_cold,
        dispersant_wind_wave_artificial_agitation,
        dispersant_ice_vessel_artificial_agitation,
    ]),
    "dispersant_vessel_natural_agitation":append_dicts([
        vessel_vis,
        vessel_cold,
        dispersant_wind_wave_natural_agitation,
        dispersant_ice_vessel_natural_agitation
    ]),
    "dispersant_aerial_artificial_agitation":append_dicts([
        air_vis,
        air_cold,
        dispersant_wind_wave_artificial_agitation,
        dispersant_ice_air_artificial_agitation
    ]),
    "dispersant_aerial_natural_agitation":append_dicts([
        air_vis,
        air_cold,
        dispersant_wind_wave_natural_agitation,
        dispersant_ice_air_natural_agitation
    ]),
    "burn_aerial":append_dicts([
        burn_air_vis,
        vessel_cold,
        burning_wind_wave,
        burn_ice
    ]),
    "burn_vessel":append_dicts([
        vessel_vis,
        vessel_cold,
        burning_wind_wave,
        burn_ice
    ]),
    "burn_aerial_new":append_dicts([
        burn_air_vis,
        air_cold,
        new_burning_wind_wave,
        new_air_burn_ice
    ]),
    "burn_vessel_new":append_dicts([
        vessel_vis,
        vessel_cold,
        new_burning_wind_wave,
        boom_ice
    ])
}


RGAs_without_waves = {
    "OW_median":append_dicts([
        vessel_vis,
        vessel_cold,
        boom_wind_median,
        boom_ice
    ]),
    "dispersant_vessel_artificial_agitation_median":append_dicts([
        vessel_vis,
        vessel_cold,
        dispersant_wind_artificial_agitation_median,
        dispersant_ice_vessel_artificial_agitation
    ]),
    "dispersant_vessel_natural_agitation_median":append_dicts([
        vessel_vis,
        vessel_cold,
        dispersant_wind_natural_agitation_median,
        dispersant_ice_vessel_natural_agitation
    ]),
    "dispersant_aerial_artificial_agitation_median":append_dicts([
        air_vis,
        air_cold,
        dispersant_wind_artificial_agitation_median,
        dispersant_ice_air_artificial_agitation
    ]),
    "dispersant_aerial_natural_agitation_median":append_dicts([
        air_vis,
        air_cold,
        dispersant_wind_natural_agitation_median,
        dispersant_ice_air_natural_agitation
    ]),
    "burn_aerial_median_new":append_dicts([
        burn_air_vis,
        air_cold,
        new_air_burning_wind_median,
        new_air_burn_ice
    ]),
    "burn_vessel_median_new":append_dicts([
        vessel_vis,
        vessel_cold,
        boom_wind_median,
        boom_ice
    ])
}

component_RGAs = {
    "air_vis_night_ok":air_vis_night_ok,
    "vessel_vis":vessel_vis,
    "air_vis":air_vis,
    "burn_air_vis":burn_air_vis,
    "vessel_cold":vessel_cold,
    "air_cold":air_cold,
    "OW_wind_wave":OW_wind_wave,
    "OW_wind_no_waves":OW_wind_no_waves,
    "OW_wind_wave_all_steep":OW_wind_wave_all_steep,
    "boom_wind_median":boom_wind_median,
    "new_air_burning_wind_median":new_air_burning_wind_median,
    "boom_ice":boom_ice,
    "dispersant_wind_wave_artificial_agitation":dispersant_wind_wave_artificial_agitation,
    "dispersant_wind_wave_natural_agitation":dispersant_wind_wave_natural_agitation,
    "dispersant_wind_artificial_agitation_median":dispersant_wind_artificial_agitation_median,
    "dispersant_wind_natural_agitation_median":dispersant_wind_natural_agitation_median,
    "dispersant_ice_vessel_artificial_agitation":dispersant_ice_vessel_artificial_agitation,
    "dispersant_ice_vessel_natural_agitation":dispersant_ice_vessel_natural_agitation,
    "dispersant_ice_air_artificial_agitation":dispersant_ice_air_artificial_agitation,
    "dispersant_ice_air_natural_agitation":dispersant_ice_air_natural_agitation,
    "burning_wind_wave":burning_wind_wave,
    "burning_wind_median":burning_wind_median,
    "burn_ice":burn_ice,
    "new_air_burn_ice":new_air_burn_ice
}

official_15_list = [key for key in RGAs_without_waves] + [key for key in RGAs_with_waves]
RGAs_without_waves_list = [key for key in RGAs_without_waves]
component_RGAs_list = [key for key in component_RGAs]

wavetest = append_dicts([ #Makes a set of 15 more RGAs that will only calculate a response gap if there is wave data (regardless of whether it's otherwise required)
    {key+" wavetest":mod_dict(value,exclude_wave_gaps,[]) for key,value in RGAs_without_waves.iteritems()},
    {key+" wavetest":mod_dict(value,exclude_wave_gaps,[]) for key,value in RGAs_with_waves.iteritems()}
])

wavetest_list = [key for key in wavetest]

all_RGAs = official_15_list + RGAs_without_waves_list + component_RGAs_list + wavetest_list

raw_model_dict = append_dicts([RGAs_without_waves, RGAs_with_waves, wavetest, component_RGAs])
