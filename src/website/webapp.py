# prototype Panel + Flask app
# Copyright (C) 2020 HWITW project
#
from flask import Flask, render_template, request, Response, send_from_directory
from bokeh.embed import components
#from bokeh.plotting import figure
#import plotly.graph_objs as go
import heatmap
from webauth import requires_auth

# notebooks need this: pn.extension('plotly')
app = Flask(__name__)

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


# Index page
@app.route('/', methods=['GET'] )
@requires_auth
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "Sepal Length"

	# Create the panel
	apanel = heatmap.create_hmap_pn( current_feature_name )
	 
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
	raw_png_data = heatmap.create_station_hmap_png( df_col, df_method )
	return Response( raw_png_data, mimetype='image/png')

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
