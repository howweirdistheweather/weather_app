how_weird_is_the_weather
==============================

A short description of the project.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org

--------

A place to document potential sources of weather data.  

# **<u>US NOAA</u>**
For reference most but not all are listed here: https://www.ncdc.noaa.gov/cdo-web/datasets

Note, station ids can be different for different datasets! GHCN station ids are different from NCEI.  
There is a **master station list** here that cross references the different station ids  
https://www.ncdc.noaa.gov/homr/reports/mshr

## **Weather.gov Observations**

Station IDs:?  
Latest rich hourly weather data, but only 1 month of it.

### **Access**

1. We can use the python noaa-sdk to access it programatically.  
https://www.weather.gov/documentation/services-web-api  

## **ISD - Integrated Surface Data**

Station IDs: **USAF+WBAN**  
Rich hourly weather data. Should be a good source. Except it doesn't go back very many years for some sites. For example Seldovia (Airport) only goes back to 2005. Others go back to early 1900s.  
https://www.ncdc.noaa.gov/isd  

Also check out isd-lite. A condensed version of ISD data, 8 weather variables, in an ASCII table format.  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/isd-lite-format.txt  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/isd-lite-technical-document.txt  

### **Access**

1. Data is available for direct download by year/station in a RAW ASCII METAR sentence table format.  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/  

2. Data is available via a web service? Looks like NO or it was discontinued.  

Documentation of result columns  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-format-document.pdf  

Stations are defined here:  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt  
or: ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv  

## **NDBC Buoy data**

This document spells it all out as far as what they have and how to get it  
https://www.ndbc.noaa.gov/docs/ndbc_web_data_guide.pdf  

And this is a quick example of what we can get, some ~hourly buoy data in a text file  
https://www.ndbc.noaa.gov/view_text_file.php?filename=42040h2001.txt.gz&dir=data/historical/stdmet/  

## **LCD - Local Climatological Data**

Station IDs: **USAF+WBAN**, search for the unique USAF id or the WBAN id or both [Seldovia 703621:25516]  
Based on **ISD Integrated Surface Data**  

This is basically ISD data, but processed, in a nice .CSV format.  
https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C00684/html  

### **Access**

1. Data is available for direct download by year/station in a .CSV format here.  
https://www.ncei.noaa.gov/data/local-climatological-data/access  
https://www.ncei.noaa.gov/data/local-climatological-data/doc  

2. Data is available via a web service? .CSV or JSON format  
https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation  
https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data&stations=99999925516&startDate=2005-01-01&endDate=2010-12-01  

Documentation of result columns  
https://www.ncei.noaa.gov/data/local-climatological-data/doc/LCD_documentation.pdf  

Stations are defined in the ISD:  
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt  
or: ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv  

## **GHCND - Global Historical Climate Network Daily / Daily Summaries**

Station IDs: **GHCN**  
No hourly data, probably not useful.  

Many climate website projects are using NOAAs GHCN collection for historical weather data. It has the oldest weather readings known(?) but they are daily, there is no hourly. For some sites it goes back as far as the 1700s, but the data is spotty... For example Seldovia has some readings for 1917-1920 and 1961-present day. You only get a few types of readings like TMAX TMIN PRECIP SNOW.  

### **Access**

1. Data is available for direct download by year or by station in .CSV format. It can be sourced here along with documentation.  
ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/  
ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/  
ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/  

2. There is also a "superghcnd" available, a 12GB compressed .CSV that contains ALL of it (95GB uncompressed!).  
ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/superghcnd/   

3. There is also a webapi available. It is limited by 1000 results at a time, 5 requests per second, 10000 requests per day, 1 year of data, at a time. An access token is required. Results are in JSON format. The python "noaa" class accesses this (NOT the noaa-sdk).  
https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted  

Stations are defined here: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt  

For reference and research here are some websites that make use of this data:  
https://geographic.org/global_weather/alaska/seldovia_350.html  
https://data.leonetwork.org/weather/station/USC00508350  
http://berkeleyearth.org/source-files/  
http://imiq-map.gina.alaska.edu/  

## **ASOS data**  

1-minute and 5-minute ASOS data is available, going back to the mid 1990s?. Is this already included in the LCD?  

---------

