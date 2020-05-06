from datetime import datetime
from glob import glob
import pandas as pd, numpy as np

from airflow import DAG
from airflow.models import Variable
from airflow.hooks.postgres_hook import PostgresHook # appearantly only good for reads but not writes? wtf
from sqlalchemy import create_engine                 # DOA for postgresql
from airflow.operators.python_operator import PythonOperator
 
import requests, re, os
import logging

def create_dag(dag_id, 
               schedule,
               dag_number,
               default_args):

    pg_dsn          = Variable.get('pg_dsn', default_var="postgresql://hwitw:hwitw@localhost:5432/hwitw_lake")
    start_year      = int(Variable.get('start_year', default_var=1960))
    end_year        = datetime.today().year
    historicals_dir = Variable.get('start_year', default_var=1960)
    dir_path        = os.path.dirname(os.path.realpath(__file__))
    base_url        = "https://www.ncei.noaa.gov/data/local-climatological-data/access/"
    data_dir        = "/home/dave/projects/how_weird_is_the_weather/data/external/historical"
    hourly_features = [
        "HourlyAltimeterSetting"   ,    
        "HourlyDewPointTemperature",    
        "HourlyDryBulbTemperature" ,    
        "HourlyPrecipitation"      ,    
        "HourlyPresentWeatherType" ,    
        "HourlyPressureChange"     ,    
        "HourlyPressureTendency"   ,    
        "HourlyRelativeHumidity"   ,    
        "HourlySkyConditions"      ,    
        "HourlySeaLevelPressure"   ,    
        "HourlyStationPressure"    ,    
        "HourlyVisibility"         ,    
        "HourlyWetBulbTemperature" ,    
        "HourlyWindDirection"      ,    
        "HourlyWindGustSpeed"      ,    
        "HourlyWindSpeed"          ,
    ]
    type_map = dict(
        HourlyVisibility = "object",
    )

    target_features = list(set(hourly_features) - set(['HourlyPresentWeatherType', 'HourlySkyConditions']))

    # echo "Sending request to $base_url..."
    # directory_src=`curl $base_url`
    # filename=`echo {$directory_src} | grep -o -E href=\"\([0-9]{6}25507.csv\) | grep -o -E [0-9]+.csv`
    # echo "Found file $filename"
    # echo "Downloading to historical/$i/$filename..."
    # mkdir -p ./historical/$i
    # wget -O ./historical/$i/$STATION_ID.csv $base_url/$filename

    def fetch_station(*args, **kwargs):

        # fetch index by year
        for year in range(start_year, end_year + 1):
            url = f"{base_url}{year}/"
            index_file = data_dir + f"/{year}/index.html"

            if os.path.exists(index_file):
                with open(data_dir + f"/{year}/index.html") as f:
                    index_contents = f.read()
            else: 
                response = requests.get(url)
                index_contents = response.text

            if not index_contents and response.status_code != 200:
                print(type)
                raise ValueError(f'Response fetch_station({kwargs}) with url {url}: {response.status_code}')


            m = re.search(r"href=\"([0-9]{6}" + str(station_id) + ".csv)", index_contents)

            try:
                station_filename = m.group(1)
            except:
                print(m)
                raise ValueError(f"Could not find CSV match for station: {station_id}")

            # Check if historical file directory exists
            if not os.path.isdir(data_dir + "/" + str(year)):
                #print("Creating directory", data_dir + "/" + str(year))
                logging.info("Creating directory" + data_dir + "/" + str(year))
                os.makedirs(data_dir + "/" + str(year))

            if not os.path.exists(index_file):
                with open(index_file, "w") as f:
                    f.write(response.text)

            # Check if year direcotry not exists
            target_filename =  data_dir + "/" + str(year) + f"/{station_filename}"

            if not os.path.isfile(target_filename):
                with open(target_filename, "w") as f:
                    response = requests.get(f"{url}/{station_filename}")
                    f.write(response.text)

    def clean_hourly(series):
        
        def remove_ending(n):
            
            ## Dealing with wind direction
            if n == "VRB":
                n = np.nan
                
            ## Regular "s" and other single character endings 
            if type(n) == str and (n[0].isalpha() or n[-1].isalpha()):
                n = float("".join([i for i in n if i.isdigit()]))
            
            return n
        
        clean_map = dict(
            map_t         = lambda n: .05 if n == "T" else n,
            map_star      = lambda n: np.nan if n in ["*", "M"] else n,
            remove_ending = remove_ending
        )
        
        for method_name, method in clean_map.items():
            series = series.map(method)
        
        return series

    def extract_load_station_csv(*args, **kwargs):

        src_conn = create_engine(pg_dsn)
        df = pd.read_sql("select * from pg_catalog.pg_tables", con = src_conn)
        incoming_table_exists = df.query('tablename == "lcd_incoming"').shape[0]
        logging.info(incoming_table_exists)
        ## Iterate through years to find local CSV files matching station in context
        for year in range(start_year, end_year + 1):
            year_directory = f"{data_dir}/{year}"
            year_csv_file  = f"{year_directory}/*{station_id}.csv"
            ## Check if table already exists and data exists for this year

            try:
                year_csv = glob(year_csv_file)
                year_csv = (year_csv[:1] or [False])[0]
                lcd_df = pd.read_csv(
                    year_csv, 
                    encoding        = "UTF8", 
                    low_memory      = False, 
                    dtype           = type_map,
                    keep_default_na = False, 
                    na_values       = ['', ' ', '-', '_', '+']
                )
                lcd_df.loc[:, target_features] = lcd_df[target_features].apply(clean_hourly).astype(float)
                cleaned_df = lcd_df.set_index("DATE")[target_features]
                cleaned_df.to_sql("lcd_incoming", if_exists = "append", con = src_conn)
            except:
                raise ValueError(f"Couldn't load to staging database: {year_csv_file}")

    dag = DAG(dag_id,
        schedule_interval=schedule,
        default_args=default_args
    )

    # Fetch station CSV if exists
    t1 = PythonOperator(
        task_id         = 'fetch_station',
        provide_context = True,
        python_callable = fetch_station,
        op_kwargs       = dict(station_id = station_id),
        catchup         = False,
        dag             = dag
    )

    # Move station CSV into database if database records don't exist
    t2 = PythonOperator(
        task_id         = 'extract_load_station_csv',
        provide_context = True,
        python_callable = extract_load_station_csv,
        op_kwargs       = dict(station_id = station_id),
        catchup         = False,
        dag             = dag
    )

    # Make sure we do task1 before task2
    t1.set_downstream(t2)

    return dag


station_ids = map(int, Variable.get('station_ids', default_var=["25507"]).split())

for dag_number, station_id in enumerate(list(station_ids)):
    dag_id = f'fetch_station_csv_{station_id}'

    default_args = {'owner': 'airflow',
                    'start_date': datetime.today(),
                    'max_active_runs': 1
                    }

    schedule = '@daily'

    # dag_number = n

    globals()[dag_id] = create_dag(
        dag_id,
        schedule,      # How often will the dag run
        station_id,    # parameter send to fetch_station
        default_args
    )