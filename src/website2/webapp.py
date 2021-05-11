# prototype Panel + Flask app
# Copyright (C) 2020 HWITW project
#
from flask import Flask, render_template, request, Response, send_from_directory
from bokeh.embed import components
#from bokeh.plotting import figure
#import plotly.graph_objs as go
import html
import json
import heatmap
from webauth import requires_auth
import folium
import folium.plugins
import sqlalchemy
import pandas as pd

from flask_cors import CORS

# notebooks need this: pn.extension('plotly')
app = Flask(__name__)
CORS(app) # CORS headers to make devel easier
hdat = heatmap.HData( fake_data=True )


# return plot data as json
@app.route('/wxapp/plot0.json')
@requires_auth
def plot0json():
	station_id = request.args.get( 'df_station' )
	df_col = request.args.get( 'df_col' )
	df_method = request.args.get( 'df_method' )
	#hdat.range_v1 = request.args.get( 'rv1', type=float, default=0.33 )
	#hdat.range_v2 = request.args.get( 'rv2', type=float, default=0.66 )

	json_data = heatmap.create_station_hmap_json( hdat, station_id, df_col, df_method )
	
	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	return resp

# return aggregation methods list as json
@app.route('/wxapp/aggmethods.json')
@requires_auth
def aggmethodsjson():
	json_data = hdat.get_aggmethods_json()

	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	return resp

# return column/reading-type list as json
@app.route('/wxapp/readingtypes.json')
@requires_auth
def readingtypesjson():
	json_data = hdat.get_collist_json()

	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	return resp

# return station metadata table as json
@app.route('/wxapp/stationsmeta.json')
@requires_auth
def stationsmetajson():
	sm_type = request.args.get( 'sm_type', default='allco' )
	sm_co = request.args.get( 'sm_co', default='D33DB33F' )
	sm_state = request.args.get( 'sm_state', default='D33DB33F' )
	
	json_data = hdat.get_stationsmeta_json( sm_type, sm_co, sm_state )

	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	return resp

# station map
@app.route('/wxapp/station_map')
@requires_auth
def station_map():
	### query station metadata table
	# Connect to the PostgreSQL database
	conn = sqlalchemy.create_engine( hdat.db_conn_str )    

	# get station meta data
	station_data = pd.read_sql(
		sql = "SELECT * FROM stations_in", # 16131 WHERE \"STATE\"='AK' LIMIT 800",
		con = conn
		#params = { 'pwban':hdat.station_id }
	)
	# create follium map	
	#lat, long = station_data[ station_data['stationname'].str.contains( 'Seldovia' )][['lat','lon']].values[0]
	lat = 59
	lon = -151

	f_map = folium.Map(
    	location   = (lat, lon),
    	tiles      = 'Stamen Terrain',
    	zoom_start = 6
	)

	# for automatic zoom clustering we use a markercluster. we add the markers to it instead of to the map object.
	# ..and now we are using FastMarkerCluster which can handle thousands of markers.
	marker_data = []
	marker_cluster = folium.plugins.FastMarkerCluster( name='ICD Stations', data=marker_data ).add_to( f_map )

	## Add markers from DataFrame
	def apply_markers(row):
		# some station names have backticks and other weird stuff I guess. It needs to be proper html.
		# if no name is present use stationid as the name
		sname = row['STATIONNAME']
		if sname == None:
			sname = row['STATIONID']
		else:
    		# folium chokes on backticks for some reason. get rid of any.
			sname = sname.replace( '`', '' )			
			#sname = html.escape( sname, quote=True )
			
		# create and add tooltip
		mark_lat = row['LAT']
		mark_lon = row['LON']
		if not pd.isnull( mark_lat ) and not pd.isnull( mark_lon ):
			tooltip_meta = f"<div style='width: 300px;'><strong>{sname}</strong></br>"
			tooltip_meta += f"id: {row['STATIONID']}</br> elev/m: {row['ELEVM']}</br>"
			tooltip_meta += f"start: {row['BEGIN']}</br> end: {row['END']}</div>"
			folium.Marker(location=[mark_lat,mark_lon], popup=folium.Popup( tooltip_meta, parse_html=False ) ).add_to( marker_cluster ) #add_to( f_map )

	station_data.apply( apply_markers, axis = 1 )
	
	return render_template(
		"station_map.html",
		f_map = f_map._repr_html_()
	)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
