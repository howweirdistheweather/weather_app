# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
import sys
import io
import re
import pandas as pd
import numpy as np
import sqlite3, errno, os

import matplotlib       # Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')   # ..must do this before import pyplot
from matplotlib import pyplot

import seaborn
import panel as pn

#seaborn.set()
#pn.extension()

import psycopg2

class HData:

    def __init__( self ):
        self.db_conn_str         = 'host=localhost dbname=hwitw_lake user=hwitw password=hwitw' 
        self.station_list        = None
        self.station_id          = '0'        
        self.main_column_list    = None #['none','none2']
        self.column_init         = 'nocol'
        self.method_names        = [ 'mean', 'min', 'max' ]
        self.method_name_init    = self.method_names[0]
        pass

    def init2( self ):
        if self.station_list == None:
            self.get_stationlist()

        if self.main_column_list == None:
            self.get_collist()        

    def set_station_id( self, s_id:str ):
        if s_id != None:
            self.station_id = s_id

    # get the station list
    def get_stationlist( self ):
        sys.stderr.write( 'dbg: get_stationlist\n' )
        # Establish a connection to the database by creating a cursor object
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(  self.db_conn_str )
        # Create a new cursor
        cur = conn.cursor()

        # get the column list
        sql = "SELECT DISTINCT station_id FROM lcd_incoming"
        station_df = pd.read_sql(
                sql,
                con = conn )
#        sys.stderr.write(stations['station_id'].astype( str ) )
        stations = station_df['station_id'].astype( str )
        self.station_list = stations.values.tolist()
        
        self.station_id = self.station_list[0]
            
        cur.close()
        conn.close()    

    # get the column list
    def get_collist( self ):
        sys.stderr.write( 'dbg: get_collist\n' )
        # Establish a connection to the database by creating a cursor object
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(  self.db_conn_str )
        # Create a new cursor
        cur = conn.cursor()

        # get the column list
        sql = "SELECT * FROM lcd_incoming LIMIT 1"
        homer = pd.read_sql(
                sql,
                con = conn,
                parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'},
                index_col='DATE' )

        #homer.set_index( 'DATE' )
        self.main_column_list = list(homer.columns)
        self.column_init = self.main_column_list[1]
            
        cur.close()
        conn.close()    


# process station dataframe into a heatmap datagrame
def create_heat_df( station_df:pd.DataFrame, column_a:str, method_a:str ):
 #   df_clean = station_df
#    df_clean[ column_a ] = df_clean[ column_a ].apply( objtofloat )
    #homer.info()
    #homer['HourlyStationPressure'].value_counts()
    #homer[ "HourlyStationPressure" ].plot()

    # resample to Daily frequency
    heat_df = station_df[ [column_a] ]
    heat_df = heat_df.resample('D')
    if method_a == 'mean' :
        heat_df = heat_df.mean()
    elif method_a == 'min':
        heat_df = heat_df.min()
    else:
        heat_df = heat_df.max()
#    heat_df = method_a( heat_df ) # call aggregation method
    
    # create year and day columns and pivot
    heat_df['year'] = heat_df.index.year
    heat_df['day'] = heat_df.index.dayofyear
    heat_df = heat_df.pivot( index='year', columns='day', values=column_a )
 
    return heat_df

def create_hmap_rawpng( station_df:pd.DataFrame, station_name:str, col_a:str, met_a:str ):
        hdf = create_heat_df( station_df, col_a, met_a )
        # create panel and plot
        fig = pyplot.figure(figsize=(10,12))        
        ax = fig.subplots()
        ax.set_title( station_name + " - " + col_a + " - " + met_a )
        hmap = seaborn.heatmap( ax=ax, data=hdf, linewidths=0, cmap='PuBuGn' )
        ax.invert_yaxis()
        #fig.tight_layout()
        pyplot.tight_layout()

        buf = io.BytesIO()
        fig.savefig( buf, format='png' )
        pyplot.close( fig )
        data=buf.getvalue()

        return data

# WARNING: df_column and df_method ARE USER INPUT AND HAVE NOT BEEN SANITIZED. UNSAFE!
def create_station_hmap_png( hdat:HData, df_column:str, df_method:str ):
    
    if df_column == None:
        df_column = hdat.column_init

    if df_method == None:
        df_method = hdat.method_name_init

    # Establish a connection to the database by creating a cursor object
    # Connect to the PostgreSQL database
    conn = psycopg2.connect( hdat.db_conn_str )
    # Create a new cursor
    cur = conn.cursor()

    # get some datas and graph
    sql = "SELECT * FROM lcd_incoming WHERE station_id=%(p0)s ORDER BY \"DATE\""
    homer = pd.read_sql(
            sql,
            con = conn,
            params = { 'p0':hdat.station_id },
            parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'},
            index_col='DATE' )

    #homer.set_index( 'DATE' )

    cur.close()
    conn.close()
    sys.stderr.write( hdat.station_id )
    return create_hmap_rawpng( homer, hdat.station_id, df_column, df_method )

def create_hmap_pn( hdat:HData ):

    # create dropdowns
    station_dropdown = pn.widgets.Select( name='Station', options=hdat.station_list, value=hdat.station_id )
    column_dropdown = pn.widgets.Select( name='Column', options=hdat.main_column_list, value=hdat.column_init )
    method_dropdown = pn.widgets.Select( name='Method', options=hdat.method_names, value=hdat.method_name_init )

    # @pn.depends( column_dropdown.param.value, watch=True )
    # def on_column( col_a ):
    #     current_method = method_dropdown.value
    #     print( col_a )
        #main_pn[1] = create_hmap( col_a, current_method )

    # @pn.depends( method_dropdown.param.value, watch=True )
    # def on_method( met_name_a ):
    #     current_column = column_dropdown.value
    #     print( met_name_a )
        #main_pn[1] = create_hmap( current_column, met_name_a )

    station_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}`;
        """
    )

    column_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}`;
        """
    )

    method_dropdown.jscallback(
        args={ 'station_obj':station_dropdown,
               'column_obj':column_dropdown,
               'method_obj':method_dropdown
        },
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_station=${station_obj.value}&df_col=${column_obj.value}&df_method=${method_obj.value}`;
        """
    )

    main_pn = pn.Row( station_dropdown, column_dropdown, method_dropdown )
    return main_pn
