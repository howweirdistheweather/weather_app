ready_locations = [
    "Seldovia",
    "Yakutat",
    "McMurdo",
    "Aachen",
    "Seattle",
    "Batagaika",
    "Dubai",
    "Grewingk",
    "Solar_de_Uyuni",
    "Galveston",
    "Offshore_of_Kodiak",
    "Southern_Bering_Sea",
    "Sterling",
    "Haida_1",
    "Plymouth",
    "Taan_Fiord",
    "Puerto_Maldonado",
    "Phoenix",
    "Little_Diomede",
    "North_Pacific",
    "Alert"
]

site_settings = {
    "Global":{
        "name":"location: {inp_lat}, {inp_long)",
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover'],
        "output_raw_years":[],
    },
    "Seldovia":{
        "name":"Seldovia",
        "end_year":2022,
        "inp_lat": 59.45,
        "inp_long":-151.72,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought', 'ocean_temp'],
        "output_raw_years":[1989, 2021],
#        "notes":"geocode: 861233"
    },
    "Sterling":{
        "name":"Sterling",
        "end_year":2022,
        "inp_lat":60.54,
        "inp_long":-150.78,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[2021],
#        "notes":"geocode: 868436"
    },
    "Plymouth":{
        "name":"Plymouth",
        "end_year":2021,
        "inp_lat":41.96,
        "inp_long":-70.67,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover'],
        "output_raw_years":[],
    },
    "Taan_Fiord":{
        "name":"Taan_Fiord",
        "end_year":2021,
        "inp_lat": 60.178,
        "inp_long":-141.0838,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover'],
        "output_raw_years":[],
    },
    "Puerto_Maldonado":{
        "name":"Puerto_Maldonado",
        "end_year":2021,
        "inp_lat": -12.583, #lat=-12.583&lon=-69.195
        "inp_long":-69.195,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover'],
        "output_raw_years":[],
    },
    "Phoenix":{
        "name":"Phoenix",
        "end_year":2021,
        "inp_lat":33.4, #lat=33.4&lon=-112.1
        "inp_long":-112.1,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover'],
        "output_raw_years":[],
    },
    "Little_Diomede":{
        "name":"Little_Diomede",
        "end_year":2021,
        "inp_lat":65.76,
        "inp_long":-168.93,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover'],
        "output_raw_years":[],
    },
    "Haida_1":{
        "name":"Haida_1",
        "end_year":2021,
        'inp_lat':53.213405,
        'inp_long':-135.854727,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temp'],
        "output_raw_years":[2016,2019,2020,2021],
    },
    "North_Pacific":{
        "name":"North_Pacific",
        "end_year":2021,
        'inp_lat':48.715849,
        'inp_long':-176.966171,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temp'],
        "output_raw_years":[2016,2019,2020,2021],
    },
    "Southern_Bering_Sea":{
        "name":"Southern_Bering_Sea",
        "end_year":2021,
        "inp_lat":54.217174,
        "inp_long":-169.193876,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temp'],
        "output_raw_years":[2016,2019,2020,2021],
    },
    "Offshore_of_Kodiak":{
        "name":"Offshore_of_Kodiak",
        "end_year":2021,
        "inp_lat":53.211884,
        "inp_long":-154.708915,
        "available_groups":['temperature_and_humidity','wind','precipitation','cloud_cover','waves','ocean_temp'],
        "output_raw_years":[2016,2019,2020,2021],
    },
    "Galveston":{
        "name":"Galveston",
        "end_year":2021,
        "inp_lat":29.3,
        "inp_long":-94.8,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[],
    },
    "Solar_de_Uyuni":{
        "name":"Solar_de_Uyuni",
        "end_year":2022,
        "inp_lat":-20.1,
        "inp_long":-68.1,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[2021],
    },
    "Alert":{
        "name":"Alert",
        "end_year":2022,
        "inp_lat":82.48,
        "inp_long":-62.35,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover'],
        "output_raw_years":[2021],
    },
    "Grewingk":{
        "name":"Grewingk",
        "end_year":2022,
        "inp_lat":59.6,
        "inp_long":-151.1,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "Dubai":{
        "name":"Dubia",
        "end_year":2022,
        "inp_lat":25.2, #lat=25.2&lon=55.3
        "inp_long":55.3,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[2021]
    },
    "Batagaika":{
        "name":"Batagaika",
        "end_year":2022,
        "inp_lat":67.58,
        "inp_long":134.77,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover'],# 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "Seattle":{
        "name":"Seattle",
        "end_year":2022,
        "inp_lat":47.6,
        "inp_long":-122.336,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "Aachen":{
        "name":"Aachen",
        "end_year":2022,
        "inp_lat":50.77,
        "inp_long":6.08,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "McMurdo":{
        "name":"McMurdo",
        "end_year":2022,
        "inp_lat":-77.85,
        "inp_long":166.69,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "Yakutat":{
        "name":"Yakutat",
        "end_year":2022,
        "inp_lat":59.55,
        "inp_long":-139.73,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    },
    "Melbourne":{
        "name":"Melbourne",
        "end_year":2022,
        "inp_lat":-37.8,
        "inp_long":144.9,
        "available_groups":['temperature_and_humidity', 'wind', 'precipitation', 'cloud_cover', 'runoff', 'drought'],
        "output_raw_years":[]
    }
}
