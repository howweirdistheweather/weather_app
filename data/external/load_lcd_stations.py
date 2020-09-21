# fetch lcd station list and load into database
# HWITW Copyright (C) 2020
#
from sqlalchemy import create_engine, types as sqt                 # DOA for postgresql
import urllib.request as request
from io import StringIO
#import wget
import pandas as pd

def fetch_lcd_stationlist():
    
    try:
        station_csv_url = "ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv"    
        response = request.urlopen(station_csv_url)
        csv_contents = response.read()
        
    except EOFError as ee:        
        raise ValueError( f'FTP read failed: {ee}' )

    if not csv_contents and response.status_code != 200:
        raise ValueError( f'Response fetch_lcd_stationlist() with url {station_csv_url}: {response.status_code}')   

    csv_stringio = StringIO( csv_contents.decode(encoding='UTF-8') )

    sl_df = pd.read_csv(
        csv_stringio, 
        encoding        = "UTF8", 
        low_memory      = False, 
        keep_default_na = False,
        dtype           = { 'USAF':str,'WBAN': str, 'STATION NAME':str, 'CTRY':str, 'STATE':str, 'ICAO':str },  #, ‘c’: ‘Int64’},
        na_values       = ['', ' ', '-', '_', '+']
    )

    ## fix some stuff
    # The ELEV(M) column has parenthesis in its name. Postgres or sqlalchemy doesn't like that.
    sl_df.rename(columns={'ELEV(M)':'ELEVM'}, inplace=True)
    # Take the space out of the STATION NAME column
    sl_df.rename(columns={'STATION NAME':'STATIONNAME'}, inplace=True)

    # create a station id column which is USAF + WBAN. The lcd table uses this full 11 character id
    sl_df.insert( 0, 'STATIONID', sl_df['USAF'] + sl_df['WBAN'] )

    return sl_df

def main():
    try:        
        ## get latest CSV station list as a dataframe
        stations_df = fetch_lcd_stationlist()
        
        stations_df.info()
        print( stations_df.head() )

        # put in in a table
        pg_dsn   = "postgresql://hwitw:hwitw@localhost:5432/hwitw_lake"
        src_conn = create_engine( pg_dsn )
        stations_df.to_sql( 
            name            = "stations_in",
            if_exists       = "replace",
            con             = src_conn,
            dtype      = { 'USAF':sqt.String,'WBAN':sqt.String, 'STATIONNAME':sqt.String, 'CTRY':sqt.String, 'STATE':sqt.String, 'ICAO':sqt.String }            
        )
        
        # lcd_df.loc[:, target_features] = lcd_df[target_features].apply(clean_hourly).astype(float)
        #     ## Adding station_id to output
        #     lcd_df['station_id'] = station_id

        #     ## Get max day for station in database
        #     sql = f"""
        #         SELECT TO_CHAR(TO_DATE(MAX("DATE"), 'YYYY-MM-DD'), 'YYYYMMDD') AS last_date 
        #         FROM lcd_incoming 
        #         WHERE station_id = {station_id}
        #     """
        #     df = pd.read_sql(sql, con = src_conn).get('last_date')
        #     last_date = df.iloc[0]

        # cleaned_df.to_sql("lcd_incoming", if_exists = "append", con = src_conn)
        # logging.info(f"Successfully loaded {cleaned_df.shape[0]} new daily record(s)")
    except:
        raise ValueError(f"Couldn't load database.")

if __name__=="__main__":
    main()
