from data_settings import *

extra_data_settings = {
    "data_specs": {

    },
    "compression": {
        "water_temperature":{
            "min":-10,
            "scale":0.2,
            "type":"linear",
            "units":"C"
        },
        "water_flux":{
            "scale":0.005,
            "type":"signed_parabolic",
            "units":"m"
        },
        "water_flux_sensitive":{
            "scale":0.0005,
            "type":"signed_parabolic",
            "units":"m"
        },
        "water_flux_very_sensitive":{
            "scale":0.0001,
            "type":"signed_parabolic",
            "units":"m"
        },
        "cloud_ceiling":{
            "min":0,
            "scale":30,
            "type":"linear",
            "units":"m"
        },
        "wave_height":{
            "min":0,
            "scale":0.1,
            "type":"linear",
            "units":"m"
        },
        "wave_period":{
            "min":0,
            "scale":0.1,
            "type":"linear",
            "units":"s"
        }
    },
    "variables": {
        "cloud_ceiling": {
            "p50": {
                "description": "",
                "long_name": "Median ceiling elevation",
                "short_name": "Median",
                "compression": "cloud_ceiling"
            },
            "min": {
                "description": "",
                "long_name": "Lowest ceiling elevation in any hour of the week",
                "short_name": "Lowest ceiling",
                "compression": "cloud_ceiling"
            },
            "p25": {
                "description": "",
                "long_name": "25th percentile ceiling elevation",
                "short_name": "25th percentile",
                "compression": "cloud_ceiling"
            },
            "p75": {
                "description": "",
                "long_name": "75th percentile ceiling elevation",
                "short_name": "75th percentile",
                "compression": "cloud_ceiling"
            },
            "max": {
                "description": "",
                "long_name": "Highest ceiling elevation in any hour of the week (clear is considered max height)",
                "short_name": "Highest ceiling",
                "compression": "cloud_ceiling"
            }
        },
        "runoff": {
            "total": {
                "description": "",
                "long_name": "Total surface and subsurface runoff through the week",
                "short_name": "Total runoff",
                "compression": "precipitation"
            },
            "p90": {
                "description": "",
                "long_name": "90th percentile high runoff",
                "short_name": "90th percentile",
                "compression": "precipitation_very_sensitive"
            },
            "max": {
                "description": "",
                "long_name": "Maximum single-hour runoff for the week",
                "short_name": "Maximum runoff",
                "compression": "precipitation_very_sensitive"
            }
        },
        "drought": {
            "potential_evaporation": {
                "description": "",
                "long_name": "Total potential evaporation through the week",
                "short_name": "Potential evaporation",
                "compression": "water_flux_sensitive"
            },
            "evaporation": {
                "description": "",
                "long_name": "Total estimated evaporation (takes into consideration water availability)",
                "short_name": "Estimated evaporation",
                "compression": "water_flux"
            },
            "p90": {
                "description": "",
                "long_name": "90th percentile extreme potential evaporation (typically negative)",
                "short_name": "90th percentile",
                "compression": "water_flux_very_sensitive"
            },
            "max": {
                "description": "",
                "long_name": "Greatest single-hour potential evaporation for the week (typically negative)",
                "short_name": "Maximum",
                "compression": "water_flux_very_sensitive"
            },
            "P-PET": {
                "description": "This is one common measure of drought stress, calculated as the amount of precipitation "
                               "reduced by the amount of potential evaporation. For this calculation, the difference is "
                               "calculated for each hour, then summed. Since negative PET denotes evaporation, "
                               "this difference is actually the sum.",
                "long_name": "cumulative discrepancy between precipitation and (potential) evaporation.",
                "short_name": "P-PET drought metric",
                "compression": "water_flux"
            }
        },
        "ocean_temp": {
            "avg": {
                "description": "",
                "long_name": "Average ocean temperature over the week",
                "short_name": "Average",
                "compression": "water_temperature"
            },
            "max": {
                "description": "",
                "long_name": "Maximum hourly ocean temperature of the week",
                "short_name": "Maximum",
                "compression": "water_temperature"
            },
            "min": {
                "description": "",
                "long_name": "Minimum hourly ocean temperature of the week",
                "short_name": "Minimum",
                "compression": "water_temperature"
            },
            "range": {
                "description": "",
                "long_name": "Range from the highest to lowest hourly ocean temperatures in this week",
                "short_name": "Temperature range",
                "compression": "temperature_range_sensitive"
            }
        },
        "waves": {
            "avg": {
                "description": "",
                "long_name": "Average significant wave height through the week",
                "short_name": "Average",
                "compression": "wave_height"
            },
            "avg_max": {
                "description": "",
                "long_name": "Average of largest waves in 20-minute windows distributed hourly through the week",
                "short_name": "Average of maximums",
                "compression": "wave_height"
            },
            "avg_period": {
                "description": "",
                "long_name": "Average period of waves through the week",
                "short_name": "Average period",
                "compression": "wave_period"
            },
            "max": {
                "description": "",
                "long_name": "Approximate largest single wave of the week (amongst hourly 20-minute windows)",
                "short_name": "Largest",
                "compression": "wave_height"
            },
            "max_significant": {
                "description": "",
                "long_name": "Significant wave height in the single hour of the week where waves were tallest.",
                "short_name": "Largest significant waves",
                "compression": "wave_height"
            },
            "min_significant": {
                "description": "",
                "long_name": "Significant wave height in the single hour of the week where waves are smallest",
                "short_name": "Smallest significant waves",
                "compression": "wave_height"
            }
        }
    }
}

def merge_data_settings(A, B):
    merged = copy.deepcopy(A)
    for key,value in B['data_specs'].items(): merged['data_specs'].update([(key,copy.deepcopy(value))])
    for key,value in B['compression'].items(): merged['compression'].update([(key,copy.deepcopy(value))])
    for key,value in B['variables'].items(): merged['variables'].update([(key,copy.deepcopy(value))])
    return merged

data_settings = merge_data_settings(data_settings, extra_data_settings)

data_settings_internal = make_compression_functions(data_settings)
#The order of these two functions matters a bit.
add_empty_data_holders(data_settings)

if __name__ == '__main__':
    print(make_compression_functions(data_settings))
    print(data_settings)