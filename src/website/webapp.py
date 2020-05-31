# prototype Panel + Flask app
# Copyright (C) 2020 HWITW project
#
from flask import Flask, render_template, request, Response
from bokeh.embed import components
#from bokeh.plotting import figure
#import plotly.graph_objs as go
import heatmap
from webauth import requires_auth

# notebooks need this: pn.extension('plotly')
app = Flask(__name__)
hdat = heatmap.HData()

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
	df_col = request.args.get("df_col")
	df_method = request.args.get( "df_method" )	
	raw_png_data = heatmap.create_station_hmap_png( hdat, df_col, df_method )
	return Response( raw_png_data, mimetype='image/png')

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
