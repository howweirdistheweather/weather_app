import math
import copy

data_settings = {
    "data_specs": {
        "start_year":1950
    },
    "compression": {
        "temperature":{
            "min":-60,
            "max":67.5,
            "scale":0.5,
            "type":"linear",
            "units":"C"
        },
        "temperature_range":{
            "min":0,
            "max":51,
            "scale":0.2,
            "type":"linear",
            "units":"C"
        },
        "wind_speed":{
            "min":0,
            "max":127.5,
            "scale":0.5,
            "type":"linear",
            "units":"m/s"
        },
        "direction":{
            "min":0,
            "max":360,
            "scale":2,
            "type":"linear",
            "units":"degrees"
        },
        "proportion":{
            "min":0,
            "max":1,
            "scale":0.005,
            "type":"linear",
            "units":""
        }
    },
    "variables": {
        "temperature":{
            "min":{
                "long_name":"Coldest single hour of the week",
                "compression":"temperature"
            },
            "p10":{
                "long_name":"10th percentile temperature (the 17th coldest single hour in the week)",
                "compression":"temperature"
            },
            "avg":{
                "long_name":"Average hourly temperature",
                "compression":"temperature"
            },
            "p90":{
                "long_name":"90th percentile temperature (the 17th hottest single hour in the week)",
                "compression":"temperature"
            },
            "max":{
                "long_name":"Hottest single hour of the week",
                "compression":"temperature"
            },
            "day_avg":{
                "long_name":"Average hourly temperature between 6 am and 6 pm solar time",
                "compression":"temperature"
            },
            "night_avg":{
                "long_name":"Average hourly temperature before 6 am and after 6 pm solar time",
                "compression":"temperature"
            },
            "range_avg":{
                "long_name":"Average difference between the coldest and hottest hours of the day for each day this week",
                "compression":"temperature_range"
            }
        },
        "relative_humidity":{
            "p10":{
                "long_name":"10th percentile humidity (the 17th driest hour in the week)",
                "compression":"proportion"
            },
            "p50":{
                "long_name":"Median relative humidity",
                "compression":"proportion"
            },
            "p90":{
                "long_name":"90th percentile humidity (the 17th wettest hour in the week)",
                "compression":"proportion"
            }
        },
        "wind":{
            "avg":{
                "long_name":"Average hourly wind speed",
                "compression":"wind_speed"
            },
            "modal_dir":{
                "long_name":"Most common wind direction this week",
                "compression":"direction"
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
        if compressed > 255: return 255
        elif compressed < 0: return 0
        else: return compressed
    return compression_function

def make_compression_functions():
    settings = copy.deepcopy(data_settings)
    variables = settings['variables']
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
            else: raise Exception(f'ERROR: Compression type not implemented: {compression_info}')
    return settings

data_settings_internal = make_compression_functions()
#The order of these two functions matters a bit.
add_empty_data_holders()

if __name__ == '__main__':
    print(make_compression_functions())
    print(data_settings)