# prototype Panel + Flask app
# Copyright (C) 2020 HWITW project
#
from flask import Flask, render_template, request, Response, send_from_directory, jsonify
from bokeh.embed import components
#from bokeh.plotting import figure
#import plotly.graph_objs as go
import heatmap
import smtplib
from email.mime.text import MIMEText
from webauth import requires_auth

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

@app.route('/contact/data', methods=['POST'] )
def contact_json():
	""" STill needs to be wired up to front-end

	Returns:
		[type]: [description]
	"""

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = "[contact form] Test subject.."
	msg['From'] = "contact@localhost"
	msg['To'] = "david@yerrington.net"

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail(me, [you], msg.as_string())
	s.quit()

	return jsonify(app_config)

@app.route('/terms', methods=['GET'] )
def terms():
	return render_template("terms.html")

@app.route('/echarts-demo', methods=['GET'] )
def echarts_demo():
	return render_template("echarts-demo.html")

@app.route('/weather/stations', methods = ['GET'])
def get_stations_json():
	hdat.init2()
	stations = hdat.get_stationlist()
	return jsonify(stations)

@app.route('/weather/init', methods = ['GET'])
def get_init_json():
	""" 
		get_init_json()
		
		This method will return the json version of the initial data states for the webapp.
		  - List of initial stations
		  - List of varibles
		  - List of methods

	Returns:
		json[str]: Converted from mixed type dictionary
	"""
	hdat.init2()
	app_config = hdat.get_init()
	hdat.logging.debug(app_config)
	return jsonify(app_config)

@app.route('/weather/<station_id>', methods = ['GET'] )
def get_weather_json(station_id = 25507):
	result = heatmap.create_heat_df()
	return jsonify(["test"])

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

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
