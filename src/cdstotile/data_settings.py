import math
import copy

data_settings = {
    "data_specs": {
        "start_year":1950
    },
    "compression": {
        "temperature":{
            "min":-60,
            "scale":0.5,
            "type":"linear",
            "units":"C"
        },
        "temperature_range":{
            "min":0,
            "scale":0.1,
            "type":"linear",
            "units":"C"
        },
        "wind_speed_HiFi":{
            "min":0,
            "scale":0.1,
            "type":"linear",
            "units":"m/s"
        },
        "wind_speed_LoFi":{
            "min":0,
            "scale":0.4,
            "type":"linear",
            "units":"m/s"
        },
        "direction":{
            "min":0, #Should be safe, but 0 as min direction is assumed elsewhere
            "scale":1.5, #2 works pretty good and is rounder
            "type":"linear",
            "units":"degrees"
        },
        "proportion":{
            "min":0,
            "scale":0.0039,
            "type":"linear",
            "units":""
        },
        "precipitation":{
            "min":0,
            "scale":0.003,
            "type":"parabolic",
            "units":"m"
        },
        "cloud_ceiling":{
            "min":0,
            "scale":30,
            "type":"linear",
            "units":"m"
        }
    },
    "variables": {
        "temperature":{
            "avg":{
                "long_name":"Average hourly temperature",
                "short_name":"Average",
                "compression":"temperature"
            },
            "min":{
                "long_name":"Coldest single hour of the week",
                "short_name":"Minimum",
                "compression":"temperature"
            },
            "p10":{
                "long_name":"10th percentile temperature (the 17th coldest single hour in the week)",
                "short_name":"10th percentile",
                "compression":"temperature"
            },
            "p90":{
                "long_name":"90th percentile temperature (the 17th hottest single hour in the week)",
                "short_name":"90th percentile",
                "compression":"temperature"
            },
            "max":{
                "long_name":"Hottest single hour of the week",
                "short_name":"Maximum",
                "compression":"temperature"
            },
            "day_avg":{
                "long_name":"Average hourly temperature between 6 am and 6 pm solar time",
                "short_name":"Daytime average",
                "compression":"temperature"
            },
            "night_avg":{
                "long_name":"Average hourly temperature before 6 am and after 6 pm solar time",
                "short_name":"Nighttime average",
                "compression":"temperature"
            },
            "range_avg":{
                "long_name":"Average difference between the coldest and hottest hours of the day for each day this week",
                "short_name":"Average daily range",
                "compression":"temperature_range"
            }
        },
        "relative_humidity":{
            "p50":{
                "long_name":"Median relative humidity",
                "short_name":"Median",
                "compression":"proportion"
            },
            "p10":{
                "long_name":"10th percentile humidity (the 17th driest hour in the week)",
                "short_name":"10th percentile",
                "compression":"proportion"
            },
            "p90":{
                "long_name":"90th percentile humidity (the 17th wettest hour in the week)",
                "short_name":"90th percentile",
                "compression":"proportion"
            }
        },
        "wind":{
            "speed_avg":{
                "long_name":"Average hourly wind speed",
                "short_name":"Average speed",
                "compression":"wind_speed_HiFi"
            },
            "dir_modal":{
                "long_name":"Most common wind direction this week",
                "short_name":"Modal direction",
                "compression":"direction"
            },
            "speed_max":{
                "long_name":"Strongest hour of wind all week",
                "short_name":"Maximum speed",
                "compression":"wind_speed_LoFi"
            },
            "dir_net":{
                "long_name":"Direction of net wind displacement over the week",
                "short_name":"Average direction",
                "compression":"direction"
            },
            "speed_net":{
                "long_name":"Average speed of transport in the direction of net wind displacement",
                "short_name":"Average velocity",
                "compression":"wind_speed_HiFi"
            }
        },
        "precipitation":{
            'total':{
                "long_name":"Total of all types of precipitation over the week",
                "short_name":"Total",
                "compression":"precipitation"
            },
            'total_rain':{
                "long_name":"Total rainfall over the week",
                "short_name":"Total rain",
                "compression":"precipitation"
            },
            'total_snow':{
                "long_name":"Total snowfall over the week (water equivalent)",
                "short_name":"Total snow",
                "compression":"precipitation"
            },
            'total_wet_snow':{
                "long_name":"Total wet snow over the week (water equivalent)",
                "short_name":"Total wet snow",
                "compression":"precipitation"
            },
            'total_freezing_rain':{
                "long_name":"Total freezing rain over the week",
                "short_name":"Total freezing rain",
                "compression":"precipitation"
            },
            'total_ice_pellets':{
                "long_name":"Total ice pellets or hail over the week (water equivalent)",
                "short_name":"Total ice pellets",
                "compression":"precipitation"
            },
            'p90':{
                "long_name":"90th percentile hourly precipitation over the week (water equivalent)",
                "short_name":"90th percentile",
                "compression":"precipitation"
            },
            'max':{
                "long_name":"Most precipitation in any hour of the week (water equivalent)",
                "short_name":"Maximum",
                "compression":"precipitation"
            }
        },
        "cloud_cover": {
            "p50":{
                "long_name":"Median cloud cover",
                "short_name":"Median",
                "compression":"proportion"
            },
            "p25":{
                "long_name":"25th percentile cloud cover",
                "short_name":"25th percentile",
                "compression":"proportion"
            },
            "p75":{
                "long_name":"75th percentile cloud cover",
                "short_name":"75th percentile",
                "compression":"proportion"
            },
            "p_sunny":{
                "long_name":"Proportion of time with less than 10% cloud cover",
                "short_name":"Proportion sunny",
                "compression":"proportion"
            },
            "p_cloudy":{
                "long_name":"Proportion of time with more than 90% cloud cover",
                "short_name":"Proportion cloudy",
                "compression":"proportion"
            }
        },
        "cloud_ceiling": {
            "p50":{
                "long_name":"Median ceiling elevation",
                "short_name":"Median",
                "compression":"cloud_ceiling"
            },
            "min":{
                "long_name":"Lowest ceiling elevation in any hour of the week",
                "short_name":"Lowest ceiling",
                "compression":"cloud_ceiling"
            },
            "p25":{
                "long_name":"25th percentile ceiling elevation",
                "short_name":"25th percentile",
                "compression":"cloud_ceiling"
            },
            "p75":{
                "long_name":"75th percentile ceiling elevation",
                "short_name":"75th percentile",
                "compression":"cloud_ceiling"
            },
            "max":{
                "long_name":"Highest ceiling elevation in any hour of the week (clear is considered max height)",
                "short_name":"Highest ceiling",
                "compression":"cloud_ceiling"
            }
        }
    }
}

def add_empty_data_holders():
    for variable,variable_info in data_settings['variables'].items():
        for stat,details in variable_info.items():
            details.update([('data',[])])

def create_linear_compression_function(min, scale):
    def compression_function(value):
        compressed = int((value-min)/scale) #It is considerably more time-costly to force it to numpy.uint8 rather than int
        if compressed > 254: return 254
        elif compressed < 0: return 0
        else: return compressed
    return compression_function

def create_parabolic_compression_function(scale):
    def compression_function(value):
        compressed = int(math.sqrt(value)/scale)
        if compressed > 254: return 254
        else: return compressed
    return compression_function

"""
def create_linear_compression_function(min, scale):
    def compression_function(value):
        try:
            compressed = int((value-min)/scale) #It is considerably more time-costly to force it to numpy.uint8 rather than int
            if compressed > 254: return 254
            elif compressed < 0: return 0
            else: return compressed
        except: return 255
    return compression_function

def create_parabolic_compression_function(scale):
    def compression_function(value):
        try:
            compressed = int(math.sqrt(value)/scale)
            if compressed > 254: return 254
            else: return compressed
        except: return 255
    return compression_function
"""
def make_compression_functions():
    settings = copy.deepcopy(data_settings)
    variables = settings['variables']
    settings.update([('flat_functions',{})])
    for variable,variable_info in variables.items():
        for stat,details in variable_info.items():
            compression_info = data_settings['compression'][details['compression']]
            if compression_info['type'] == 'linear':
                details.update([(
                    "compression_function",create_linear_compression_function(
                        compression_info['min'],
                        compression_info['scale']
                    )
                )])
                settings['flat_functions'].update([(
                    f'{variable}_{stat}',create_linear_compression_function(
                        compression_info['min'],
                        compression_info['scale']
                    )
                )])
            elif compression_info['type'] == 'parabolic':
                details.update([(
                    "compression_function",create_parabolic_compression_function(
                        compression_info['scale']
                    )
                )])
                settings['flat_functions'].update([(
                    f'{variable}_{stat}',create_parabolic_compression_function(
                        compression_info['scale']
                    )
                )])
            else: raise Exception(f'ERROR: Compression type not implemented: {compression_info}')
    return settings

data_settings_internal = make_compression_functions()
#The order of these two functions matters a bit.
add_empty_data_holders()

if __name__ == '__main__':
    print(make_compression_functions())
    print(data_settings)