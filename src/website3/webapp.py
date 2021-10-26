# prototype Flask app server
# Copyright (C) 2021 HWITW project
#
from flask import Flask, render_template, request, Response, send_from_directory
import html
import json
import wxdata
from webauth import requires_auth
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # CORS headers to make devel easier


# return var data as json
@app.route('/wxapp/getwxvar')
@requires_auth
def getwxvarjson():
	var_lat = request.args.get( 'vlat' )
	var_long = request.args.get( 'vlong' )

	json_data = wxdata.get_wxvar( var_lat, var_long )
	
	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	print(resp)	#debug
	return resp

# return reading/weather variables as json
@app.route('/wxapp/wxvars')
@requires_auth
def wxvarsjson():
	json_data = json.dumps( wxdata.get_wxvar_list() )

	resp = Response( json_data, mimetype='application/json')
	resp.headers['Access-Control-Allow-Origin'] = '*' # get around CORS during development
	print(resp)	#debug
	return resp

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
