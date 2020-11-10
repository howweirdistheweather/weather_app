# prototype Panel + Flask app
# Copyright (C) 2020 HWITW project
#
from flask import Flask, render_template, request, Response, send_from_directory
from bokeh.embed import components
#from bokeh.plotting import figure
#import plotly.graph_objs as go
import html
import heatmap
from webauth import requires_auth
import folium
import folium.plugins
import sqlalchemy
import pandas as pd

# notebooks need this: pn.extension('plotly')
app = Flask(__name__)
hdat = heatmap.HData()

## Static Files Config
@app.route('/js/<path:path>')
def get_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def get_css(path):
    return send_from_directory('static/css', path)

@app.route('/img/<path:path>')
def get_img(path):
    return send_from_directory('static/assets/img', path)

@app.route('/example', methods=['GET'] )
def example():
	return render_template("example.html")

@app.route('/about', methods=['GET'] )
def about():
	return render_template("about.html")

@app.route('/team', methods=['GET'] )
def team():
	return render_template("team.html")

@app.route('/contact', methods=['GET'] )
def contact():
	return render_template("contact.html")

@app.route('/terms', methods=['GET'] )
def terms():
	return render_template("terms.html")


# Index page
@app.route('/', methods=['GET'] )
@requires_auth
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "Sepal Length"

	# init if not already
	hdat.init2()

	# Create the panel	
	apanel = heatmap.create_hmap_pn( hdat )
	 
	# Embed into HTML via Flask Render
	bokeh_script, bokeh_div = components( apanel.get_root() )
	return render_template( 
		"index.html", 
		#pn_embed=apanel.embed(),
		bokeh_script=bokeh_script, 
		bokeh_div=bokeh_div,
		current_feature_name=current_feature_name
	)

# png plot
@app.route('/plot0.png')
@requires_auth
def plot0():
	# init if not already
	hdat.init2()

	hdat.set_station_id( request.args.get( 'df_station' ) )
	df_col = request.args.get( 'df_col' )
	df_method = request.args.get( 'df_method' )
	hdat.range_v1 = request.args.get( 'rv1', type=float, default=0.33 )
	hdat.range_v2 = request.args.get( 'rv2', type=float, default=0.66 )

	raw_png_data = heatmap.create_station_hmap_png( hdat, df_col, df_method )
	return Response( raw_png_data, mimetype='image/png')

# station map
@app.route('/station_map')
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
