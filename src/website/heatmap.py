# render a web page heatmap
# Copyright (C) 2020 HWITW project
#
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

# define main columns of interest and verify that they exist
main_column_list = [
    'DATE',
    'HourlyAltimeterSetting',
    'HourlyDewPointTemperature',
    'HourlyDryBulbTemperature',
    'HourlyPrecipitation',
    'HourlyPresentWeatherType',
    'HourlyPressureChange',
    'HourlyPressureTendency',               
    'HourlyRelativeHumidity',
    'HourlySkyConditions',
    'HourlySeaLevelPressure',
    'HourlyStationPressure',
    'HourlyVisibility',
    'HourlyWetBulbTemperature',
    'HourlyWindDirection',
    'HourlyWindGustSpeed',
    'HourlyWindSpeed'
]

def make_column_str( a ):
    the_str = ""
    for i in range( len(a) ):
        the_str += a[i]
        if i < len(a) - 1:
            the_str += ','

    return the_str

numeric_const_pattern = r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"

def objtofloat( a:object ):
    if type(a) == float:
        return a    
    
    if type(a) == str:
        b = re.search(numeric_const_pattern, a)
        if type(b) == type(None):
            return np.nan
        
        c = b.group()
        return float( c )
    
    return np.nan

# clean columns and create a dataframe for the heatmap
def create_heat_df( station_df:pd.DataFrame, column_a:str, method_a:str ):
    df_clean = station_df
    df_clean[ column_a ] = df_clean[ column_a ].apply( objtofloat )
    #homer.info()
    #homer['HourlyStationPressure'].value_counts()
    #homer[ "HourlyStationPressure" ].plot()

    # resample to Daily frequency
    heat_df = df_clean[ [column_a] ]
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

column_init = main_column_list[11]
method_names = [ 'mean', 'min', 'max' ]
method_name_init = method_names[0]

# WARNING: df_column and df_method ARE USER INPUT AND HAVE NOT BEEN SANITIZED. UNSAFE!
def create_station_hmap_png( df_column:str, df_method:str ):
    
    if df_column == None:
        df_column = column_init

    if df_method == None:
        df_method = method_name_init

    # connect and verify columns
    station_name = 'Homer'
    conn = sqlite3.connect("lcd_daily.db")#, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES )

    cur = conn.cursor()
    cur.execute( "SELECT %s FROM daily LIMIT 1" % make_column_str(main_column_list) ) # if this fails we got the columns wrong
    cur.close()

    # get some datas and graph
    sql = "SELECT %s FROM daily ORDER BY DATE" % make_column_str(main_column_list)
    homer = pd.read_sql(
            sql,
            con = conn,
            parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'},
            index_col='DATE' )

    #homer.set_index( 'DATE' )
    return create_hmap_rawpng( homer, station_name, df_column, df_method )

def create_hmap_pn( junk ):
    # create dropdown, init with HourlyStationPressure #11
    column_dropdown = pn.widgets.Select( name='Column', options=main_column_list, value=column_init )
    method_dropdown = pn.widgets.Select( name='Method', options=method_names, value=method_name_init )

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

    column_dropdown.jscallback(
        args={'method_obj':method_dropdown},
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_col=${cb_obj.value}&df_method=${method_obj.value}`;
        """
    )

    method_dropdown.jscallback(
        args={'column_obj':column_dropdown},
        value="""
            var plot_img = document.getElementById('plot_img');
            plot_img.src = `plot0.png?df_col=${column_obj.value}&df_method=${cb_obj.value}`;
        """
    )

    main_pn = pn.Row( column_dropdown, method_dropdown )
    return main_pn
