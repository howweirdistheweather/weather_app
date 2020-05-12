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
               station_id,
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

def create_dag(dag_id, 
               schedule,
               station_id,
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
        """ This method could be pushed to a library and included since it's redundant in both dag files. Basically,
        downloads the current CSV based on the "end_year" (current year), then attempts to update the database for the specific station.

        Raises:
            ValueError: When NOAA LCD station network != 200 ok
            ValueError: When regex doesn't match the station_id defined from admin variable
        """
        year = end_year
        # fetch index by year
        url = f"{base_url}{year}/"
        index_file = data_dir + f"/{end_year}/index.html"

        if os.path.exists(index_file):
            with open(data_dir + f"/{end_year}/index.html") as f:
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

        ## Update current year file (has the updated daily events)
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

    def load_station_csv_daily(*args, **kwargs):

        src_conn = create_engine(pg_dsn)

        ## get latest CSV data
        year_directory = f"{data_dir}/{end_year}"
        year_csv_file  = f"{year_directory}/*{station_id}.csv"
        ## Check if table already exists and data exists for this year

        try:
            year_csv = glob(year_csv_file)
            year_csv = (year_csv[:1] or [False])[0]
            logging.info(f"Loading file: {year_csv}")
            lcd_df = pd.read_csv(
                year_csv, 
                encoding        = "UTF8", 
                low_memory      = False, 
                dtype           = type_map,
                keep_default_na = False, 
                na_values       = ['', ' ', '-', '_', '+']
            )
            lcd_df.loc[:, target_features] = lcd_df[target_features].apply(clean_hourly).astype(float)
            ## Adding station_id to output
            lcd_df['station_id'] = station_id

            ## Get max day for station in database
            sql = f"""
                SELECT TO_CHAR(TO_DATE(MAX("DATE"), 'YYYY-MM-DD'), 'YYYYMMDD') AS last_date 
                FROM lcd_incoming 
                WHERE station_id = {station_id}
            """
            df = pd.read_sql(sql, con = src_conn).get('last_date')
            last_date = df.iloc[0]
            logging.info(f"Max date: {last_date}")
            # Select only new records
            delta_records = lcd_df.query(f'DATE > "{last_date}"')

            # Update new records if available
            if delta_records.shape[0]:
                cleaned_df = delta_records.set_index("DATE")[['station_id'] + target_features]
                logging.info(cleaned_df.head())
                cleaned_df.to_sql("lcd_incoming", if_exists = "append", con = src_conn)
                logging.info(f"Successfully loaded {cleaned_df.shape[0]} new daily record(s)")
            else:
                logging.info(f"No new records to load for {station_id}")
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
        dag             = dag
    )

    # Move station CSV into database if database records don't exist
    t2 = PythonOperator(
        task_id         = 'load_station_csv_daily',
        provide_context = True,
        python_callable = load_station_csv_daily,
        op_kwargs       = dict(station_id = station_id),
        dag             = dag
    )

    # Make sure we do task1 before task2
    t1.set_downstream(t2)

    return dag


station_ids = map(int, Variable.get('station_ids', default_var=["25507"]).split())

for dag_number, station_id in enumerate(list(station_ids)):
    dag_id = f'fetch_daily_station_csv_{station_id}'

    default_args = {'owner': 'airflow',
                    'start_date': datetime.today(),
                    'max_active_runs': 1,
                    }

    schedule = '@daily'

    # dag_number = n

    globals()[dag_id] = create_dag(
        dag_id,
        schedule,      # How often will the dag run
        station_id,    # parameter send to fetch_station
        default_args
    )