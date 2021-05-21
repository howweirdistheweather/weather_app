# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
import sys
import io
import re
import json
import random
import statistics
import math
import pandas as pd
import numpy as np
import sqlalchemy


class HData:

    def __init__( self, fake_data = False ):
        self.fake_data           = fake_data
        self.station_data        = None
        self.agg_methods         = ['avg temp','range temp', 'median wind','99th % wind','avg rain','99th % rain' ]
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
                sta_list = [
                    {"index":29223,"STATIONID":"99999925701","USAF":"999999","WBAN":"25701","STATIONNAME":"ADAK DAVIS AFB","CTRY":"US","STATE":"AK","ICAO":None,"LAT":51.883,"LON":-176.65,"ELEVM":4.9,"BEGIN":19490101,"END":19500701},
                    {"index":27880,"STATIONID":"99738099999","USAF":"997380","WBAN":"99999","STATIONNAME":"ADAK ISLAND","CTRY":"US","STATE":"AK","ICAO":None,"LAT":51.87,"LON":-176.63,"ELEVM":7.0,"BEGIN":20080101,"END":20200924},
                    {"index":15469,"STATIONID":"70454099999","USAF":"704540","WBAN":"99999","STATIONNAME":"ADAK (NAS)","CTRY":"US","STATE":"AK","ICAO":"PADK","LAT":51.883,"LON":-176.65,"ELEVM":5.0,"BEGIN":20000101,"END":20031231},
                    {"index":15468,"STATIONID":"70454025704","USAF":"704540","WBAN":"25704","STATIONNAME":"ADAK NAS","CTRY":"US","STATE":"AK","ICAO":"PADK","LAT":51.883,"LON":-176.65,"ELEVM":5.2,"BEGIN":19421030,"END":20200925},
                    {"index":15459,"STATIONID":"70392699999","USAF":"703926","WBAN":"99999","STATIONNAME":"AKHIOK","CTRY":"US","STATE":"AK","ICAO":"PAKH","LAT":56.933,"LON":-154.183,"ELEVM":13.0,"BEGIN":20070521,"END":20200924}]
                return json.dumps( sta_list )
            elif sm_type == 'co':
                state_list = [{"STATE":"AK","CTRY":"US"},{"STATE":"AL","CTRY":"US"},{"STATE":"FL","CTRY":"US"}] 
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

def create_station_hmap_json( hdat:HData, station_id:str, df_methods:tuple ):
    sys.stderr.write( 'dbg: create_station_hmap_json station_id:' + station_id + ' df_method1:' + df_methods[0] + '\n' )
    sys.stderr.write( 'dbg: create_station_hmap_json station_id:' + station_id + ' df_method2:' + df_methods[1] + '\n' )

    # TODO SANITIZE df_column and df_method. these are user input so we need to watch
    # out for SQL injection type attacks
    for df_method in df_methods:
        if df_method == None or df_method not in hdat.agg_methods:
            df_method = hdat.agg_methods[0]

    if hdat.fake_data:
        #Generate fake hourly data
        print(df_methods)
        n_hours = 525600
        num_year = int(math.ceil(n_hours/8760))
        num_week = 52#int(math.ceil(8760/7))
        df_methods = tuple(set(df_methods))
        hourly_data = dict([(key,np.zeros(n_hours, dtype=float)) for key in ['temp','wind','rain']])
        mesuments = list(set([method.split()[-1] for method in df_methods]))
        temp_x = 0.25
        temp_y = 0.25
        wind_x = 0.25
        rain_x = 0.25
        #temp
        for i in range(n_hours):
            y = int(math.floor(i / 8760))
            w = int(math.floor(i / 168) % 52)
            if 'temp' in mesuments:
                fast_rate = 0.02
                slow_rate = 0.001
                temp_trend = float(y)/num_year * 0.2 + (1.0+math.sin(float(w)/num_week*math.pi))/2 * 0.8
                day_trend = (1.0+math.sin(float(i)/12*math.pi))/2
                temp_x = random.uniform(max(0,temp_x-fast_rate), min(1.0,temp_x+fast_rate))
                temp_y = random.uniform(max(0,temp_y-slow_rate), min(1.0,temp_y+slow_rate))
                hourly_data['temp'][i] = 0.2*temp_trend+0.3*day_trend+0.1*temp_x+0.4*temp_y
            if 'wind' in mesuments:
                wind_trend = float(y)/num_year * 0.2 + (1.0-math.sin(float(w)/num_week*math.pi-0.1))/2 * 0.8
                wind_x = random.uniform(max(0,wind_x-0.05), min(1.0,wind_x+0.05))
                hourly_data['wind'][i] = (0.7*wind_trend+0.3*wind_x)**4
            if 'rain' in mesuments:
                rain_trend = float(y)/num_year * 0.2 + (1.0-math.sin(float(w)/num_week*math.pi-0.5))/2 * 0.8
                rain_x = random.uniform(max(0,rain_x-0.3), min(1.0,rain_x+0.3))
                hourly_data['rain'][i] = max(0,(0.7*rain_trend+0.3*rain_x)**3 * 1.5 - 0.5)
        #wind
        '''
        if 'wind' in mesuments:
            for i in range(n_hours):
                y = int(math.floor(i / 8760))
                w = int(math.floor(i / 168))
                trend = float(y)/num_year * 0.2 + (1.0-math.sin(float(w)/num_week*math.pi-0.1))/2 * 0.8
                x = random.uniform(max(0,x-0.05), min(1.0,x+0.05))
                hourly_data['wind'][i] = (0.7*trend+0.3*x)**4
        #rain
        if 'rain' in mesuments:
            for i in range(n_hours):
                y = int(math.floor(i / 8760))
                w = int(math.floor(i / 168))
                trend = float(y)/num_year * 0.2 + (1.0-math.sin(float(w)/num_week*math.pi-0.5))/2 * 0.8
                x = random.uniform(max(0,x-0.3), min(1.0,x+0.3))
                hourly_data['rain'][i] = max(0,(0.7*trend+0.3*x)**5 * 1.5 - 0.5)
        '''
        #Apply selected algorithm to fake hourly data (or possibly apply all algorithms)
        weeks_in_year = 52        
        json_data = {}
        week_99th = int(168*0.99)
        for mesument in mesuments:
            for method in df_methods:
                if method.split()[-1] == mesument:
                    week_prev = -1
                    first = True
                    for i in range(n_hours):            
                        y = int(math.floor(i / 8760))
                        w = int(math.floor(i/168) % 52)
                        if w != week_prev:
                            if json_data.get(method) is None:
                                json_data[method] = [[0 for week in range(weeks_in_year)] for year in range(num_year)]
                                #do statistics and append procesed value
                            if not first:
                                if df_method.split()[0] == 'avg':
                                    json_data[method][y][w] = statistics.mean(value_list)
                                elif df_method.split()[0] == 'range':
                                    json_data[method][y][w] = max(value_list) - min(value_list)
                                elif df_method.split()[0] == 'median':
                                    json_data[method][y][w] = statistics.median(value_list)
                                elif df_method.split()[0] == '99th':
                                    json_data[method][y][w] = sorted(value_list)[week_99th]
                            first = False
                            value_list = [hourly_data[mesument][i]]
                            week_prev = w
                        else:
                            value_list.append(hourly_data[mesument][i])
        #Build data structure to send via JSON
        print('yes')
        return json.dumps( json_data )
        '''
        #median wind, 99th % wind

        week_prev = -1
        first = True
        for i,value in enumerate(hourly_data['wind']):
            y = int(math.floor(i / 8760))
            w = int(math.floor((i % 8760) / 7))
            if w != week_prev:
                #do statistics and append procesed value
                if not first:
                    json_data['median wind'][y,w] = 256 * statistics.median(value_list)
 #                   json_data['99th % wind'][y,w] = 256 * (sorted(value_list)[week_99th])
                first = False
                value_list = [value]
                week_prev = w
            else:
                value_list.append(value)
        #total rain, 99th % rain
        week_prev = -1
        first = True
        for i,value in enumerate(hourly_data['rain']):
            y = int(math.floor(i / 8760))
            w = int(math.floor((i % 8760) / 7))
            if w != week_prev:
                #do statistics and append procesed value
                if not first:
                    json_data['total precip'][y,w] = 256 * sum(value_list)
      #              json_data['99th % rain'][y,w] = 256 * (sorted(value_list)[int(math.floor(len(value_list)*0.99))])
                first = False
                value_list = [value]
                week_prev = w
            else:
                value_list.append(value)'''
        
        
        
        #Build data structure to send via JSON
        
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
