ready_locations = [
    "Seldovia",
    "Offshore_of_Kodiak",
    "Southern_Bering_Sea",
    "Sterling",
    "Haida_1",
    "Plymouth",
    "Taan_Fiord",
    "Puerto_Maldonado",
    "Phoenix",
    "Little_Diomede",
    "North_Pacific"
]

site_settings = {
    "Global":{
        "name":"location: {inp_lat}, {inp_long)",
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Seldovia":{
        "name":"Seldovia",
        "inp_lat": 59.45,
        "inp_long":-151.72,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought','ocean_temperature'],
#        "notes":"geocode: 861233"
    },
    "Sterling":{
        "name":"Sterling",
        "inp_lat":60.54,
        "inp_long":-150.78,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','runoff','drought'],
#        "notes":"geocode: 868436"
    },
    "Plymouth":{
        "name":"Plymouth",
        "inp_lat":41.96,
        "inp_long":-70.67,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Taan_Fiord":{
        "name":"Taan_Fiord",
        "inp_lat": 60.178,
        "inp_long":-141.0838,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Puerto_Maldonado":{
        "name":"Puerto_Maldonado",
        "inp_lat": -12.583,
        "inp_long":-69.195,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Phoenix":{
        "name":"Phoenix",
        "inp_lat":33.4,
        "inp_long":-112.1,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Little_Diomede":{
        "name":"Little_Diomede",
        "inp_lat":65.76,
        "inp_long":-168.93,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover']
    },
    "Haida_1":{
        "name":"Haida_1",
        'inp_lat':53.213405,
        'inp_long':-135.854727,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temperature']
    },
    "North_Pacific":{
        "name":"North_Pacific",
        'inp_lat':48.715849,
        'inp_long':-176.966171,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temperature']
    },
    "Southern_Bering_Sea":{
        "name":"Southern_Bering_Sea",
        "inp_lat":54.217174,
        "inp_long":-169.193876,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temperature']
    },
    "Offshore_of_Kodiak":{
        "name":"Offshore_of_Kodiak",
        "inp_lat":53.211884,
        "inp_long":-154.708915,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temperature']
    },
    "Galveston":{
        "name":"Galveston",
        "inp_lat":29.3,
        "inp_long":-94.8,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought','ocean_temperature']
    }
}
