from generate_HWITW_stats import (
    do_temp_dp,
    do_wind,
    do_precip,
    do_cloud_cover
)
from gen_extra_stats import (
    do_runoff,
    do_drought,
    do_ocean_temp,
    do_waves,
    do_cloud_ceiling
)

# the variables we are interested, long name and short name.
# short name is used inside the netcdf files
CDSVAR_U10 =   ['10m_u_component_of_wind', 'u10']
CDSVAR_V10 =   ['10m_v_component_of_wind', 'v10']
CDSVAR_D2M =   ['2m_dewpoint_temperature', 'd2m']
CDSVAR_T2M =   ['2m_temperature', 't2m']
CDSVAR_CBH =   ['cloud_base_height', 'cbh']
CDSVAR_PTYPE = ['precipitation_type', 'ptype']
CDSVAR_TCC =   ['total_cloud_cover', 'tcc']
CDSVAR_TP =    ['total_precipitation', 'tp']
CDSVAR_RO =    ['runoff', 'ro']
CDSVAR_PEV =   ['potential_evaporation', 'pev']
CDSVAR_E =     ['evaporation', 'e'] #Check to make sure "ev" is correct
CDSVAR_HMAX =  ['maximum_individual_wave_height', 'hmax']
CDSVAR_SWH =   ['significant_height_of_combined_wind_waves_and_swell', 'swh']
CDSVAR_PP1D =  ['peak_wave_period', 'pp1d']
CDSVAR_SST =   ['sea_surface_temperature', 'sst']

all_variables = [CDSVAR_U10, CDSVAR_V10, CDSVAR_D2M, CDSVAR_T2M, CDSVAR_CBH, CDSVAR_PTYPE, CDSVAR_TCC, CDSVAR_TP, CDSVAR_RO, CDSVAR_E, CDSVAR_PEV, CDSVAR_HMAX, CDSVAR_SWH, CDSVAR_PP1D, CDSVAR_SST]

data_groups = {
    'temperature_and_humidity': {'files': [CDSVAR_T2M, CDSVAR_D2M], 'analyze': do_temp_dp, 'sub_vars':['temperature','relative_humidity']},
    'wind': {'files': [CDSVAR_U10, CDSVAR_V10], 'analyze': do_wind, 'sub_vars':['wind']},
    'precipitation': {'files': [CDSVAR_TP, CDSVAR_PTYPE], 'analyze': do_precip, 'sub_vars':['precipitation']},
    'cloud_cover': {'files': [CDSVAR_TCC], 'analyze': do_cloud_cover, 'sub_vars':['cloud_cover']},
    'cloud_ceiling': {'files': [CDSVAR_CBH], 'analyze': do_cloud_ceiling, 'sub_vars':['cloud_ceiling']},
    'runoff':{'files': [CDSVAR_RO], 'analyze': do_runoff, 'sub_vars':['runoff']},
    'drought':{'files':[CDSVAR_PEV, CDSVAR_E, CDSVAR_TP], 'analyze': do_drought, 'sub_vars':['drought']},
    'waves':{'files':[CDSVAR_HMAX, CDSVAR_SWH, CDSVAR_PP1D], 'analyze': do_waves, 'sub_vars':['waves']},
    'ocean_temperature':{'files':[CDSVAR_SST], 'analyze':do_ocean_temp, 'sub_vars':['ocean_temperature']}
}