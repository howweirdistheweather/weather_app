# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
import sys
import io
import re
import pandas as pd
import numpy as np
import sqlalchemy

import matplotlib       # Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')   # ..must do this before import pyplot
from matplotlib import pyplot
from matplotlib.colors import LinearSegmentedColormap

import seaborn
import panel as pn

#seaborn.set()
#pn.extension()

class HData:

    def __init__( self ):
        self.db_conn_str         = 'postgresql://hwitw:hwitw@localhost:5432/hwitw_lake'
        self.station_list        = None
        self.station_id          = '0'
        self.main_column_list    = None #['none','none2']
        self.column_init         = 'nocol'
        self.method_names        = [ 'MEDIAN','AVG', 'MIN', 'MAX' ]
        self.method_name_init    = self.method_names[0]        
        self.range_v1            = 0.33     # color slider range value 1
        self.range_v2            = 0.66     # slider value 2
        pass

    def init2( self ):
        if self.station_list == None:
            self.get_stationlist()

        if self.main_column_list == None:
            self.get_collist()

        create_pg_median( self.db_conn_str )  

    def set_station_id( self, s_id:str ):
        if s_id != None:
            self.station_id = s_id

    # get the station list
    def get_stationlist( self ):
        sys.stderr.write( 'dbg: get_stationlist\n' )     
        # Connect to the PostgreSQL database
        conn = sqlalchemy.create_engine( self.db_conn_str )

        # get the column list
        sql = "SELECT DISTINCT station_id FROM lcd_incoming"
        station_df = pd.read_sql(
                sql,
                con = conn )

        stations = station_df['station_id'].astype( str )
        self.station_list = stations.values.tolist()
        self.station_id = self.station_list[0]

    # get the column list
    def get_collist( self ):
        sys.stderr.write( 'dbg: get_collist\n' )
        # Connect to the PostgreSQL database
        conn = sqlalchemy.create_engine( self.db_conn_str )

        # get the column list
        sql = "SELECT * FROM lcd_incoming LIMIT 1"
        homer = pd.read_sql(
                sql,
                con = conn,
                parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'},
                index_col='DATE' )

        self.main_column_list = list(homer.columns)
        self.column_init = self.main_column_list[1]


# this gives us a median() function in postgres
def create_pg_median( db_conn_str:str ):

    # func_sql = """CREATE OR REPLACE FUNCTION _final_median(numeric[])
    #        RETURNS numeric AS
    #         $$
    #         SELECT AVG(val)
    #         FROM (
    #             SELECT val
    #             FROM unnest($1) val
    #             ORDER BY 1
    #             LIMIT  2 - MOD(array_upper($1, 1), 2)
    #             OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
    #         ) sub;
    #         $$
    #         LANGUAGE 'sql' IMMUTABLE;

    #         DROP AGGREGATE IF EXISTS median(numeric);
    #         CREATE AGGREGATE median(numeric) (
    #         SFUNC=array_append,
    #         STYPE=numeric[],
    #         FINALFUNC=_final_median,
    #         INITCOND='{}'
    #         );"""

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

def create_hmap_rawpng( station_df:pd.DataFrame, hdat:HData, col_a:str, met_a:str ):
    hdf = create_heat_df( station_df, col_a, met_a )
    hvmin = hdf.values.min()
    hvmax = hdf.values.max()

    # setup colors
    hcolor0 = '#edf8b1'
    hcolor1 = '#7fcdbb'
    hcolor2 = '#2c7fb8'

    hb0 = 0.0        
    hb1 = hdat.range_v1
    hb2 = hdat.range_v2
    hb3 = 1.0

    #boundaries = [ 0.0, 0.33, 0.33, 0.66, 0.66, 1.0 ]#hdf.values.min, hdf.values.max ]  # custom boundaries        
    boundaries = [ hb0, hb1, hb1, hb2, hb2, hb3 ]
    hex_colors = [ hcolor0, hcolor0, hcolor1, hcolor1, hcolor2, hcolor2 ]
    colors=list(zip(boundaries, hex_colors))
    custom1_map = LinearSegmentedColormap.from_list(
        name='custom1',
        colors=colors,
    )

    # create plot
    fig = pyplot.figure(figsize=(4.8,4))#, dpi=500)
    ax = fig.subplots()
    ax.set_title( hdat.station_id + " - " + col_a + " - " + met_a, fontsize=8 )        
    hmap = seaborn.heatmap( 
        ax=ax, 
        data=hdf,
#            vmin=hdat.range_v0,
#            vmax=hdat.range_v3,
        linewidths=0.65, 
        linecolor='white', 
        cmap=custom1_map, 
        square=True, 
        cbar=True,
        rasterized=True )

    # set cbar font size
    cbar = ax.collections[0].colorbar      
    cbar.ax.tick_params(labelsize=6)

    ax.invert_yaxis()
    #seaborn.set( font_scale=0.5 )
    hmap.set( xlabel=None, ylabel=None )

    # calc locations of week tick marks
    week_tick = []
    for i in range(0,12):
        week_tick.append( month_to_week( i+1 ) )

    hmap.set_xticks( week_tick )
    hmap.set_xticklabels( ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], fontsize=6, rotation=90 )
    hmap.set_yticklabels( hmap.get_ymajorticklabels(), fontsize=6, rotation=10 )
    #tick_spacing = 4
    #ax.xaxis.set_major_locator( matplotlib.ticker.MultipleLocator( tick_spacing ) )
    fig.tight_layout()

    # create png
    buf = io.BytesIO()
    fig.savefig( buf, format='png', dpi=400 )
    pyplot.close( fig )
    data=buf.getvalue()

    return data

def create_station_hmap_png( hdat:HData, df_column:str, df_method:str ):
    # SANITIZE df_column and df_method. these are user input so we need to watch
    # out for SQL injection type attacks
    if df_column == None or df_column not in hdat.main_column_list:
        df_column = hdat.column_init

    if df_method == None or df_method not in hdat.method_names:
        df_method = hdat.method_name_init

    # Connect to the PostgreSQL database
    conn = sqlalchemy.create_engine( hdat.db_conn_str )    

    agg_str = """%s("%s")""" % (df_method, df_column)    

    sql = """SELECT DATE_PART('year', "DATE") as "theyear",
                    DATE_PART('week', "DATE") as "theweek",
                    %s AS "xval" """ % agg_str + """
                    from lcd_incoming
                    where station_id = %(psid)s group by theyear, theweek"""
    stationdf = pd.read_sql(
        sql,
        con = conn,
        params= { 'psid':hdat.station_id } )

    return create_hmap_rawpng( stationdf, hdat, df_column, df_method )

def create_hmap_pn( hdat:HData ):
    # create widgets
    station_dropdown = pn.widgets.Select( name='Station', options=hdat.station_list, value=hdat.station_id )
    column_dropdown = pn.widgets.Select( name='Column', options=hdat.main_column_list, value=hdat.column_init )
    method_dropdown = pn.widgets.Select( name='Method', options=hdat.method_names, value=hdat.method_name_init )   

    range_slider = pn.widgets.RangeSlider( name='Range', start=0.0, end=1.0, value=( hdat.range_v1, hdat.range_v2), step=0.05 )

    station_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown,
               'range_obj':range_slider
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}&rv1=${range_obj.value[0]}&rv2=${range_obj.value[1]}`;
        """
    )

    column_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown,
               'range_obj':range_slider
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}&rv1=${range_obj.value[0]}&rv2=${range_obj.value[1]}`;
        """
    )

    method_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown,
               'range_obj':range_slider
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}&rv1=${range_obj.value[0]}&rv2=${range_obj.value[1]}`;
        """
    )

    range_slider.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown,
               'range_obj':range_slider
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}&rv1=${range_obj.value[0]}&rv2=${range_obj.value[1]}`;
        """
    )

    main_pn = pn.Column(
        pn.Row( station_dropdown, column_dropdown, method_dropdown, width=700 ),
        pn.Row( range_slider, width=200 )
    )
    return main_pn
