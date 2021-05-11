# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
import sys
import io
import re
import json
import random
import pandas as pd
import numpy as np
import sqlalchemy


class HData:

    def __init__( self, fake_data = False ):
        self.fake_data           = fake_data
        self.db_conn_str         = 'postgresql://hwitw:hwitw@localhost:5432/hwitw_lake'
        self.station_data        = None
        self.agg_methods        = [ 'MEDIAN','AVG', 'MIN', 'MAX' ]
        self.range_v1            = 0.33     # color slider range value 1
        self.range_v2            = 0.66     # slider value 2
        # this is causing a db concurrency error: create_pg_median( self.db_conn_str )  
        pass            

    def get_aggmethods_json( self ):
        return json.dumps( self.agg_methods )

    # get the station meta table as json
    def get_stationsmeta_json( self, sm_type, sm_co, sm_state ):
        sys.stderr.write( 'dbg: get_stationsmeta sm_type:' + sm_type + ' sm_co:' + sm_co + ' sm_state:' + sm_state + '\n' )

        if self.fake_data: 
            if sm_type == 'state':
                sta_list = [{"index":29223,"STATIONID":"99999925701","USAF":"999999","WBAN":"25701","STATIONNAME":"ADAK DAVIS AFB","CTRY":"US","STATE":"AK","ICAO":None,"LAT":51.883,"LON":-176.65,"ELEVM":4.9,"BEGIN":19490101,"END":19500701},{"index":27880,"STATIONID":"99738099999","USAF":"997380","WBAN":"99999","STATIONNAME":"ADAK ISLAND","CTRY":"US","STATE":"AK","ICAO":None,"LAT":51.87,"LON":-176.63,"ELEVM":7.0,"BEGIN":20080101,"END":20200924},{"index":15469,"STATIONID":"70454099999","USAF":"704540","WBAN":"99999","STATIONNAME":"ADAK (NAS)","CTRY":"US","STATE":"AK","ICAO":"PADK","LAT":51.883,"LON":-176.65,"ELEVM":5.0,"BEGIN":20000101,"END":20031231},{"index":15468,"STATIONID":"70454025704","USAF":"704540","WBAN":"25704","STATIONNAME":"ADAK NAS","CTRY":"US","STATE":"AK","ICAO":"PADK","LAT":51.883,"LON":-176.65,"ELEVM":5.2,"BEGIN":19421030,"END":20200925},{"index":15459,"STATIONID":"70392699999","USAF":"703926","WBAN":"99999","STATIONNAME":"AKHIOK","CTRY":"US","STATE":"AK","ICAO":"PAKH","LAT":56.933,"LON":-154.183,"ELEVM":13.0,"BEGIN":20070521,"END":20200924}]
                return json.dumps( sta_list )
            elif sm_type == 'co':
                state_list = [{"STATE":"AK"},{"STATE":"AL"},{"STATE":"FL"}] 
                return json.dumps( state_list )
            else:
                ctry_list = [{"CTRY":"US"},{"CTRY":"AC"},{"CTRY":"AE"}]
                return json.dumps( ctry_list )


        # Connect to the database
        conn = sqlalchemy.create_engine( self.db_conn_str )

        sql = ''
        params1 = None

        if sm_type == 'state' and sm_state == 'null':    # let 'null' be a wildcard
            sql = "SELECT * FROM stations_in WHERE \"CTRY\" = %(sm_co)s ORDER BY \"STATIONNAME\""
            params1 = { 'sm_co':sm_co }
        elif sm_type == 'state':            
            sql = "SELECT * FROM stations_in WHERE \"CTRY\" = %(sm_co)s AND \"STATE\" = %(sm_state)s ORDER BY \"STATIONNAME\""
            params1 = { 'sm_co':sm_co, 'sm_state':sm_state }
        elif sm_type == 'co':
            sql = "SELECT DISTINCT \"STATE\" FROM stations_in WHERE \"CTRY\" = %(sm_co)s ORDER BY \"STATE\""
            params1 = { 'sm_co':sm_co }
        else:
            sql = "SELECT DISTINCT \"CTRY\" FROM stations_in ORDER BY \"CTRY\""

        # get station meta data
        station_meta = pd.read_sql(
            sql = sql,
            con = conn,
            params = params1
        )
        return station_meta.to_json(orient='records')

    # get the column list
    def get_collist_json( self ):
        sys.stderr.write( 'dbg: get_collist\n' )
        
        if self.fake_data:
            return json.dumps( ['temperature','windspeed','rainfall'] )

        # Connect to the PostgreSQL database
        conn = sqlalchemy.create_engine( self.db_conn_str )

        # get the column list
        sql = "SELECT * FROM lcd_incoming LIMIT 1"
        columns_df = pd.read_sql(
                sql,
                con = conn,
                parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'},
                index_col='DATE' )

        main_column_list = list(columns_df.columns)
        return json.dumps( main_column_list );


# this gives us a median() function in postgres. Found somewhere on the www.
def create_pg_median( db_conn_str:str ):
    func_sql = """CREATE OR REPLACE FUNCTION _final_median(anyarray) RETURNS float8 AS $$ 
                WITH q AS
                (
                    SELECT val
                    FROM unnest($1) val
                    WHERE VAL IS NOT NULL
                    ORDER BY 1
                ),
                cnt AS
                (
                    SELECT COUNT(*) as c FROM q
                )
                SELECT AVG(val)::float8
                FROM 
                (
                    SELECT val FROM q
                    LIMIT  2 - MOD((SELECT c FROM cnt), 2)
                    OFFSET GREATEST(CEIL((SELECT c FROM cnt) / 2.0) - 1,0)  
                ) q2;
                $$ LANGUAGE sql IMMUTABLE;

                DROP AGGREGATE IF EXISTS median(anyelement);
                CREATE AGGREGATE median(anyelement) (
                SFUNC=array_append,
                STYPE=anyarray,
                FINALFUNC=_final_median,
                INITCOND='{}'
                );"""

    # Connect to the PostgreSQL database and execute the sql
    conn = sqlalchemy.create_engine( db_conn_str )    
#    try:
    sql_result = conn.execute( func_sql )        
#    except:# sqlalchemy  psycopg2.errors.DuplicateFunction:
#        raise RuntimeError( "Crap median!!" )

# process station dataframe into a heatmap data
def create_heat_df( station_df:pd.DataFrame, column_a:str, method_a:str ):
    # drop leap year week 53's
    heat_df = station_df[ station_df.theweek <= 52 ]
    heat_df['theyear'] = heat_df['theyear'].astype(int) # so they don't print as floats like 1950.0
    heat_df = heat_df.pivot( index='theyear', columns='theweek', values='xval' )
    return heat_df

def month_to_week( nmonth ):
    import datetime
    day_of_year = datetime.date( year=datetime.datetime.now().year, month=nmonth, day=1 ).timetuple().tm_yday
    return day_of_year * 52 / 365 

def create_hmap_json( station_df:pd.DataFrame, hdat:HData, col_a:str, met_a:str ):
    hdf = create_heat_df( station_df, col_a, met_a )
    return hdf.to_json(orient='values')

def create_station_hmap_json( hdat:HData, station_id:str, df_column:str, df_method:str ):
    sys.stderr.write( 'dbg: create_station_hmap_json station_id:' + station_id + ' df_column:' + df_column + ' df_method:' + df_method + '\n' )

    # TODO SANITIZE df_column and df_method. these are user input so we need to watch
    # out for SQL injection type attacks
    if df_method == None or df_method not in hdat.agg_methods:
        df_method = hdat.agg_methods[0]

    if hdat.fake_data:
        # make an array of random values
        num_year = 60
        num_week = 52
        some_fake_data = [[0 for i in range(num_week)] for j in range(num_year)]
        for y in range( num_year ):
            for w in range( num_week ):
                some_fake_data[y][w] = random.random()

        # put some nulls in there to simulate DB nulls
        some_fake_data[0][0] = None
        some_fake_data[0][1] = None
        some_fake_data[0][2] = None
        some_fake_data[0][3] = None
        some_fake_data[0][4] = None
        some_fake_data[9][5] = None

        return json.dumps( some_fake_data )

    # Connect to the PostgreSQL database
    conn = sqlalchemy.create_engine( hdat.db_conn_str )    

    # main data query
    agg_str = """%s("%s")""" % (df_method, df_column)    

    sql = """SELECT DATE_PART('year', "DATE") as "theyear",
                    DATE_PART('week', "DATE") as "theweek",
                    %s AS "xval" """ % agg_str + """
                    from lcd_incoming
                    where station_id = %(psid)s group by theyear, theweek"""                    
    
    main_df = pd.read_sql(
        sql,
        con = conn,
        params = { 'psid':station_id }
    )

    return create_hmap_json( main_df, hdat, df_column, df_method )
