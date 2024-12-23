//Copyright 2023 Ground Truth Alaska

//Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
//documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
//rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
//persons to whom the Software is furnished to do so, subject to the following conditions:

//The above copyright notice and this permission notice shall be included in all copies or substantial portions
//of the Software.

//THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
//WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
//COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
//OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

// initialize as an array LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value)of zeros. an empty grid.
const svg = document.getElementById('mySvg');
const tooltip = document.getElementById('tooltip');

function showTooltip(evt, word) {
	tooltip.textContent = word;
	tooltip.style.left = `${evt.pageX}px`;
	tooltip.style.top = `${evt.pageY}px`;
	tooltip.style.display = 'block';
}

function hideTooltip() {
	tooltip.style.display = 'none';
}

function createRandomCircle() {
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  const randomWord = dictionary[Math.floor(Math.random() * dictionary.length)];

  circle.setAttribute('cx', Math.random() * 800); // Adjust for your SVG size
  circle.setAttribute('cy', Math.random() * 600); // Adjust for your SVG size
  circle.setAttribute('r', 20); // Circle radius
  circle.setAttribute('fill', 'blue'); // Circle color

  circle.addEventListener('mousemove', (evt) => showTooltip(evt, 'iouh'));
  circle.addEventListener('mouseout', hideTooltip);

  return circle;
}

var wx_grdata = {"":Array(60).fill().map(() => Array(52).fill(0))}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid

var histo_hights = []
document.onkeydown = function() {
    var key = event.keyCode || event.charCode;
	console.log(key)
	if (key == 80) {
		console.log(prev_states)
	}
	if (key == 18 && event.metaKey && event.shiftKey){
		// command+shift+option
		var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state_dict));
		var dlAnchorElem = document.getElementById('downloadAnchorElem');
		dlAnchorElem.setAttribute("href",     dataStr     );
		dlAnchorElem.setAttribute("download", "state.json");
		dlAnchorElem.click();
	}
	// if (key == 79){
// 		// command+shift+option
// 		var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(start_data));
// 		var dlAnchorElem = document.getElementById('downloadAnchorElem');
// 		dlAnchorElem.setAttribute("href",     dataStr     );
// 		dlAnchorElem.setAttribute("download", "state.json");
// 		dlAnchorElem.click();
// 	}
    if ( key == 8 || key == 46 ) {
        HandleDelete()
		
		saveState()
		redo_states = []
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	if (key == 38) {
		arrowHandler(1)
		if (!is_shifting){
			
		}
		saveState()
		redo_states = []
		is_shifting = true
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	if (key == 40) {
		arrowHandler(-1)
		if (!is_shifting){
			
		}
		saveState()
		redo_states = []
		is_shifting = true
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	if (key == 37) {
		horizontalArrowHandler(-1)
		if (!is_shifting){
			
		}
		saveState()
		redo_states = []
		is_shifting = true
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	if (key == 39) {
		horizontalArrowHandler(1)
		if (!is_shifting){
			
		}
		saveState()
		redo_states = []
		is_shifting = true
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	if (key == 13) {
		for (i in selects){
			select_draws[i].remove();
		}
		selects = []
		select_draws = []
	}
	if (key == 90 && event.metaKey){
		is_undoing = true
		if (event.shiftKey && redo_states.length > 0){
			saveState("undo")
			prev_states.push(state_dict)
			state_dict = redo_states[redo_states.length-1]
			loadState()
			redo_states.splice(-1)
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
		}
		else if (!event.shiftKey && prev_states.length > 0){
			saveState("undo")
			redo_states.push(state_dict)
			state_dict = prev_states[prev_states.length-1]
			loadState()
			prev_states.splice(-1)
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
		}
		is_undoing = false
	}
	if (document.getElementById("myModal").style.display == "block"){
//		update_txt()
	}
};

window.addEventListener("keydown", function(e) {
    if(["Space","ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].indexOf(e.code) > -1) {
        e.preventDefault();
    }
}, false);
function download(filename, text) {
	var element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
	element.setAttribute('download', filename);

	element.style.display = 'none';
	document.body.appendChild(element);

	element.click();

	document.body.removeChild(element);
}
var state_dict = {}
var prev_states = []
var redo_states = []
var is_shifting = false
var is_weigth_sliding = false
var is_range_sliding = false
var is_sensetivity_sliding = false
var is_loading = false
var is_undoing = false
var prev_update = "base"
const offset = 28

var is_trend = false
var lines = []
var year_draw = null
var season_draw = null
var highlights = []
var unit_sets = ['metric','american']
var unit_num = 0
var histo_data = []
var invert_btns = []
var file_names = []
var selected_years = []
var year_covers = []
var selected_seasons = []
var season_covers = []
var covers = []
var bsizes = []
var method_dict = {}
var reading_options = []

var line_opacidy = 0.1
var state_index = null
var maxes = [];
var gridlines = [];
var mins = [];
var prev_maxes = [];
var prev_mins = [];
var doPDO = false
var is_seasonaly_adjusted = false
var color_grads = false
var grid_cells = []
var selects = []
var select_draws = []
var draws = []
var compresed_data = []
var color_data = []
var wx_data = []
var click_data = []
var data_len = 0
var wx_grdata_min = 0.0;
var wx_grdata_max = 1.0;
var wx_range_val0 = 0.33;
var wx_range_val1 = 0.66;
var off_x = 0
var season_hight = 0.5
var sensetivity = 1
var save_clicks_x = []
var save_clicks_y = []
var grid_draw = null
var outlines = []
var reading_dropdowns = []
var direction_dropdowns = []
var method_dropdowns = []
var weight_sliders = []
var click_coords = []
var histograms = []
var weight_setexes = []
var weight_vals = []
var close_btns = []
var measurement_index = 0
let cred_str = 'weird:weather'  // TODO: remove. handy for devel
var wxapp_folder = '/wxapp/'    // base folder/url of python app stuff
var reading_types = []
var method_types = []
var has_reading = false
var all_data = []
var base_data = []
var seasonal_data = []
var fades = []
var short_names = {}
var has_loaded = false
var prevs = []
var PDO = [-2.24, -1.12, -1.55, -0.64, -0.4, -2.07, -1.81, 0.29, 0.86, 0.27, 0.04, -0.57, -1.1, -0.24, -0.89, -0.14, -0.44, -0.74, -0.15, -0.34, -0.4, -1.32, -1.14, -1.14, -0.3, -1.41, -0.15, 0.05, 0.07, 0.11, 0.31, 0.84, -0.26, 1.25, 0.6, 0.03, 1.01, 1.14, -0.04, -0.5, -0.83, -0.88, 0.76, 1.04, -0.49, 0.44, 0.68, 1.32, -0.48, -1.84, -1.13, -1.13, -0.44, 0.38, -0.22, -0.19, -0.35, -0.7, -1.66, -1.03, -1.06, -1.81, -1.73, -1.17, 0.55, 0.92, 0.67, -0.1, -0.36, -0.15, -1.14, -1.88, -2.12] //https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat
var ENSO = [-1.31, 0.45, 0.03, 0.65, -0.45, -1.16, -0.97, 0.6, 0.58, 0.09, -0.13, -0.06, -0.34, 0.44, -0.55, 0.88, 0.46, -0.29, -0.05, 0.72, -0.3, -1.04, 0.96, -0.67, -1.0, -1.24, -0.04, 0.86, 0.03, 0.26, 0.31, -0.17, 0.97, 1.22, -0.32, -0.43, 0.3, 1.37, -0.87, -0.82, 0.18, 0.61, 1.16, 0.88, 0.5, -0.18, -0.61, 1.17, 0.32, -1.24, -0.85, -0.39, 0.35, 0.17, 0.14, -0.02, 0.02, -0.6, -1.09, -0.03, -0.89, -1.34, -0.32, -0.41, -0.02, 1.28, 0.45, -0.5, -0.29, 0.34, -0.59, -1.2, -0.94] //https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php
var start_year = 0
var is_setting = false // dir_net
var is_active = true
var color_lists = [['#dadaeb','#9e9ac8','#54278f'],['#ffffb2','#fecc5c','#e31a1c'],['#1871bc','#f7e3f7','#ef8a62'],['#bdd7e7','#6baed6','#1871bc'],['#bae4b3','#74c476','#006d2c'],['#ffffcc','#b2aa93','#110800'],['#e9a3c9','#f7f7f7','#a1d76a']]
var color_num = 0
var t_weight_vals = []
const input_dict = {"temperature":[-60,131.25,0.75],"ceiling":[0,6375,25], "precipitation":[0,.00255,.00001], "cloud cover":[0,1,0.004]};
//var wxgrid_url = http://localhost:5001/wxapp/getwxvar?lat=1000&lon=1000
var wxgrid_url = `/wxapp/getwxvar`;
var urlParams = new URLSearchParams(window.location.search);
var tutorial = urlParams.get('tutorial');
if (tutorial != '0' && tutorial != null){
	tutorial = parseInt(tutorial)
	target_state = {"is_trend":true,"sensetivity":7,"is_seasonaly_adjusted":true,"mins":[55,41],"maxes":[69,86],"wx_grdata_min":0,"wx_grdata_max":1,"wx_range_val0":0.33,"wx_range_val1":0.66,"click_coords":[{"13":0,"123":0,"155":62.5,"268":62.5},{"13":0,"95":0,"189":62.5,"268":62.5}],"weight_vals":[0.3543,0.6456999999999999],"measurement_index":1,"reading_types":["temperature","wind"],"method_types":["avg","speed_avg"],"prevs":[0.3543,0.6456999999999999],"doPDO":false,"line_editing":true,"color_num":0,"unit_num":0}
} else {
	tutorial = false
}
console.log(tutorial)
var lat = urlParams.get('lat');
if (lat == null || tutorial){
	lat = 59.44
}
var lon = urlParams.get('lon');
if (lon == null || tutorial){
	lon = -151.7
}

var querrySTR = urlParams.get('state')
if (!querrySTR || querrySTR == "0" || tutorial){
	// state_dict = {
	// 	'is_trend':false,
	// 	'sensetivity':1,
	// 	'is_seasonaly_adjusted':false,
	// 	'mins':[51],
	// 	'maxes':[74],
	// 	'wx_grdata_min':0,
	// 	'wx_grdata_max':1,
	// 	'wx_range_val0':0.33,
	// 	'wx_range_val1':0.66,
	// 	'click_coords':{13:0,115:0,165:62.5,267:62.5},
	// 	'weight_vals':[1],
	// 	'measurement_index':0,
	// 	'reading_types':['temperature'],
	// 	'method_types':['avg'],
	// 	'prevs':[1],
	// 	'doPDO':false,
	// 	'line_editing':false,
	// 	'color_num':0,
	// 	'unit_num':0
	// }
	// updateQuerry([false,1,false,[51],[74],0,1,0.33,0.66,{13:0,115:0,165:62.5,267:62.5},[1],0,['temperature'],['avg'],[1],false,false,0,0])
	var url = new URL(window.location.href);
	url.searchParams.set("state","[false,1,āăą[51],[74ď0Ć,0.33ė.66Đ{\"13\":ĕĢ15ĥħ16Ī:62.5,\"267ĥıĳ}ď[ĎėĐ0ľŃĐŀĉĄĈĂŉĕŃ");
	window.history.pushState(null, null, url);
}
urlParams = new URLSearchParams(window.location.search);
querrySTR = urlParams.get('state')
var url = wxgrid_url+`?lat=${lat}&lon=${lon}`
fetch(url , {   method:'GET',
                        headers: {'Authorization': 'Basic ' + btoa(cred_str)} 
                    }
)
.then(
    function( response ) {
        if ( response.status !== 200 ) {
            console.warn('Problem with fetch wxgrid. Status Code: ' + response.status );
            return;
        }

        response.json().then(
            function(data) {
                // parse JSON and determine some stuff
                start_data = data;//JSON.parse( data.response );
				//start_data = data_temp
				start_year = start_data["data_specs"]["start_year"];
				document.getElementById( 'location' ).innerHTML = start_data["data_specs"]["Name"];
				compresion_types = start_data["compression"];
				compresion = {}
				start_data = start_data["variables"];
				base_data = {}
				for (mesurment of Object.keys(start_data)){
					compresion[mesurment] = {}
					base_data[mesurment] = {}
					short_names[mesurment] = {}
					for (func of Object.keys(start_data[mesurment])){
						compresion[mesurment][func] = compresion_types[start_data[mesurment][func]["compression"]]
						base_data[mesurment][func] = []
						short_names[mesurment][func] = start_data[mesurment][func]["short_name"]
						for (var i = 0; i < start_data[mesurment][func]["data"].length; i++){
							base_data[mesurment][func].push([])
							for (var j = 0; j < start_data[mesurment][func]["data"][i].length; j++){
								base_data[mesurment][func][i].push(0)
								if (start_data[mesurment][func]["data"][i][j] == 255 || start_data[mesurment][func]["data"][i][j] == null){
									base_data[mesurment][func][i][j] = null
								}
								else {
									base_data[mesurment][func][i][j] = start_data[mesurment][func]["data"][i][j]
								}
							}
						}
					}
				}
				cropped_data = {}
				for (mesurment of Object.keys(base_data)){
					cropped_data[mesurment] = {}
					for (func of Object.keys(base_data[mesurment])){
						cropped_data[mesurment][func] = []
						track_data = []
						for (var i = 0; i < base_data[mesurment][func].length; i++){
							temp_list = []
							has_found = false
							for (var j = 0; j < base_data[mesurment][func][i].length; j++){
								if (base_data[mesurment][func][i][j] != null){
									has_found = true
								} 
								temp_list.push(base_data[mesurment][func][i][j])
							}
							track_data.push(temp_list)
							if (has_found){
								cropped_data[mesurment][func].push(...track_data)
								track_data = []
							}
						}
					}
				}
				seasonal_data = doSesonalCompression(cropped_data)
				all_data = cropped_data
				reading_options = Object.keys(all_data)
				for (var i=0; i < reading_options.length; i++){
					method_dict[reading_options[i]] = Object.keys(all_data[reading_options[i]])
				}
				for (year of cropped_data[reading_options[0]][method_dict[reading_options[0]][0]]){
					if (year[0]){
						data_len ++
					}
				}
				unitNamesHandaler()
				unitMulHandaler()
				makeNewMeasurmeant(0,false)
				if (querrySTR) {
					loadFromeQuerry(querrySTR)
				}
				
				// else {
				// 	saveState()
				// 	state_dict = {
				// 		'is_trend':false,
				// 		'sensetivity':1,
				// 		'is_seasonaly_adjusted':false,
				// 		'mins':[51],
				// 		'maxes':[74],
				// 		'wx_grdata_min':0,
				// 		'wx_grdata_max':1,
				// 		'wx_range_val0':0.33,
				// 		'wx_range_val1':0.66,
				// 		'click_coords':{13:0,115:0,165:62.5,267:62.5},
				// 		'weight_vals':[1],
				// 		'measurement_index':0,
				// 		'reading_types':['temperature'],
				// 		'method_types':['avg'],
				// 		'prevs':[1],
				// 		'doPDO':false,
				// 		'line_editing':false,
				// 		'color_num':0,
				// 		'unit_num':0
				// 	}
				// 	loadState()
				// }
				
				has_loaded = true
				//saveState()
            }
        );
    }
)
.catch(function(err) {
    console.error('Fetch Error -', err);
});
function doSesonalCompression(in_data){
	var week_totals = [{},{}]
	for (mesurment of Object.keys(in_data)){
		week_totals[0][mesurment] = {}
		week_totals[1][mesurment] = {}
		for (func of Object.keys(in_data[mesurment])){
			week_totals[0][mesurment][func] = new Array(52).fill(0);
			week_totals[1][mesurment][func] = new Array(52).fill(0);
			for (var i = 0; i < in_data[mesurment][func].length; i++){
				for (var j = 0; j < in_data[mesurment][func][i].length; j++){
					if (in_data[mesurment][func][i][j] != 255 && in_data[mesurment][func][i][j] != null){
						week_totals[0][mesurment][func][j] += in_data[mesurment][func][i][j]
						week_totals[1][mesurment][func][j] += 1
					}
				}
			}
		}
	}
	var out_data = {}
	for (mesurment of Object.keys(in_data)){
		out_data[mesurment] = {}
		for (func of Object.keys(in_data[mesurment])){
			out_data[mesurment][func] = []
			for (var i = 0; i < in_data[mesurment][func].length; i++){
				out_data[mesurment][func].push([])
				for (var j = 0; j < in_data[mesurment][func][i].length; j++){
					out_data[mesurment][func][i].push(0)
					if (in_data[mesurment][func][i][j] == 255 || in_data[mesurment][func][i][j] == null){
						out_data[mesurment][func][i][j] = null
					}
					else {
						out_data[mesurment][func][i][j] = in_data[mesurment][func][i][j]-parseInt(week_totals[0][mesurment][func][j]/week_totals[1][mesurment][func][j])+127
						// if (out_data[mesurment][func][i][j] < 0){
// 							out_data[mesurment][func][i][j] = 0
// 						}
// 						if (out_data[mesurment][func][i][j] > 254){
// 							out_data[mesurment][func][i][j] = 254
// 						}
					}
				}
			}
		}
	}
	return out_data
}
var color_selector = document.getElementById("color_selector")
color_selector.onchange =
		function () {
			if (!is_loading){
				color_num = parseInt(color_selector.value)
				saveState()
				RenderGrid()
			}
		};
var enable_line_editing = document.getElementById("enable_line_editing")
enable_line_editing.onchange =
		function () {
			if (enable_line_editing.checked){
				line_opacidy = 1
			}
			else {
				selects = []
				for (i in select_draws){
					select_draws[i].remove()
				}
				select_draws = []
				line_opacidy = 0.1
			}
			for (let i=0; i<=measurement_index; i++){
				DrawLines(i)
			}
			saveState()
		};
var seasonal_adjust = document.getElementById("seasonal_adjust")
seasonal_adjust.onchange =
		function () {
			is_seasonaly_adjusted = seasonal_adjust.checked
			updateSeasonality(false)
			RenderGrid()
			
			saveState()
			redo_states = []
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
		};
function updateSeasonality(is_load_call){
	if (is_seasonaly_adjusted){
		all_data = seasonal_data
	}
	else {
		all_data = cropped_data
	}
	if (!is_load_call){
		LoadWXGrid();
		RenderGrid()
		if (!is_loading){
			selects = []
			for (select_draw of select_draws){
				select_draw.remove()
			}
			select_draws = []
			for (let num=0; num<=measurement_index; num++){
				if (['dir_modal','dir_net'].includes(method_types[num])){
					click_coords[num] = {}
					click_coords[num][13] = 0
					click_coords[num][mins[num]*2+13] = 0
					click_coords[num][maxes[num]+mins[num]+17] = histo_hights[num]
					click_coords[num][268] = 0
				}
				else {
					click_coords[num] = {}
					click_coords[num][13] = 0
					click_coords[num][mins[num]*2+13] = 0
					click_coords[num][maxes[num]*2+17] = histo_hights[num]
					click_coords[num][268] = histo_hights[num]
				}
				DrawLines(num)
			}
		}
	}
	
}
//var temp = document.getElementById("temp")
// temp.onchange =
// 		function () {
// 			if (temp.checked){
// 				saveState()
// 			}
// 			else {
// 				loadState()
// 			}
// 			LoadWXGrid();
// 			RenderGrid()
// 		};	
var trend = document.getElementById("trend")
trend.onchange =
		function () {
			const was_undoing = is_undoing
			is_undoing = true
			is_trend = trend.checked
			updateTrends(5)
			RenderGrid();
			redo_states = []
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
			is_undoing = was_undoing
			saveState()
		};
function updateTrends(st_sensetivity){
	if (is_trend){
		makeNewElement("sensetivity_slider_holder","div",{"class":"sensetivity_slider","id":"sensetivity_slider"},null);
		noUiSlider.create( document.getElementById('sensetivity_slider'), {
		    start: [st_sensetivity],
		    connect: false,
		    range: {
		        'min': 1,
		        'max': 9
		    },     
		});
		document.getElementById('sensetivity_slider').noUiSlider.on('update', function (values, handle) {
		    sensetivity = Math.round(values[0])
			if (!is_active) {
				return
			}
			if (!is_loading){
				RenderGrid();
				saveState("trend")
			}
			});
	}
	else {
		document.getElementById('sensetivity_slider').remove()
	}
}
var do_PDO = document.getElementById("do_PDO")
do_PDO.onchange =
		function () {
			if (do_PDO.checked){
				doPDO = true
			}
			else {
				doPDO = false
			}
			saveState()
			RenderGrid()
		};
		
var do_PDO = document.getElementById("do_PDO")
do_PDO.onchange =
		function () {
			if (do_PDO.checked){
				doPDO = true
			}
			else {
				doPDO = false
			}
			saveState()
			RenderGrid()
		};
var colorGrads = document.getElementById("color_grad")
colorGrads.onchange =
		function () {
			if (colorGrads.checked){
				color_grads = true
			}
			else {
				color_grads = false
			}
			saveState()
			RenderGrid()
		};
var download = document.getElementById("download");
download.addEventListener("click",downloadData);

var reset = document.getElementById("reset");
reset.addEventListener("click",function () {
	var url = new URL(window.location.href);
	url.searchParams.set("state","0");
	window.history.pushState(null, null, url);
	window.location.reload();
});


var unit_selector = document.getElementById("unit_selector")
unit_selector.onchange =
		function () {
			unit_num = parseInt(unit_selector.value)
			saveState()
			RenderGrid()
		};
var unit_names = {'metric':{'temperature':{'default':'°C'},'relative_humidity':{'default':'%'},'wind':{'default':' m/s','dir_modal':'°','dir_net':'°'},'precipitation':{'default':'cm'},'cloud_cover':{'default':'%'}},'american':{'temperature':{'default':'°F'},'relative_humidity':{'default':'%'},'wind':{'default':' mph','dir_modal':'°','dir_net':'°'},'precipitation':{'default':' in.'},'cloud_cover':{'default':'%'}}};
function unitNamesHandaler(){
	for (unit_set of unit_sets){  
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]])
			for (var j=0; j < method_options.length; j++){ 
				if (unit_names[unit_set][reading_options[i]][method_options[j]] == undefined){
					unit_names[unit_set][reading_options[i]][method_options[j]] = unit_names[unit_set][reading_options[i]]['default']
				}
			}
		}
	}
}
var unit_muls = {'metric':{'temperature':{'default':[1,0,1]},'relative_humidity':{'default':[100,0,0]},'wind':{'default':[1,0,0]},'precipitation':{'default':[100,0,2]},'cloud_cover':{'default':[100,0,0]}},'american':{'temperature':{'default':[9/5,32,1]},'relative_humidity':{'default':[100,0,0]},'wind':{'default':[2.237,0,0],'dir_modal':[1,0,0],'dir_net':[1,0,0]},'precipitation':{'default':[39.37,0,2]},'cloud_cover':{'default':[100,0,0]}}};
function unitMulHandaler(){
	for (unit_set of unit_sets){  
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]])
			for (var j=0; j < method_options.length; j++){ 
				
				if (unit_muls[unit_set][reading_options[i]][method_options[j]] == undefined){
					unit_muls[unit_set][reading_options[i]][method_options[j]] = unit_muls[unit_set][reading_options[i]]['default']
				}
			}
		}
	}
}
//var type_selector = document.getElementById('type_selector')
//type_selector.onchange =
//	function () {
//		if (type_selector.value == "2"){
//			is_active = false
//			for (var i = 0; i < measurement_index; i++) {
//				deleteMeasurement()
///			}
//		}
//	};

var gr_grid = document.getElementById('gr_grid');
gr_grid.addEventListener("click", function () {
	if (!is_active) {
		return
	}
	DetectGridClick(event)
});

var gr_years = document.getElementById('gr_years');
gr_years.addEventListener("click", function () {
	if (!is_active) {
		return
	}
	DetectYearClick(event)
});

var gr_sesonalitys = document.getElementById('gr_sesonalitys');
gr_sesonalitys.addEventListener("click", function () {
	if (!is_active) {
		return
	}
	DetectSeasonClick(event)
});

function compress(num,inputs){
	if (num < -150 || num == null){
		return null
	}
	if (num > inputs[1]){
		num = inputs[1]
	}
	if (num < inputs[0]){
		num = inputs[0]
	}
	return parseInt((num-inputs[0])/inputs[2])
}

function saveState(update_type="base"){
	if (!has_loaded){
		return
	}
	if (is_undoing && update_type != "undo"){
		updateQuerry()
		return
	}
	if ((update_type == "base" || prev_update != update_type) && !is_undoing && update_type != "no_save"){
		prev_states.push(state_dict)
	}
	prev_update = update_type
	var t_click_coords = []
	for (var i = 0; i < click_coords.length; i++){
	    t_click_coords[i] = {...click_coords[i]};
	}
	state_dict = {
		'is_trend':is_trend,
		'sensetivity':sensetivity,
		'is_seasonaly_adjusted':is_seasonaly_adjusted,
		'mins':mins.slice(),
		'maxes':maxes.slice(),
		'wx_grdata_min':wx_grdata_min,
		'wx_grdata_max':wx_grdata_max,
		'wx_range_val0':wx_range_val0,
		'wx_range_val1':wx_range_val1,
		'click_coords':t_click_coords.slice(),
		'weight_vals':weight_vals.slice(),
		'measurement_index':measurement_index,
		'reading_types':reading_types.slice(),
		'method_types':method_types.slice(),
		'prevs':prevs.slice(),
		'doPDO':doPDO,
		'line_editing':enable_line_editing.checked,
		'color_num':color_num,
		'unit_num':unit_num,
		'color_grads':color_grads
	}
	if (tutorial){
		is_matching = true
		for (key of ['is_trend','is_seasonaly_adjusted','measurement_index','doPDO']){
			if (target_state[key] != state_dict[key]){
				console.log(key)
				is_matching = false
			}
		}
		for (key of ['method_types','reading_types']){
			if (JSON.stringify(target_state[key]) != JSON.stringify(state_dict[key])){
				console.log(key)
				is_matching = false
			}
		}
		for (key of ['wx_range_val0','wx_range_val1']){
			if (Math.abs(target_state[key] - state_dict[key]) > 0.02){
				console.log(key)
				is_matching = false
			}
		}
		click_problem = false
		clicks1 = target_state['click_coords']
		clicks2 = state_dict['click_coords']
		if (clicks1.length == clicks2.length){
			for (var i = 0; i < clicks1.length; i++){
				click_list1 = []
				for (var key in clicks1[i]) {
				    if (clicks1[i].hasOwnProperty(key)) {
				        click_list1.push( [parseInt(key), clicks1[i][key] ] );
				    }
				}
				click_list2 = []
				for (var key in clicks2[i]) {
				    if (clicks2[i].hasOwnProperty(key)) {
				        click_list2.push( [parseInt(key), clicks2[i][key] ] );
				    }
				}
				if (click_list2.length == click_list1.length){
					for (var j = 0; j < click_list1.length; j++){
						if (Math.abs(click_list2[j][0] - click_list1[j][0]) > 2 || Math.abs(click_list2[j][1] - click_list1[j][1]) > 2) {
							click_problem = true
						}
					}
				} else {
					click_problem = true
				}
			}
		} else {
			click_problem = true
		}
		if (click_problem){
			console.log('click_coords')
			is_matching = false
		}
		if (target_state['is_trend']){
			if (target_state['sensetivity'] != state_dict['sensetivity']){
				console.log('sensetivity')
				is_matching = false
			}
		}
		weight_problem = false
		weight1 = target_state['weight_vals']
		weight2 = state_dict['weight_vals']
		if (weight1.length == weight2.length){
			for (var i = 0; i < weight1.length; i++){
				if (Math.abs(weight1[i] - weight2[i]) > 0.02){
					weight_problem = true
				}
			}
		}  else {
			weight_problem = true
		}
		if (weight_problem){
			console.log('weight_vals')
			is_matching = false
		}
		if (is_matching){
			console.log('match')
		}
	}
	
	updateQuerry()
}

function getState(){
	var t_click_coords = []
	for (var i = 0; i < click_coords.length; i++){
	    t_click_coords[i] = {...click_coords[i]};
	}
	let state = [is_trend,sensetivity,is_seasonaly_adjusted,mins.slice(),maxes.slice(),wx_grdata_min,
		wx_grdata_max,wx_range_val0,wx_range_val1,t_click_coords.slice(),weight_vals.slice(),measurement_index,
		reading_types.slice(),method_types.slice(),prevs.slice(),doPDO,enable_line_editing.checked,color_num,unit_num,color_grads]
	return state
}

function updateQuerry(state=null){
	if (!state){
		state = getState()
	}
	let r_types = state_dict['reading_types']
	let m_types = state_dict['method_types']
	for (var i = 0; i <= state[11]; i++){
		state[10][i] = Math.round(state[10][i]*100)/100;
		state[14][i] = Math.round(state[14][i]*100)/100;
		r_type = state[12][i]
		state[12][i] = reading_options.indexOf(r_type)
		state[13][i] = method_dict[r_type].indexOf(state[13][i])
	}
	state[7] = Math.round(state[7]*100)/100;
	state[8] = Math.round(state[8]*100)/100;
	//console.log(JSON.stringify(state))
	//console.log(JSON.stringify(state).length)
	//console.log(lzw_encode(JSON.stringify(state)).length)
	let querry = lzw_encode(JSON.stringify(state))
	var url = new URL(window.location.href);
	url.searchParams.set("state", querry);
	window.history.pushState(null, null, url);
}
function loadFromeQuerry(querry) {
	querry = lzw_decode(querry);
	if (querry == null){
		return
	}
	var state = JSON.parse(querry)
	for (var i = 0; i <= state[11]; i++){
		state[12][i] = reading_options[state[12][i]]
		state[13][i] = method_dict[state[12][i]][state[13][i]]
	}
	state_dict = {
		'is_trend':state[0],
		'sensetivity':state[1],
		'is_seasonaly_adjusted':state[2],
		'mins':state[3],
		'maxes':state[4],
		'wx_grdata_min':state[5],
		'wx_grdata_max':state[6],
		'wx_range_val0':state[7],
		'wx_range_val1':state[8],
		'click_coords':state[9],
		'weight_vals':state[10],
		'measurement_index':state[11],
		'reading_types':state[12],
		'method_types':state[13],
		'prevs':state[14],
		'doPDO':state[15],
		'line_editing':state[16],
		'color_num':state[17],
		'unit_num':state[18],
		'color_grads':state[19]
	}
	loadState()
}

function lzw_encode(s) {
    var dict = {};
    var data = (s + "").split("");
    var out = [];
    var currChar;
    var phrase = data[0];
    var code = 256;
    for (var i=1; i<data.length; i++) {
        currChar=data[i];
        if (dict[phrase + currChar] != null) {
            phrase += currChar;
        }
        else {
            out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
            dict[phrase + currChar] = code;
            code++;
            phrase=currChar;
        }
    }
    out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
    for (var i=0; i<out.length; i++) {
        out[i] = String.fromCharCode(out[i]);
    }
    return out.join("");
}

// Decompress an LZW-encoded string
function lzw_decode(s) {
    var dict = {};
    var data = (s + "").split("");
    var currChar = data[0];
    var oldPhrase = currChar;
    var out = [currChar];
    var code = 256;
    var phrase;
    for (var i=1; i<data.length; i++) {
        var currCode = data[i].charCodeAt(0);
        if (currCode < 256) {
            phrase = data[i];
        }
        else {
           phrase = dict[currCode] ? dict[currCode] : (oldPhrase + currChar);
        }
        out.push(phrase);
        currChar = phrase.charAt(0);
        dict[code] = oldPhrase + currChar;
        code++;
        oldPhrase = phrase;
    }
    return out.join("");
}
function loadState(){
	is_loading = true
	t_measurement_index = measurement_index
	n_measurement_index = state_dict['measurement_index']
	t_weight_vals = state_dict['weight_vals'].slice()
	measurement_index = t_measurement_index
	if (n_measurement_index < t_measurement_index){
		for (var i = n_measurement_index; i < t_measurement_index; i++){
			deleteMeasurement()
		}
	}
	else {
		for (var i = n_measurement_index; i > t_measurement_index; i--){
			newMeasurementHandeler(null,null,true)
		}
	}
	reset_sliders(measurement_index,true)
	weight_vals = state_dict['weight_vals'].slice()
	mins = state_dict['mins'].slice()
	maxes = state_dict['maxes'].slice()
	sensetivity = state_dict['sensetivity']
	t_is_trend = is_trend
	is_trend = state_dict['is_trend']
	if (t_is_trend){
		document.getElementById('sensetivity_slider').remove()
	}
	document.getElementById("trend").checked = is_trend;
	if (is_trend){
		updateTrends(sensetivity)
	}
	is_seasonaly_adjusted = state_dict['is_seasonaly_adjusted']
	updateSeasonality(true)
	document.getElementById("seasonal_adjust").checked = is_seasonaly_adjusted;
	enable_line_editing.checked = state_dict['line_editing'];
	if (state_dict['line_editing']){
		line_opacidy = 1
	}
	else {
		line_opacidy = 0.1
	}
	doPDO = state_dict['doPDO']
	do_PDO.checked = doPDO;
	color_grads = state_dict['color_grads']
	colorGrads.checked = color_grads;
	color_num = state_dict['color_num']
	color_selector.selectedIndex = color_num
	unit_num = state_dict['unit_num']
	unit_selector.selectedIndex = unit_num
	let t_wx_grdata_min = state_dict['wx_grdata_min']
	let t_wx_grdata_max = state_dict['wx_grdata_max']
	wx_range_val0 = state_dict['wx_range_val0']
	wx_range_val1 = state_dict['wx_range_val1']
	generateSlider(wx_range_val0*100,wx_range_val1*100)
	let t_reading_types = state_dict['reading_types'].slice()
	let t_method_types = state_dict['method_types'].slice()
	reading_types = state_dict['reading_types'].slice()
	method_types = state_dict['method_types'].slice()
	for (var i = 0; i < measurement_index+1; i++){
		let r_index = Object.keys(all_data).indexOf(t_reading_types[i]) 
		let m_index = Object.keys(all_data[t_reading_types[i]]).indexOf(t_method_types[i]) 
		LoadReadingDropdown(i,r_index,m_index)
	}
	click_coords = []
	is_loading = false
	let t_click_coords = state_dict['click_coords']
	for (var i = 0; i < t_click_coords.length; i++){
	    click_coords.push({...t_click_coords[i]})
	}
	for (var i = 0; i < measurement_index+1; i++){
		DrawLines(i)
	}
	LoadWXGrid()
	RenderGrid()
	saveState("no_save")
}

function downloadData(){
	let d_reading_options = Object.keys(all_data)
	let d_method_options = []
	for (var i = 0; i < d_reading_options.length; i++){
		d_method_options.push(Object.keys(all_data[d_reading_options[i]]))
	}
	let num_years = all_data[d_reading_options[0]][d_method_options[0][0]].length
	let data_len = num_years*52
	download_data = []
	for (var i = 0; i < data_len+1; i++){
		download_data.push([])
	}
	download_data[0].push('')
	for (var i = 0; i < num_years; i++){
		for (var j = 0; j < 52; j++){
			
			month_lenghths = [31,28,31,30,31,30,31,31,30,31,30,31]
			var day = j*7
			var display_day = null
			var month = null
			for (k=0; k<month_lenghths.length; k++){
				if (day < month_lenghths.slice(0,k).reduce((a, b) => a + b, 0)){
					month = k-1
					display_day = day - month_lenghths.slice(0,k-1).reduce((a, b) => a + b, 0)
					break;
				}
			}
			if (month == null){
				display_day = day - month_lenghths.slice(0,11).reduce((a, b) => a + b, 0)
				month = 11
			}
			let months_txt = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
			var year = i+parseInt(start_year) 
			txt = (display_day+1)+'/'+months_txt[month]+'/'+year
			if (unit_sets[unit_num] == "american"){
				txt = months_txt[month]+'/'+(display_day+1)+'/'+year
			}
			day = j*7+6
			var display_day = null
			var month = null
			for (k=0; k<month_lenghths.length; k++){
				if (day < month_lenghths.slice(0,k).reduce((a, b) => a + b, 0)){
					month = k-1
					display_day = day - month_lenghths.slice(0,k-1).reduce((a, b) => a + b, 0)
					break;
				}
			}
			if (month == null){
				display_day = day - month_lenghths.slice(0,11).reduce((a, b) => a + b, 0)
				month = 11
			}
			txt2 = (display_day+1)+'/'+months_txt[month]+'/'+year
			if (unit_sets[unit_num] == "american"){
				txt2 = months_txt[month]+'/'+(display_day+1)+'/'+year
			}
			download_data[i*52+j+1].push(txt+"-"+txt2);
		}
	}
	for (var m_opt = 0; m_opt < d_reading_options.length; m_opt++){
		for (var d_opt = 0; d_opt < d_method_options[m_opt].length; d_opt++){
			for (var s_adj = 0; s_adj < 2; s_adj++){
				download_data[0].push(['','Seasonaly adjusted '][s_adj]+short_names[d_reading_options[m_opt]][d_method_options[m_opt][d_opt]]+' '+d_reading_options[m_opt])
				for (var i = 0; i < num_years; i++){
					for (var j = 0; j < 52; j++){
						let data = []
						if (s_adj == 1) {
							data = seasonal_data
						}
						else {
							data = cropped_data
						}
						let r_opt_t = d_reading_options[m_opt]
						let m_opt_t = d_method_options[m_opt][d_opt]
						var mul = 1
						var expon = 1
						if (compresion[r_opt_t][m_opt_t]["type"] == "parabolic") {
							expon = 2
						}
						if (data[r_opt_t][m_opt_t][i][j] == null){
							txt = null
						}
						else {
							let value = parseFloat(((((data[r_opt_t][m_opt_t][i][j]*compresion[r_opt_t][m_opt_t]["scale"])**expon)*unit_muls[unit_sets[unit_num]][r_opt_t][m_opt_t][0])*mul-(((127*compresion[r_opt_t][m_opt_t]["scale"])**expon)*unit_muls[unit_sets[unit_num]][r_opt_t][m_opt_t][0])*mul).toFixed(2))
							var st_txt = ''
							if (s_adj == 1){
								if (value > 0){
									st_txt = '+'
								}
							}
							txt = st_txt+parseFloat(value).toFixed(2)+unit_names[unit_sets[unit_num]][r_opt_t][m_opt_t]
						}
						download_data[i*52+j+1].push(txt)
					}
				}
			}
		}
	}
	download_data[0].push('User metric')
	for (var i = 0; i < num_years; i++){
		for (var j = 0; j < 52; j++){
			download_data[i*52+j+1].push(compresed_data[i][j])
		}
	}
	let csvContent = "data:text/csv;charset=utf-8,"
	    	+ download_data.map(e => e.join(",")).join("\n");
	var encodedUri = encodeURI(csvContent);
	var link = document.createElement("a");
	link.setAttribute("href", encodedUri);
	link.setAttribute("download", "HWITW_data.csv");
	document.body.appendChild(link); // Required for FF

	link.click();
}

function makeNewElement(id, type, atributes, txt) {
	var theDiv = document.getElementById(id);
	var content = document.createElement(type);
	var atibutes_to_set = Object.keys(atributes);
	for (atibute_to_set of atibutes_to_set) {
		content.setAttribute(atibute_to_set, atributes[atibute_to_set]);
	}
	theDiv.appendChild(content);
	if (txt != null) {
		content.innerHTML = txt
	}
}
function makeNewMeasurmeant(curent_id_num,is_load_call) {
	click_coords.push({})
	histo_hights.push(0)
	lines.push([])
	draws.push(null)
	maxes.push[0]
	mins.push[0]
	prev_maxes.push[0]
	prev_mins.push[0]
	makeNewElement("histos","div",{"style":"text-align: center;","id":"histo"+curent_id_num},null);
	makeNewElement("measurements","div",{"style":"text-align: center;","id":"measurement"+curent_id_num},null);
	makeNewElement("measurement"+curent_id_num,"div",{"id":"histogram"+curent_id_num},null);
	histograms.push(document.getElementById('histogram'+curent_id_num));
	
	AddClickHandler(curent_id_num)
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-reading_dropdown"+curent_id_num},null);
	reading_dropdowns.push(document.getElementById('gr-reading_dropdown'+curent_id_num));
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-method_dropdown"+curent_id_num},null);
	method_dropdowns.push(document.getElementById('gr-method_dropdown'+curent_id_num));
	// var was_loading = is_loading
	// is_loading = true
	LoadReadingDropdown(curent_id_num,0,0);
	// is_loading = was_loading
	makeNewElement("measurement"+curent_id_num,"button",{"id":"invert_button"+curent_id_num,"style":"font-size: 12px; height: 19px; background-color: #fff; border-width: thin; border-radius: 2px;"},"invert");
	invert_btns.push(document.getElementById('invert_button'+curent_id_num));
	invert_btns[curent_id_num].addEventListener("click", function() {
		invertHandeler(curent_id_num,true)
		
		saveState()
		redo_states = []
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	});
	makeNewElement("measurement"+curent_id_num,"button",{"id":"close_button"+curent_id_num,"style":"font-size: 12px; height: 19px; background-color: #fff; border-width: thin; border-radius: 2px;"},"X");
	close_btns.push(document.getElementById('close_button'+curent_id_num));
	close_btns[curent_id_num].addEventListener("click", function() {
		deleteSpecificMesurment(curent_id_num)
		
		saveState()
		redo_states = []
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	});

	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+curent_id_num},null);
	makeNewElement("weight_slider_holder"+curent_id_num,"div",{"class":"weight_slider","id":"weight_slider"+curent_id_num},null);
	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+curent_id_num},null);
	makeNewElement("weight_stext_div"+curent_id_num,"div",{"class":"weight_setex","id":"weight_stext"+curent_id_num},null);
	weight_setexes.push(document.getElementById( 'weight_stext'+curent_id_num ));
	prevs.push(100)
	weight_sliders.push(document.getElementById('weight_slider'+curent_id_num));
	weight_vals.push(0)
	noUiSlider.create( weight_sliders[curent_id_num], {
	    start: [100],
	    connect: false,
	    range: {
	        'min': 1,
	        'max': 100
	    },     
	});
	var was_loading = is_loading
	is_loading = true
	weight_sliders[curent_id_num].noUiSlider.on('update', function (values, handle) {
	    var weight_val = values[0] / 100;
	    // update text and redraw wx grid
		if (!is_active) {
			return
		}
		weight_vals[curent_id_num] = parseFloat(weight_val)
	    weight_setexes[curent_id_num].textContent = (weight_val*100).toFixed(0)+'%';
		handleSlider(curent_id_num)
		});
	is_loading = was_loading
	method_dropdowns[curent_id_num].onchange =
		function () {
			if (!is_active) {
				return
			}
    		LoadWXGrid();
			RenderGrid()
			if (['dir_modal','dir_net'].includes(method_types[curent_id_num])){
				click_coords[curent_id_num] = {}
				click_coords[curent_id_num][13] = 0
				click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
				click_coords[curent_id_num][maxes[curent_id_num]+mins[curent_id_num]+17] = histo_hights[curent_id_num]
				click_coords[curent_id_num][maxes[curent_id_num]*2+17] = 0
				click_coords[curent_id_num][268] = 0
			}
			else {
				click_coords[curent_id_num] = {}
				click_coords[curent_id_num][13] = 0
				click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
				click_coords[curent_id_num][maxes[curent_id_num]*2+17] = histo_hights[curent_id_num]
				click_coords[curent_id_num][268] = histo_hights[curent_id_num]
			}
			for (i in selects){
				if (selects[i][1] == measurement_index){
					selects.splice(i);
					select_draws[i].remove();
					select_draws.splice(i);
				}
			}
			
			DrawLines(curent_id_num)
			RenderGrid()
			
			saveState()
			redo_states = []
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
	};
	reading_dropdowns[curent_id_num].onchange =
		function () {
			if (!is_active) {
				return
			}
			LoadMethodDropdown(curent_id_num,0);
			
			saveState()
			redo_states = []
			is_shifting = false
			is_weigth_sliding = false
			is_range_sliding = false
			is_sensetivity_sliding = false
	};
	if (!is_load_call){
		reset_sliders(curent_id_num,is_load_call)
	}
	if (compresion[mesurment][func] == 'direction'){
		click_coords[curent_id_num] = {}
		click_coords[curent_id_num][13] = 0
		click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
		click_coords[curent_id_num][maxes[curent_id_num]+mins[curent_id_num]+17] = histo_hights[curent_id_num]
		click_coords[curent_id_num][maxes[curent_id_num]*2+17] = 0
		click_coords[curent_id_num][267] = 0
	}
	else {
		click_coords[curent_id_num] = {}
		click_coords[curent_id_num][13] = 0
		click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
		click_coords[curent_id_num][maxes[curent_id_num]*2+17] = histo_hights[curent_id_num]
		click_coords[curent_id_num][267] = histo_hights[curent_id_num]
	}
	if (!is_load_call){
		DrawLines(curent_id_num)
	}
}
// make wx_grdata an array of zeros
function ClearWXGridData() {
	compresed_data = []
    wx_grdata = {}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid
	for (dropdown of reading_dropdowns ){
		wx_grdata[dropdown.value] = Array(60).fill().map(() => Array(52).fill(0))
	}
    wx_grdata_min = 0.0;
    wx_grdata_max = 1.0;
	prev_wx_grdata_min = wx_grdata_min
	prev_wx_grdata_max = wx_grdata_max   
}


var measurement_button = document.getElementById('measurement_button');
measurement_button.addEventListener("click", newMeasurementHandeler);

var invert_all_button = document.getElementById('invert_all_button');
invert_all_button.addEventListener("click", function () {
	for (var i = 0; i <= measurement_index; i++) {
		invertHandeler(i,false)
	}
	RenderGrid()
	
	saveState()
	redo_states = []
	is_shifting = false
	is_weigth_sliding = false
	is_range_sliding = false
	is_sensetivity_sliding = false
});

function save_handler() {
	save_recrser(0)
}
function save_recrser(num) {
	fetch( "file:///Users/katmai/Downloads/HWITW"+num+".json", {   method:'GET',
	                        headers: {'Authorization': 'Basic ' + btoa(cred_str)}
	                    }
	)
	.then(
	    function( response ) {
	        if ( response.status !== 200 ) {
				SaveCompleet(num)
	            return;
	        }
	        response.json().then(
	            function(data) {
					file_names.push(data["filename"])
				});
			save_recrser(num+1)
	    }
	)
	.catch(function(err) {
		save(num)
	});
}

function SaveCompleet(num) {
	var data = {"reading_dropdowns":reading_dropdowns,"method_dropdowns":method_dropdowns,"weight_vals":weight_vals,"click_coords":click_coords,"maxes":maxes,"mins":mins,"wx_range_val0":wx_range_val0,"wx_range_val1":wx_range_val1,"filename":num}
	download("HWITW"+num+".json",data)
	document.getElementById("myModal").style.display = "none";
}

function save() {
	document.getElementById("myModal").style.display = "block";
}

function detectMove() {
	if (compresed_data == []) {
		return;
	}
	if (event.offsetY < 55) {
		return
	}
	moveX = event.offsetX
	moveY = event.offsetY*(-1)+compresed_data.length*9+10
	if (moveY < 10 || moveX < 55 || moveY > compresed_data.length*9+10){
		return;
	}
	y_num = (moveY - 2)/9
	x_num = (moveX - 55)/9
	txt = `${parseInt(y_num+start_year)}`
	var wx_grid = document.getElementById('gr_grid')
	wx_grid.title = txt
}

//var save_button = document.getElementById('save_measurement_button')
//save_button.addEventListener("click", save);

//var save_button_complet = document.getElementById('save')
//save_button_complet.addEventListener("click", save_handler);

//var close_button = document.getElementById('cancle')
//close_button.addEventListener("click", function(){
//	document.getElementById("myModal").style.display = "none";
//});

//var wx_grid = document.getElementById('gr_grid')
//wx_grid.addEventListener('mousemove', detectMove);


function newMeasurementHandeler(event,val,is_load_call) {
	let can_save = false
	const was_undoing = is_undoing
	is_undoing = true
	if (val == undefined){
		let v = 0.5
		is_load_call = false
		can_save = true
	}
	if ( measurement_index >= 4 || !is_active ){
		is_undoing = false
		return;
	}
	measurement_index ++
	makeNewMeasurmeant(measurement_index,is_load_call)
	is_undoing = was_undoing
	if (can_save){
		
		saveState()
		redo_states = []
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
}
function deleteMeasurementHandeler() {
	if (measurement_index > 0 || !is_active) {
		const was_undoing = is_undoing
		is_undoing = true
		deleteMeasurement()
		DrawLines(measurement_index)
		LoadWXGrid()
		RenderGrid()
		reset_sliders(measurement_index,false)
		is_undoing = was_undoing
		saveState()
		redo_states = []
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	}
	
}

function deleteSpecificMesurment(i){
	if (measurement_index == 0){
		return
	}
	is_loading = true
	save_dict = {
		'mins':state_dict['mins'].slice(),
		'maxes':state_dict['maxes'].slice(),
		'click_coords':state_dict['click_coords'].slice(),
		'reading_types':state_dict['reading_types'].slice(),
		'method_types':state_dict['method_types'].slice(),
		'prevs':state_dict['prevs'].slice()
	}
	save_dict['mins'].splice(i,1)
	save_dict['maxes'].splice(i,1)
	save_dict['click_coords'].splice(i,1)
	save_dict['reading_types'].splice(i,1)
	save_dict['method_types'].splice(i,1)
	save_dict['prevs'].splice(i,1)
	var m = 0
	if (i == 0){
		m = 0
	}
	
	const t_measurement_index = measurement_index
	for (var j = 0; j < t_measurement_index-i+1-m; j++) {
		deleteMeasurement()
	}
	for (var j = 0; j < t_measurement_index-i-m; j++) {
		newMeasurementHandeler(null,true)
	}
	mins = save_dict['mins'].slice()
	maxes = save_dict['maxes'].slice()
	let t_reading_types = save_dict['reading_types'].slice()
	let t_method_types = save_dict['method_types'].slice()
	reading_types = save_dict['reading_types'].slice()
	method_types = save_dict['method_types'].slice()
	for (var i = 0; i < measurement_index+1; i++){
		let r_index = Object.keys(all_data).indexOf(t_reading_types[i]) 
		let m_index = Object.keys(all_data[t_reading_types[i]]).indexOf(t_method_types[i]) 
		LoadReadingDropdown(i,r_index,m_index)
	}
	click_coords = []
	is_loading = false
	let t_click_coords = save_dict['click_coords']
	for (var i = 0; i < t_click_coords.length; i++){
	    click_coords.push({...t_click_coords[i]})
	}
	for (var i = 0; i < measurement_index+1; i++){
		DrawLines(i)
	}
	LoadWXGrid()
	RenderGrid()
}

function deleteMeasurement() {
	for (i in selects){
		if (selects[i][1] == measurement_index){
			selects.splice(i);
			select_draws[i].remove();
			select_draws.splice(i);
		}
	}
	var measurement = document.getElementById("measurement"+measurement_index)
	var histo = document.getElementById("histo"+measurement_index)
	reading_dropdowns.splice(-1)
	method_dropdowns.splice(-1)
	close_btns.splice(-1)
	weight_sliders.splice(-1)
	weight_setexes.splice(-1)
	weight_vals.splice(-1)
	prevs.splice(-1)
	click_coords.splice(-1)
	histo_hights.splice(-1)
	lines.splice(-1)
	draws.splice(-1)
	maxes.splice(-1)
	mins.splice(-1)
	prev_maxes.splice(-1)
	prev_mins.splice(-1)
	invert_btns.splice(-1)
	histo_data.splice(-1)
	measurement.remove()
	histo.remove()
	measurement_index --
}

function reset_sliders(num,is_load_call){
	if (!is_active){
		return
	}
	is_setting = true
	for (var i = 0; i < num+1; i++){
		reset_slider(i,num,is_load_call)
	}
	is_setting = false
	if (!is_load_call){
		RenderGrid()
	}
}

function reset_slider(i,num,is_load_call){
	let s_val = 0
	if (is_load_call){
		s_val = t_weight_vals[i]*100
	}
	else{
		s_val = 100/(num+1)
	}
	prevs[i] = s_val
	document.getElementById("weight_slider_holder"+i).remove()
	document.getElementById("weight_stext_div"+i).remove()
	makeNewElement("measurement"+i,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+i});
	makeNewElement("weight_slider_holder"+i,"div",{"class":"weight_slider","id":"weight_slider"+i});
	makeNewElement("measurement"+i,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+i});
	makeNewElement("weight_stext_div"+i,"div",{"class":"weight_setex","id":"weight_stext"+i});
	
	weight_setexes[i] = document.getElementById( 'weight_stext'+i);
	weight_sliders[i] = document.getElementById('weight_slider'+i);
	noUiSlider.create( weight_sliders[i], {
	    start: [s_val],
	    connect: false,
	    range: {
	        'min': 0,
	        'max': 100
	    },     
	});
	weight_sliders[i].noUiSlider.on('update', function (values, handle) {
	    var weight_val = values[0] / 100;
	    // update text and redraw wx grid
		weight_vals[i] = weight_val
	    weight_setexes[i].textContent = (weight_val*100).toFixed(0)+'%';
		handleSlider(i,weight_val)
		saveState("weight")
		});
}

function handleSlider2(num,weight_val) {
	if (!is_setting && weight_sliders.length > 1) {
		is_setting = true
		var total_weght = 0
		for (var i = 0; i < weight_sliders.length; i++) {
			if (i != num){
				total_weght += weight_vals[i]
			}
		}
		weights = []
		for (var i = 0; i < weight_sliders.length; i++) {
			is_setting = true
			redoSlider(i,num,total_weght,null,weights)
		}
		const total_sliders = weights.reduce((a, b) => a + b, 0);
		for (var i = 0; i < weight_sliders.length; i++) {
			is_setting = true
			i_setex = weight_vals[i]
			document.getElementById("weight_slider_holder"+i).remove()
			document.getElementById("weight_stext_div"+i).remove()
			makeNewElement("measurement"+i,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+i});
			makeNewElement("weight_slider_holder"+i,"div",{"class":"weight_slider","id":"weight_slider"+i});
			makeNewElement("measurement"+i,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+i});
			makeNewElement("weight_stext_div"+i,"div",{"class":"weight_setex","id":"weight_stext"+i});

			weight_setexes[i] = document.getElementById( 'weight_stext'+i);
			weight_sliders[i] = document.getElementById('weight_slider'+i);
			noUiSlider.create( weight_sliders[i], {
			    start: [weights[i]/total_sliders],
			    connect: false,
			    range: {
			        'min': 0,
			        'max': 100
			    },     
			});
			weight_sliders[i].noUiSlider.on('update', function (values, handle) {
			    var weight_val = values[0] / 100;
			    // update text and redraw wx grid
				weight_vals[i] = weight_val
			    weight_setexes[i].textContent = (weight_val*100).toFixed(0)+'%';
				handleSlider(i,weight_val)
				saveState("weight")
				});
			is_setting = false
		}
		RenderGrid()
	}
	else if (!is_setting && weight_sliders.length == 1){
		is_setting = true
		redoSlider(0,null,0,100,null)
	}
	prevs[num] = weight_val
}
function redoSlider2(i,num,total_weght,set_num,weights) {
	if (i != num) {
//		console.log(total_weght)
		if (total_weght != 0){
			wegth_i = weight_vals[i]/total_weght
		}
		else {
			wegth_i = 1/(weight_sliders.length)
		}
		i_setex = weight_vals[i]
		if (set_num != null){
			document.getElementById("weight_slider_holder"+i).remove()
			document.getElementById("weight_stext_div"+i).remove()
			makeNewElement("measurement"+i,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+i});
			makeNewElement("weight_slider_holder"+i,"div",{"class":"weight_slider","id":"weight_slider"+i});
			makeNewElement("measurement"+i,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+i});
			makeNewElement("weight_stext_div"+i,"div",{"class":"weight_setex","id":"weight_stext"+i});

			weight_setexes[i] = document.getElementById( 'weight_stext'+i);
			weight_sliders[i] = document.getElementById('weight_slider'+i);
			noUiSlider.create( weight_sliders[i], {
			    start: [set_num],
			    connect: false,
			    range: {
			        'min': 0,
			        'max': 100
			    },     
			});
			weight_sliders[i].noUiSlider.on('update', function (values, handle) {
			    var weight_val = values[0] / 100;
			    // update text and redraw wx grid
				weight_vals[i] = weight_val
			    weight_setexes[i].textContent = (weight_val*100).toFixed(0)+'%';
				handleSlider(i,weight_val)
				saveState("weight")
				});
		}
		else {
			weights.push((i_setex+wegth_i*(prevs[num]-weight_vals[num]))*100)
		}
		
	}
	is_setting = false
}
function handleSlider(num,weight_val) {
	if (!is_setting && weight_sliders.length > 1) {
		is_setting = true
		var total_weght = 0
		for (var i = 0; i < weight_sliders.length; i++) {
			if (i != num){
				total_weght += weight_vals[i]
			}
		}
		for (var i = 0; i < weight_sliders.length; i++) {
			is_setting = true
			redoSlider(i,num,total_weght,null)
		}
		if (!is_loading){
			RenderGrid()
		}
	}
	else if (!is_setting && weight_sliders.length == 1){
		is_setting = true
		redoSlider(0,null,0,100)
	}
	prevs[num] = weight_val
}
function redoSlider(i,num,total_weght,set_num) {
	if (i != num) {
//		console.log(total_weght)
		if (total_weght != 0){
			wegth_i = weight_vals[i]/total_weght
		}
		else {
			wegth_i = 1/(weight_sliders.length)
		}
		i_setex = weight_vals[i]
		document.getElementById("weight_slider_holder"+i).remove()
		document.getElementById("weight_stext_div"+i).remove()
		makeNewElement("measurement"+i,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+i});
		makeNewElement("weight_slider_holder"+i,"div",{"class":"weight_slider","id":"weight_slider"+i});
		makeNewElement("measurement"+i,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+i});
		makeNewElement("weight_stext_div"+i,"div",{"class":"weight_setex","id":"weight_stext"+i});

		weight_setexes[i] = document.getElementById( 'weight_stext'+i);
		weight_sliders[i] = document.getElementById('weight_slider'+i);
//		console.log('r')
		if (set_num == null){
			set_num = (i_setex+wegth_i*(prevs[num]-weight_vals[num]))*100
		}
		noUiSlider.create( weight_sliders[i], {
		    start: [set_num],
		    connect: false,
		    range: {
		        'min': 0,
		        'max': 100
		    },     
		});
		weight_sliders[i].noUiSlider.on('update', function (values, handle) {
		    var weight_val = values[0] / 100;
		    // update text and redraw wx grid
			weight_vals[i] = weight_val
		    weight_setexes[i].textContent = (weight_val*100).toFixed(0)+'%';
			handleSlider(i,weight_val)
			saveState("weight")
			});
	}
	is_setting = false
}

function LoadReadingDropdown(num,i,j) {
    // get list of reading types
    reading_dropdowns[num].options.length = 0;                
    let option;
    for (var d = 0; d < reading_options.length; d++) {
        option = document.createElement('option');
        option.text = reading_options[d].split('_').join(' ');
        option.value = reading_options[d];
        reading_dropdowns[num].add(option);
    }
    reading_dropdowns[num].selectedIndex = i;
	reading_types = [];
	for (dropdown of reading_dropdowns) {
		reading_types.push(dropdown.value);
	}
	has_reading = true
	LoadMethodDropdown(num,j)
}

function LoadMethodDropdown(num,i) {
    // get list of reading types
    method_dropdowns[num].options.length = 0;
	reading_types = [];
	for (dropdown of reading_dropdowns) {
		reading_types.push(dropdown.value);
	}
	method_options = Object.keys(all_data[reading_types[num]]) 
//	console.log(reading_types)                
    let option;
    for (let c = 0; c < method_options.length; c++) {
        option = document.createElement('option');
        option.text = short_names[reading_types[num]][method_options[c]];
        option.value = method_options[c];
        method_dropdowns[num].add(option);
    }
    method_dropdowns[num].selectedIndex = i;
	method_types = [];
	for (dropdown of method_dropdowns) {
		method_types.push(dropdown.value);
	}
	LoadWXGrid();
	if (!is_loading){
		RenderGrid()
		if (['dir_modal','dir_net'].includes(method_types[num])){
			click_coords[num] = {}
			click_coords[num][13] = 0
			click_coords[num][mins[num]*2+13] = 0
			click_coords[num][maxes[num]+mins[num]+17] = histo_hights[num]
			click_coords[num][maxes[num]*2+17] = 0
			click_coords[num][268] = 0
		}
		else {
			click_coords[num] = {}
			click_coords[num][13] = 0
			click_coords[num][mins[num]*2+13] = 0
			click_coords[num][maxes[num]*2+17] = histo_hights[num]
			click_coords[num][268] = histo_hights[num]
		}
		for (i in selects){
			if (selects[i][1] == num){
				selects.splice(i);
				select_draws[i].remove();
				select_draws.splice(i);
			}
		}
		DrawLines(num)
	}
	
	
}
function LoadDirectionDropdown(num) {
	// Determine whether high values or low values contribute to the metric
    direction_dropdowns[num].options.length = 0;                    
    let option;
    for (let i = 0; i < 2; i++) {
        option = document.createElement('option');
        option.text = ['High','Low'][i];
        option.value = [[1,0],[-1,255]][i];
        direction_dropdowns[num].add(option);
    }
    direction_dropdowns[num].selectedIndex = 0;
}
// create direction dropdown


// get slider range text objects
var wx_stext_val0 = document.getElementById( 'gr_stext0' );
var wx_stext_val1 = document.getElementById( 'gr_stext1' );

// create the range slider
generateSlider(33,66)

function generateSlider(v1,v2){
	var wx_slider = document.getElementById('gr_slider');
	wx_slider.remove()
	makeNewElement("gr_slider_holder","div",{"id":"gr_slider"});
	wx_slider = document.getElementById('gr_slider');
	noUiSlider.create( wx_slider, {
	    start: [v1, v2],
	    connect: false,
	    range: {
	        'min': 0,
	        'max': 100
	    },     
	});

	// When the slider value changes, update the wx grid
	wx_slider.noUiSlider.on('update', function (values, handle) {
		const t = Date.now()
	    wx_range_val0 = values[0] / 100;
	    wx_range_val1 = values[1] / 100;
	    // update text and redraw wx grid
	    wx_stext_val0.textContent = wx_range_val0.toFixed(2);
	    wx_stext_val1.textContent = wx_range_val1.toFixed(2);
		if (!is_loading){
		    RenderGrid();
			saveState("range")
		}
		const t2 = Date.now()
		console.log("total")
		console.log(t2-t)
	});
}


//var testurl = "plot0.json";
// using port 88 here to get around CORS block
//var testurl = "http://localhost:5000/plot0.json?df_station=13743 RONALD REAGAN WASHINGTON NATL AP&df_col=HourlySeaLevelPressure&df_method=MEDIAN";
function LoadWXGrid() {
	if (!has_reading)
		return;
	// make modifiers into arrays
	
    // clear existing wxgriddata
    ClearWXGridData();
//	console.log(all_data)
	reading_types = [];
	for (dropdown of reading_dropdowns) {
		reading_types.push(dropdown.value);
	}
	method_types = [];
	for (dropdown of method_dropdowns) {
		method_types.push(dropdown.value);
	}
	for ( var f = 0; f < reading_types.length; f++ ){
		wx_grdata[reading_types[f]][method_types[f]] = all_data[reading_types[f]][method_types[f]];		
	};    
}

function daysIntoYear( date ){
    return (Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) - Date.UTC(date.getFullYear(), 0, 0)) / 24 / 60 / 60 / 1000;
}

function month_to_week( nmonth ) {
    let day_of_year = daysIntoYear( new Date(2020, nmonth, 1) );
    let week = day_of_year * 52.0 / 365.0;
    return week;
}
// var max_value = Math.max(...histo_plot)
// for (var i = 0; i < 128; i++) {
// 	for (var j = 0; j < color_plot[i].length; j ++){
// 		if (do_colors){
// 			var color1 = color_plot[i][j][0]
// 			if (j >= color_plot[i].length-1){
// 				var color2 = color_plot[i][j][0]
// 			} else {
// 				var color2 = color_plot[i][j+1][0]
// 			}
// 		} else {
// 			var color1 = "#f4f4f4"
// 			var color2 = "#f4f4f4"
// 		}
// 		var color = '#'
// 		for (var i = 0; i < 3; i++){
// 			var color_part = parseInt((color1+color2)/2).toString(16)
// 			if (color_part.length == 0){
// 				color_part = "00"
// 			} else if (color_part.length == 1){
// 				color_part = "0" + color_part
// 			}
// 			color += color_part
// 		}
//         draw.rect( 2, 1*125/max_value ).move( i*2+15, (125-(j+1)*125/max_value)*0.5+9 ).attr({
//             'fill':color,
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
// 	}
function DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,do_colors,do_text,st_subtract,do_plus){
	var max_value = Math.max(...histo_plot)
	for (var i = 0; i < 128; i++) {
		var fillcols = []
		if (color_plot[i].length > 0) {
			var cp = 0
			fillcols.push(color_plot[i][0].slice())
			fillcols[0].push(1)
			fillcols[0].push(0)
			for ( p=1; p<color_plot[i].length; p++ ){
				if (color_plot[i][p][0] == color_plot[i][cp][0] || !do_colors) {
					fillcols.at(-1)[2] ++ 
				} else {
					fillcols.push(color_plot[i][p].slice())
					fillcols.at(-1).push(1)
					fillcols.at(-1).push(p)
					cp = p
				}
			}
		}
		var acc_ind = 0
		for (var j = 0; j < fillcols.length; j++){
			if (acc_ind == 0 && j < fillcols.length-2 && max_value >= 10 && fillcols[j][2]+fillcols[j+1][2]+fillcols[j+2][2] <= 4){
				acc_ind = 3
				if (do_colors){
					var color1 = fillcols[j][0]
					var color2 = fillcols[j+1][0]
					var color3 = fillcols[j+2][0]
				} else {
					var color1 = "#f4f4f4"
					var color2 = "#f4f4f4"
					var color3 = "#f4f4f4"
				}
				var color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
				var color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
				var color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
				var color = '#'
				for (var k = 0; k < 3; k++){
					var color_part = parseInt((color1[k]+color2[k]+color3[k])/3).toString(16)
					if (color_part.length == 0){
						color_part = "00"
					} else if (color_part.length == 1){
						color_part = "0" + color_part
					}
					color += color_part
				}
		        draw.rect( 2, 0.5*125/max_value*(fillcols[j][2]+fillcols[j+1][2]+fillcols[j+2][2]) ).move( i*2+15, (125-(fillcols[j+2][3]+fillcols[j+2][2])*125/max_value)*0.5+9 ).attr({
		            'fill':color,
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0
		        });
			} else if (acc_ind == 0) {
				acc_ind = 1
				if (do_colors){
					var color = fillcols[j][0]
				} else {
					var color = "#f4f4f4"
				}
		        draw.rect( 2, 0.5*125/max_value*fillcols[j][2] ).move( i*2+15, (125-(fillcols[j][3]+fillcols[j][2])*125/max_value)*0.5+9 ).attr({
		            'fill':color,
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0
		        });
			}
			acc_ind --
			// if (do_colors){
// 				var color = color_plot[i][j][0]
// 			} else {
// 				var color = "#f4f4f4"
// 			}
// 	        draw.rect( 2, 0.5*125/max_value ).move( i*2+15, (125-(j+1)*125/max_value)*0.5+9 ).attr({
// 	            'fill':color,
// 	            'shape-rendering':'crispEdges',
// 	            'stroke-width': 0
// 	        });
		}
		// var fillcol = '#ffffff'
//         draw.rect( 2, color_plot[2][i]*0.5*125/max_value ).move( i*2+15, (125-color_plot[2][i]*125/max_value)*0.5+9 ).attr({
//             'fill':colors[2],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
//         draw.rect( 2, color_plot[1][i]*0.5*125/max_value ).move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i])*125/max_value)*0.5+9 ).attr({
//             'fill':colors[1],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
//         draw.rect( 2, color_plot[0][i]*0.5*125/max_value ).move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i])*125/max_value)*0.5+9 ).attr({
//             'fill':colors[0],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
	}
	if (do_text){
		for (var j = 2; j < histo_plot.length-2; j++){
			if (histo_plot[j]/max_value >= 0.4){
				is_mode = true
				for (var i = 1; i < Math.min(10,j); i++){
					if (histo_plot[j-i] > histo_plot[j]){
						is_mode = false
					}
				}
				for (var i = 1; i < histo_plot.length-Math.max(histo_plot.length-10,j); i++){
					if (histo_plot[j+i] > histo_plot[j]){
						is_mode = false
					}
				}
				if (is_mode){
					if (is_seasonaly_adjusted){
						let st_txt = ''
						if (parseFloat(((((j*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2)) > 0){
							st_txt = '+'
						}
						var mode = draw.text( st_txt+`${parseFloat(((((j*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
					}
					else {
						var mode = draw.text( `${parseFloat(((((j*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
					}
					let mode_length = mode.length();
			        mode.move( j*2 - mode_length/2 + 15,125*0.5-histo_plot[j]*0.5*125/max_value ); // center vertically
				}
			}
		}
		if (is_seasonaly_adjusted){
			let st_txt = ''
			if (parseFloat(((((min_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2)) > 0){
				st_txt = '+'
			}
			var min_extrem = draw.text( st_txt+`${parseFloat(((((min_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
		}
		else {
			var min_extrem = draw.text( `${parseFloat(((((min_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
		}
	    let min_extrem_length = min_extrem.length();
	    min_extrem.move( min_num*2 - min_extrem_length/2 + 15,125*0.5+10 ); // center vertically

		if (is_seasonaly_adjusted){
			let st_txt = ''
			if (parseFloat(((((max_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2)) > 0){
				st_txt = '+'
			}
			var max_extrem = draw.text( st_txt+`${parseFloat(((((max_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul-(((st_subtract*compresion[reading_types[num]][method_types[num]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
		}
		else {
			var max_extrem = draw.text( `${parseFloat(((((max_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',9).font('family','Arial');
		}
	    let max_extrem_length = max_extrem.length();
	    max_extrem.move( max_num*2 - max_extrem_length/2 + 15,125*0.5+10 ); // center vertically
	}
}
function DrawHistograms(compresed_data,inc_data){
	if (color_data.length == 0){
		return
	}
	for (num = 0; num < measurement_index+1; num ++){
		var histo_plot_st = new Array(128).fill(0);
		var color_plot_st = new Array(128).fill().map(e => []);
		color_plot_str = JSON.stringify(color_plot_st)
		var relev_data = all_data[reading_types[num]][method_types[num]]
		for (var year = 0; year < relev_data.length; year ++){
			for (var week = 0; week < 52; week ++){
				if (relev_data[year][week] != null && parseInt(relev_data[year][week]/2) < 128 && parseInt(relev_data[year][week]/2) >= 0){
					histo_plot_st[parseInt(relev_data[year][week]/2)] += 1
					color_plot_st[parseInt(relev_data[year][week]/2)].push(color_data[relev_data.length-year-1][week])
				}
			}
		}
		for (var i = 0; i < color_plot_st.length; i ++){
			color_plot_st[i].sort((a, b) => b[1] - a[1])
		}
		var max_num = null
		for (var j = 0; j < histo_plot_st.length; j++){
			if (histo_plot_st[j] != 0){
				max_num = j
			}
		}
		var min_num = null
		for (var j = histo_plot_st.length-1; j >= 0; j--){
			if (histo_plot_st[j] != 0){
				min_num = j
			}
		}
		var histo_plot = histo_plot_st
		var color_plot = color_plot_st
		if (draws[num]){
			draws[num].clear()
			draws[num].remove()
		}
		var draw = SVG().addTo('#histogram'+num).size( 285, 125*0.5+18 );
		draw.attr({
		});
		draws[num] = draw
		var mul = 1
		var expon = 1
		if (compresion[reading_types[num]][method_types[num]]["type"] == "parabolic") {
			expon = 2
		}
		var st_subtract = 0
		var do_plus = false
		if (is_seasonaly_adjusted){
			st_subtract = 127
			do_plus = true
		}
		`
		if (compresion[reading_types[num]][method_types[num]]["units"] == "degrees"){
			drawDirectionLoop(expon,histo_plot,min_num,max_num,color_plot,draw)
			mins[num] = min_num
			maxes[num] = max_num
			histo_hights[num] = 125*0.5
			DrawLines(num)
			if (select != null && select[1] == num) {
				val = select[0]
			    select_draw = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)-2 ).attr({
			        'fill':'#d55',
			        'shape-rendering':'crispEdges',
			        'stroke-width': 0 
			    });
			}
			return
		}
		`
		if (save_clicks_x.length >= 1){
			DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,false,false,st_subtract,do_plus)
			var histo_plot_st = new Array(128).fill(0);
			var color_plot_st = new Array(128).fill().map(e => []);
			color_plot_str = JSON.stringify(color_plot_st)
			var relev_data = all_data[reading_types[num]][method_types[num]]
			var new_compressed = []
			var new_relev = []
			for (var index = 0; index < save_clicks_x.length; index ++){
				let year = save_clicks_y[index]
				let week = save_clicks_x[index]
				if (relev_data[year][week] != null && parseInt(relev_data[year][week]/2) < 128 && parseInt(relev_data[year][week]/2) >= 0){
					histo_plot_st[parseInt(relev_data[year][week]/2)] += 1
					color_plot_st[parseInt(relev_data[year][week]/2)].push(color_data[relev_data.length-year-1][week])
				}
			}
			for (var i = 0; i < color_plot_st.length; i ++){
				color_plot_st[i].sort((a, b) => b[1] - a[1])
			}
			var max_num_new = null
			for (var j = 0; j < histo_plot_st.length; j++){
				if (histo_plot_st[j] != 0){
					max_num_new = j
				}
			}
			var min_num_new = null
			for (var j = histo_plot_st.length-1; j >= 0; j--){
				if (histo_plot_st[j] != 0){
					min_num_new = j
				}
			}
			var histo_plot_new = histo_plot_st
			var color_plot_new = color_plot_st
			DrawHistogram(draw,histo_plot_new,min_num_new,max_num_new,expon,mul,color_plot_new,num,true,true,st_subtract,do_plus)
		}
		else {
			DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,true,true,st_subtract,do_plus)
		}
		histo_data[num] = {'histo_plot':histo_plot,'min_num':min_num,'max_num':max_num,'expon':expon,'mul':mul,'color_plot':color_plot}
//		console.log(min_num*2+15)
//		console.log(max_num*2+15)
		prev_maxes = maxes.slice()
		prev_mins = mins.slice()
		mins[num] = min_num
		maxes[num] = max_num
		histo_hights[num] = 125*0.5
		DrawLines(num)
		for (i in selects){
			if (selects[i][1] == num){
				val = selects[i][0]
			    select_draws[i] = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)+7 ).attr({
			        'fill':'#d55',
			        'shape-rendering':'crispEdges',
			        'stroke-width': 0
			    });
			}
		}
		
	}       
}

function drawDirectionLoop(expon,histo_plot,min_num,max_num,color_plot,draw){
	for (var i = 0; i < 2; i++) {
		var r2 = (color_plot[2][i]*0.5)**(1/2)
		var r1 = (color_plot[1][i]*0.5)**(1/2)
		var r0 = (color_plot[0][i]*0.5)**(1/2)
		var section_ang = 2.8*Math.PI/180
		var ang = (section_ang*i+section_ang/2)
		var fillcol = '#ffffff'
        draw.path("M200 150 l100 0 a100,100 0 0,1 -6.06 37.1 z").attr({  //.move(i*2+15, (125-color_plot[2][i])*0.5 )`m${125*0.25+4.5} ${285*0.5} l${Math.cos(ang)*r2} ${Math.sin(ang)*r2} a${r2},${r2} 0 1,0 ${Math.cos(ang+section_ang)*r2} ${Math.sin(ang+section_ang)*r2} z`
            'fill':'#54278f',
//            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
		`
		var radius = (color_plot[1][i]*0.5)**(1/2)
        draw.path("").move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i]))*0.5 ).attr({
            'fill':'#9e9ac8',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.path("").move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i]))*0.5 ).attr({
            'fill':'#dadaeb',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
		var line = draw.line(0, 0, 100, 100).move(0, 0)
		line.stroke({ color: '#000', width: 1, })
		line.remove()
		`
	}
}

function AddClickHandler(num) {
	var histogram = document.getElementById('histogram'+num);
	histogram.addEventListener("click", function () {
		if (!is_active) {
			return
		}
		else if (!enable_line_editing.checked){
			DetectHistoClick(num,event)
			return
		}
		RegisterClick(num,event)
		
		saveState()
		is_shifting = false
		is_weigth_sliding = false
		is_range_sliding = false
		is_sensetivity_sliding = false
	});
}
function DetectHistoClick(num,event) {
	if (!event.metaKey){
		save_clicks_x = []
		save_clicks_y = []
		selected_years = []
		selected_seasons = []
	}
	click_x = event.offsetX
	click_y = histo_hights[num]-event.offsetY+9
	if (click_y < 0 || click_x < mins[num]*2+13 || click_x > maxes[num]*2+17 ||  click_y > 71){
		return
	}
	click_x -= 17
	var compressed_coords_x = []
	var compressed_coords_y = []
	for (var i = 0; i < save_clicks_x.length; i++){
		compressed_coords_x.push(save_clicks_x[i])
		compressed_coords_y.push(save_clicks_y[i])
	}
	for (let i=0; i<all_data[reading_types[num]][method_types[num]].length; i++){
		for (let k=0; k<all_data[reading_types[num]][method_types[num]][i].length; k++){
			if (parseInt(all_data[reading_types[num]][method_types[num]][i][k]/2) == parseInt(click_x/2)){
				let is_selected = false
				for (var j=0; j < save_clicks_x.length; j++){
					if (k == save_clicks_x[j] && i == save_clicks_y[j]){
						is_selected = true
						break
					}
				}
				if (!is_selected){
					save_clicks_x.push(k)
					save_clicks_y.push(i)
				}
			}
		}
	}
	DetectGridClick(null,true)
}
function RegisterClick(num,event) {
	click_x = event.offsetX
	click_y = histo_hights[num]-event.offsetY+9
	if (click_y < -4 || click_x < 13 || click_x > 268 ||  click_y > 71){
		return
	}
	if (click_y < 0){
		click_y = 0
	}
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	for (i in selects){
		if (Math.abs(click_x-selects[i][0]) < 4 && Math.abs(click_y-click_coords[num][selects[i][0]]) < 4) {
			selects.splice(i)
			select_draws[i].remove()
			select_draws.splice(i)
			return
		}
	}
	for (val of x_vals) {
		if (Math.abs(click_x-val) < 4 && Math.abs(click_y-click_coords[num][val]) < 4) {
			if (!event.metaKey || (selects.length && selects[0][1] != num)){
				for (i in selects){
					selects.splice(i);
					select_draws[i].remove();
					select_draws.splice(i);
				}
			}
			selects.push([val,num])
			var draw = draws[num];
	        select_draws.push(draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)+7 ).attr({
	            'fill':'#d55',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        }));
			
			return
		}
	}
	if (selects.length != 0){
		for (i in selects){
			selects.splice(i);
			select_draws[i].remove();
			select_draws.splice(i);
		}
	}
	if (Object.keys(click_coords[num]).length < 10){
		click_coords[num][click_x] = click_y
	}
	DrawLines(num)
	RenderGrid()
}

function getCellCoords(x,y){
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;	
	return [Math.floor((x-35)/9),Math.floor(num_years-y/9)]
}

function DetectYearClick(event,is_render_call){
	if (!is_render_call){
		y_coord = event.offsetY-offset-data_len/2+20
	}
	if (!is_render_call && !(event.metaKey || event.shiftKey)){
		save_clicks_x = []
		save_clicks_y = []
		selected_years = []
		selected_seasons = []
	}
	if (!is_render_call && y_coord < 37){
		DetectGridClick(null,true)
		return
	}
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		if (event.shiftKey && selected_years.length >= 1){
			c_year = Math.floor((y_coord)/9)
			p_year = selected_years[selected_years.length-1]
			t_year = c_year
			if (c_year == p_year){
				
			}
			else if (c_year < p_year){
				while (t_year < p_year){
					if (!selected_years.includes(t_year)){
						selected_years.push(t_year)
					}
					t_year++
				}
			}
			else {
				while (t_year > p_year){
					if (!selected_years.includes(t_year)){
						selected_years.push(t_year)
					}
					t_year--
				}
			}
		}
		else {
			selected_years.push(Math.floor((y_coord)/9))
		}
	}
	if (!is_render_call){
		if (event.shiftKey && selected_years.length >= 1){
			t_year = c_year
			if (c_year == p_year){
				
			}
			else if (c_year < p_year){
				while (t_year < p_year){
					for (let i=0; i < 52; i++){
						var is_selected = false
						for (var j=0; j < save_clicks_x.length; j++){
							if (i == save_clicks_x[j] && num_years-t_year+3 == save_clicks_y[j]){
								is_selected = true
								break
							}
						}
						if (!is_selected){
							save_clicks_x.push(i)
							save_clicks_y.push(num_years-t_year+3)
						}
					}
					t_year++
				}
			}
			else {
				while (t_year > p_year){
					for (let i=0; i < 52; i++){
						var is_selected = false
						for (var j=0; j < save_clicks_x.length; j++){
							if (i == save_clicks_x[j] && num_years-t_year+3 == save_clicks_y[j]){
								is_selected = true
								break
							}
						}
						if (!is_selected){
							save_clicks_x.push(i)
							save_clicks_y.push(num_years-t_year+3)
						}
					}
					t_year--
				}
			}
		}
		else{
			for (let i=0; i < 52; i++){
				var is_selected = false
				for (var j=0; j < save_clicks_x.length; j++){
					if (i == save_clicks_x[j] && compresed_data.length-Math.floor((y_coord-27)/9-1) == save_clicks_y[j]){
						is_selected = true
						break
					}
				}
				if (!is_selected){
					save_clicks_x.push(i)
					save_clicks_y.push(compresed_data.length-Math.floor((y_coord-27)/9))
				}
			}
		}
	}
	if (doPDO){
		let move = 22
	}
	else{
		let move = 0
	}
	DetectGridClick(null,true)
}

function DetectSeasonClick(event,is_render_call){
	if (!is_render_call && !(event.metaKey || event.shiftKey)){
		save_clicks_x = []
		save_clicks_y = []
		selected_years = []
		selected_seasons = []
	}
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		if (event.shiftKey && selected_seasons.length >= 1){
			c_season = Math.floor((event.offsetX)/9-4)
			p_season = selected_seasons[selected_seasons.length-1]
			t_season = c_season
			if (c_season == p_season){
				
			}
			else if (c_season < p_season){
				while (t_season < p_season){
					if (!selected_seasons.includes(t_season)){
						selected_seasons.push(t_season)
					}
					t_season++
				}
			}
			else {
				while (t_season > p_season){
					if (!selected_seasons.includes(t_season)){
						selected_seasons.push(t_season)
					}
					t_season--
				}
			}
		}
		else {
			selected_seasons.push(Math.floor((event.offsetX)/9-4))
		}
	}
	if (!is_render_call && !(event.metaKey || event.shiftKey)){  
	}
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		if (event.shiftKey && selected_seasons.length >= 1){
			t_season = c_season
			if (c_season == p_season){
				
			}
			else if (c_season < p_season){
				while (t_season < p_season){
					for (let i=0; i < num_years; i++){
						var is_selected = false
						for (var j=0; j < save_clicks_x.length; j++){
							if (t_season == save_clicks_x[j] && i == save_clicks_y[j]){
								is_selected = true
								break
							}
						}
						if (!is_selected){
							save_clicks_y.push(i)
							save_clicks_x.push(t_season)
						}
					}
					t_season++
				}
			}
			else {
				while (t_season > p_season){
					for (let i=0; i < num_years; i++){
						var is_selected = false
						for (var j=0; j < save_clicks_x.length; j++){
							if (t_season == save_clicks_x[j] && i == save_clicks_y[j]){
								is_selected = true
								break
							}
						}
						if (!is_selected){
							save_clicks_y.push(i)
							save_clicks_x.push(t_season)
						}
					}
					t_season--
				}
			}
		}
		else{
			for (let i=0; i < num_years; i++){
				var is_selected = false
				for (var j=0; j < save_clicks_x.length; j++){
					if (Math.floor((event.offsetX-36)/9) == save_clicks_x[j] && i == save_clicks_y[j]){
						is_selected = true
						break
					}
				}
				if (!is_selected){
					save_clicks_y.push(i)
					save_clicks_x.push(Math.floor((event.offsetX-36)/9))
				}
			}
		}
	}
	// for (let i=0; i < 52; i++){
// 		if (!(selected_seasons.includes(i))){
// 			season_covers.push(season_draw.rect( 9, num_years*0.5 ).move( i*9+35,offset).attr({
// 					fill: '#fff'
// 				, 'fill-opacity': 0.5
// 						, stroke: '#ee0'
// 				, 'stroke-width': 0
// 					}));
// 		}
// 	}
	DetectGridClick(null,true)
}

function DetectGridClick(event,is_render_call){
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;	
	document.getElementById( "tables" ).innerHTML = "";
	document.getElementById( "heder" ).innerHTML = "";
	if (!is_render_call){
		let click_x = event.offsetX
		let click_y = event.offsetY
		let cell_coords = getCellCoords(click_x-1,click_y-2)
		if (cell_coords[0] < 0 || cell_coords[1] < 0 ) {
			save_clicks_x = []
			save_clicks_y = []
			selected_years = []
			selected_seasons = []
			DetectGridClick(null,true)
			return
		}
		let num = save_clicks_x.length
		if (event.metaKey) {
			var is_selected_cell = false;
			for (var i=0; i < num; i++){
				if (cell_coords[0] == save_clicks_x[i] && cell_coords[1] == save_clicks_y[i]){
					is_selected_cell = true
					break
				}
			}
			if (is_selected_cell){
				save_clicks_x.splice(i,1)
				save_clicks_y.splice(i,1)
			}
			else {
				save_clicks_x.push(cell_coords[0])
				save_clicks_y.push(cell_coords[1])
			}
		}
		else if (event.shiftKey && num >= 1){
			let c_week = cell_coords[0]
			let c_year = cell_coords[1]
			let l1 = [save_clicks_x[num-1],save_clicks_y[num-1]]
			let p_week = l1[0]
			let p_year = l1[1]
			if (c_week == p_week && p_year == c_year){
			}
			else if (c_year < p_year || (c_year == p_year && c_week < p_week)){
				var t_week = c_week
				var t_year = c_year
				while (t_year < p_year || (t_year == p_year && t_week < p_week)){
					var is_selected_cell = false;
					for (var i=0; i < num; i++){
						if (t_week == save_clicks_x[i] && t_year == save_clicks_y[i]){
							is_selected_cell = true
							break
						}
					}
					if (!is_selected_cell){
						save_clicks_x.push(t_week)
						save_clicks_y.push(t_year)
					}
					t_week++
					if (t_week > 51){
						t_week = 0
						t_year++
					}
				}
			}
			else{
				var t_week = c_week
				var t_year = c_year
				while (t_year > p_year || (t_year == p_year && t_week > p_week)){
					var is_selected_cell = false;
					for (var i=0; i < num; i++){
						if (t_week == save_clicks_x[i] && t_year == save_clicks_y[i]){
							is_selected_cell = true
							break
						}
					}
					if (!is_selected_cell){
						save_clicks_x.push(t_week)
						save_clicks_y.push(t_year)
					}
					t_week--
					if (t_week < 0){
						t_week = 51
						t_year--
					}
				}
			}
			
		}
		else {
			save_clicks_x = [cell_coords[0]]
			save_clicks_y = [cell_coords[1]]
			selected_years = []
			selected_seasons = []
		}
	}
	click_data = new Array(num_years).fill().map(e => new Array(52).fill(false));
	for (var i=0; i<save_clicks_x.length; i++){
		click_data[save_clicks_y[i]][save_clicks_x[i]] = true
	}
	var outline_length = outlines.length
	for (var i=0; i < outline_length; i++){
		outlines[outlines.length-1].remove()
		outlines.splice(-1)
	} 
	var cover_length = covers.length
	for (var i=0; i < cover_length; i++){
		covers[covers.length-1].remove()
		covers.splice(-1)
	}
	var fades_length = fades.length
	for (var i=0; i < fades_length; i++){
		fades[fades.length-1].remove()
		fades.splice(-1)
	}
	for (highlight of highlights) {
		var highlight_length = highlight.length
		for (var i=0; i < highlight_length; i++){
			highlight[highlight.length-1].remove()
			highlight.splice(-1)
		}
	}

	var can_fade = false
	for (var i=0; i < save_clicks_x.length; i++){
		var coords = [save_clicks_x[i],save_clicks_y[i]]
		if (Math.min(...coords) >= 0 && wx_grdata[reading_types[0]][method_types[0]][coords[1]][coords[0]] != null){
			can_fade = true
		}
	}
	if (can_fade) {
		// fades.push(grid_draw.rect( 9*52, 9*num_years ).move( 35, 1).attr({
// 					fill: '#fff'
// 			, 'fill-opacity': 0.5
// 		}));
		var fade_data = new Array(num_years).fill().map(e => [])
		for (var i = 0; i < num_years; i++) {
			var cp = false
			for (var j = 0; j < 52; j++) {
				if (click_data[i][j]){
					fade_data[i].push([false,null,null])
					cp = false
				} else if (cp){
					fade_data[i].at(-1)[1] ++

				} else {
					cp = true
					fade_data[i].push([true,1,j])
				}
			}
		}
		for (var i=0; i < num_years; i++) {
			for (var j = 0; j < fade_data[i].length; j++) {
				if (fade_data[i][j][0]){
					fades.push(grid_draw.rect( 9*fade_data[i][j][1], 9 ).move( 35+fade_data[i][j][2]*9, 1+(num_years-i-1)*9).attr({
								fill: '#fff'
						, 'fill-opacity': 0.5
					}));
				}
			}
		}	
	}
	DrawHistograms(compresed_data)
	DrawYears()
	DrawSesonalitys()
	for (var i=0; i<save_clicks_x.length; i++){
		// fillcol = color_data[num_years-save_clicks_y[i]-1][save_clicks_x[i]][0]
// 		size = bsizes[save_clicks_y[i]][save_clicks_x[i]]
// 		if (size > 0 && color_data[num_years-save_clicks_y[i]-1][save_clicks_x[i]][1]){
// 			covers.push(grid_draw.rect( size, size ).move( (save_clicks_x[i]+4)*9-0.5+(9-size)/2, (num_years-save_clicks_y[i]-1)*9+2+(9-size)/2).attr({
// 					fill: fillcol
// 				, 'fill-opacity': 1
// 					, stroke: '#000'
// 				, 'stroke-width': 0
// 		    }));
// 		}
		RegisterGridClick(null,save_clicks_x[i],save_clicks_y[i],null)
	}
	
	var extream_weeks = 0
	for (var i = 0; i < save_clicks_x.length; i++){
		if (compresed_data[save_clicks_y[i]][save_clicks_x[i]]/255 > wx_range_val1){
			extream_weeks++
		}
	}
	if (save_clicks_x.length > 0){
		document.getElementById( 'extream_weeks' ).innerHTML = "Extream weeks: " + extream_weeks + "/" + save_clicks_x.length
	} else {
		document.getElementById( 'extream_weeks' ).innerHTML = ""
	}
	if (can_fade){
		var txt = ""
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]]) 
			if (1 == 1){
				makeNewElement("tables","table",{"id":"table"+(i+1),"style":"display: inline-block; text-align: center; margin-left: 10px float: top;" },null);
				makeNewElement("table"+(i+1),"tr",{"id":"measurementy"+(i+1)},null);
				makeNewElement("measurementy"+(i+1),"th",{"id":"th"+(i+1)},reading_options[i].split('_').join(' '));
			}
			var value_list = []
			for (var j=0; j < method_options.length; j++){
				relev_data = all_data[reading_options[i]][method_options[j]]
				var mul = 1
				var expon = 1
				if (compresion[reading_options[i]][method_options[j]]["type"] == "parabolic") {
					expon = 2
				}
				var compressed_value = null
				value_list.push([])
				for (var num=0; num < save_clicks_x.length; num++){
					var coords = [save_clicks_x[num],save_clicks_y[num]]
					if (Math.min(...coords) >= 0 && wx_grdata[reading_types[0]][method_types[0]][coords[1]][coords[0]] != null){
						var value = false
						if (is_seasonaly_adjusted){
							let st_txt = ''
							if (parseFloat(((((all_data[reading_options[i]][method_options[j]][save_clicks_y[num]][save_clicks_x[num]]*compresion[reading_options[i]][method_options[j]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0])*mul-(((127*compresion[reading_options[i]][method_options[i]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0])*mul).toFixed(2)) > 0){
								st_txt = '+'
							}
							value = parseFloat(((((all_data[reading_options[i]][method_options[j]][save_clicks_y[num]][save_clicks_x[num]]*compresion[reading_options[i]][method_options[j]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0])*mul-(((127*compresion[reading_options[i]][method_options[i]]["scale"])**expon)*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0])*mul).toFixed(2))
						}
						if (!value) {
							value_list[j].push(((all_data[reading_options[i]][method_options[j]][save_clicks_y[num]][save_clicks_x[num]]*compresion[reading_options[i]][method_options[j]]["scale"])**expon+compresion[reading_options[i]][method_options[j]]["min"])*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0]+unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][1]);
						}
						else {
							value_list[j].push(value);
						}
					}
				}
			}
			let dir_net_index = method_options.indexOf('dir_net')
			let speed_net_index = method_options.indexOf('speed_net')
			for (var j=0; j < method_options.length; j++){
				if (method_options[j] == 'min'){
					compressed_value = Math.min(...value_list[j])
				}
				else if (['max','speed_max'].includes(method_options[j])){
					compressed_value = Math.max(...value_list[j])
				}
				else if (['total','total_rain','total_snow','total_wet_snow','total_freezing_rain','total_ice_pellets'].includes(method_options[j])){
					compressed_value = value_list[j].reduce((a, b) => a + b, 0)
				}
				else if (['dir_modal'].includes(method_options[j])){
					if (value_list[j].length == 1){
						compressed_value = value_list[j][0]
					}
					else {
						compressed_value = null
					}
				}
				else if (['dir_net','speed_net'].includes(method_options[j])){
					var x = 0
					var y = 0
					for (var k=0; k < value_list[j].length; k++){
						let ang = value_list[dir_net_index][k]*Math.PI/180
						let dist = value_list[speed_net_index][k]
						x += Math.cos(ang)*dist
						y += Math.sin(ang)*dist
					}
					let new_dist = Math.sqrt(x**2+y**2)
					if (method_options[j] == 'speed_net'){
						compressed_value = new_dist
					}
					else{
						compressed_value = Math.acos(x/new_dist)
						if (Math.sign(y) == -1){
							compressed_value = compressed_value + Math.PI
						}
						compressed_value *= 180/Math.PI
					}
				}
				else {
					compressed_value = value_list[j].reduce((a, b) => a + b, 0)/value_list[j].length
				}
				var st_txt = ''
				if (is_seasonaly_adjusted){
					if (compressed_value > 0){
						st_txt = '+'
					}
				}
				if (1 == 1){
					if (compressed_value == null){
						txt = 'N/A'
					}
					else {
						txt = st_txt+parseFloat(compressed_value).toFixed(2)+unit_names[unit_sets[unit_num]][reading_options[i]][method_options[j]]
					}
					makeNewElement("table"+(i+1),"tr",{"id":"methody"+(i+1)+','+j},null);
					makeNewElement("methody"+(i+1)+','+j,"td",{"id":"td"+(i+1)+','+j},short_names[reading_options[i]][method_options[j]]+': '+ txt);
				}
			}
		}
	}
	// for (var i = 0; i < gridlines.length; i++){
// 		gridlines[i].front()
// 	}
// 	for (var i = 0; i < outlines.length; i++){
// 		outlines[i].front()
// 	}
}
function arrayIncludes(a,b){
    a = JSON.stringify(a);
    b = JSON.stringify(b);
	var c = a.indexOf(b);
	if (c != -1){
	    return true
	}
	return false
}
function RegisterGridClick(event,click_x,click_y,num) {
	var num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	var coords = [click_x,click_y]
	if (Math.min(...coords) < 0 || wx_grdata[reading_types[0]][method_types[0]][coords[1]][coords[0]] == null){
		return
	}
	var fillcol = '#0000'
    var mx = compresed_data[coords[1]][coords[0]] / 255;
    if ( mx < wx_range_val0 ){
        fillcol = color_lists[color_num][0];
    }
    else if ( mx < wx_range_val1 ){
        fillcol = color_lists[color_num][1];
    }
    else {
        fillcol = color_lists[color_num][2];
    }
	size = bsizes[click_y][click_x]
	if (click_x == 51 || !click_data[click_y][click_x+1] || wx_data[click_y][click_x+1] == null){
		outlines.push(grid_draw.rect( 1.5, size).move( (click_x+4)*9-0.5+(9-size)/2+8, (num_years-click_y-1)*9+2+(9-size)/2).attr({
			fill: '#000'
		, 'fill-opacity': 1
			, stroke: '#000'
		, 'stroke-width': 0 
    	}));
	}
	if (click_x == 0 || !click_data[click_y][click_x-1] || wx_data[click_y][click_x-1] == null){
		outlines.push(grid_draw.rect( 1.5, size).move( (click_x+4)*9-0.5+(9-size)/2, (num_years-click_y-1)*9+2+(9-size)/2).attr({
			fill: '#000'
		, 'fill-opacity': 1
			, stroke: '#000'
		, 'stroke-width': 0 
    	}));
	}
	if (click_y == num_years-1 || !click_data[click_y+1][click_x] || wx_data[click_y+1][click_x] == null){
		outlines.push(grid_draw.rect( size, 1.5).move( (click_x+4)*9-0.5+(9-size)/2, (num_years-click_y-1)*9+2+(9-size)/2).attr({
			fill: '#000'
		, 'fill-opacity': 1
			, stroke: '#000'
		, 'stroke-width': 0 
    	}));
	}
	if (click_y == 0 || !click_data[click_y-1][click_x] || wx_data[click_y-1][click_x] == null){
		outlines.push(grid_draw.rect( size, 1.5).move( (click_x+4)*9-0.5+(9-size)/2, (num_years-click_y-1)*9+2+(9-size)/2+8).attr({
			fill: '#000'
		, 'fill-opacity': 1
			, stroke: '#000'
		, 'stroke-width': 0 
    	}));
	}
	// covers.push(grid_draw.rect( size-1, size-1 ).move( (click_x+4)*9-0.5+(9-size)/2, (num_years-click_y-1)*9+2+(9-size)/2).attr({
	// 		fill: fillcol
	// 	, 'fill-opacity': 0
	// 		, stroke: '#000'
	// 	, 'stroke-width': 1
	//         }));
	// if (save_clicks_x.length == 0){
	// 	for (var num = 0; num < measurement_index+1; num ++){
	// 		var max_value = Math.max(...histo_data[num]['histo_plot'])
	// 		var data = wx_grdata[reading_types[num]][method_types[num]][coords[1]][coords[0]]
	// 		histo_index = parseInt(data/2)
	// 		draw = draws[num]
	// 		if (highlights[num] == null){
	// 			highlights[num] = []
	// 		}
	//         highlights[num].push(draw.rect( 2, histo_data[num]['histo_plot'][histo_index]*0.5*125/max_value ).move( histo_index*2+15,(125-histo_data[num]['histo_plot'][histo_index]*125/max_value)*0.5+9).attr({
	//             'fill':'#eeee00',
	//             'shape-rendering':'crispEdges',
	//             'stroke-width': 0
	//         }));
	// 	}
	// }
	month_lenghths = [31,28,31,30,31,30,31,31,30,31,30,31]
	var day = [coords[0]]*7
	var display_day = null
	var month = null
	for (i=0;i<month_lenghths.length;i++){
		if (day < month_lenghths.slice(0,i).reduce((a, b) => a + b, 0)){
			month = i-1
			display_day = day - month_lenghths.slice(0,i-1).reduce((a, b) => a + b, 0)
			break;
		}
	}
	if (month == null){
		display_day = day - month_lenghths.slice(0,11).reduce((a, b) => a + b, 0)
		month = 11
	}
	let months_txt = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	var year = coords[1]+parseInt(start_year) 
	txt = (display_day+1)+'/'+months_txt[month]+'/'+year
	if (unit_sets[unit_num] == "american"){
		txt = months_txt[month]+'/'+(display_day+1)+'/'+year
	}
	day = [coords[0]]*7+6
	var display_day = null
	var month = null
	for (i=0;i<month_lenghths.length;i++){
		if (day < month_lenghths.slice(0,i).reduce((a, b) => a + b, 0)){
			month = i-1
			display_day = day - month_lenghths.slice(0,i-1).reduce((a, b) => a + b, 0)
			break;
		}
	}
	if (month == null){
		display_day = day - month_lenghths.slice(0,11).reduce((a, b) => a + b, 0)
		month = 11
	}
	txt2 = (display_day+1)+'/'+months_txt[month]+'/'+year
	if (unit_sets[unit_num] == "american"){
		txt2 = months_txt[month]+'/'+(display_day+1)+'/'+year
	}
	if (save_clicks_x.length == 1){
		document.getElementById( "heder" ).innerHTML = "Details from the week "+txt+"-"+txt2;
	}
	else {
		document.getElementById( "heder" ).innerHTML = "Details from selected weeks"
	}
//	document.getElementById( 'txt' ).innerHTML = txt;
	
}
	
function HandleDelete() {
	if (selects.length == 0){
		return
	}
	for (i in selects){
		select = selects[i]
		select_draw = select_draws[i]
		num = select[1]
		var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
		click_dict = click_coords[num]
		select_draw.remove()
		if (select[0] == x_vals[0]){
			click_coords[num][x_vals[0]] = click_coords[num][x_vals[1]]
			DrawLines(num)
			select_draws = []
			selects = []
			RenderGrid()
			return
		}
		else if (select[0] == x_vals[x_vals.length-1]){
			click_coords[num][x_vals[x_vals.length-1]] = click_coords[num][x_vals[x_vals.length-2]]
			DrawLines(num)
			select_draws = []
			selects = []
			RenderGrid()
			return
		}
		delete click_dict[select[0]]
	}
	select_draws = [];
	selects = []
	DrawLines(num)
	RenderGrid()
}

function arrowHandler(y_dif) {
	if (selects.length == 0){
		return
	}
	var shift_mul = 1
	if (event.shiftKey){
		shift_mul = 10
	}
	for (i in selects){
		var select = selects[i]
		var select_draw = select_draws[i]
		var num = select[1]
		var val = select[0]
		click_dict = click_coords[num]
		click_dict[select[0]] += y_dif*shift_mul
		if (click_dict[select[0]] > histo_hights[num]){
			click_dict[select[0]] = histo_hights[num]
		}
		if (click_dict[select[0]] < 0){
			click_dict[select[0]] = 0
		}
		select_draw.remove()
		var draw = draws[num];
	    select_draw = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)-2 ).attr({
	        'fill':'#d55',
	        'shape-rendering':'crispEdges',
	        'stroke-width': 0 
	    });
	}
	DrawLines(num)
	RenderGrid()
}

function horizontalArrowHandler(x_dif) {
	if (selects.length == 0){
		return
	}
	var shift_mul = 1
	if (event.shiftKey){
		shift_mul = 10
	}
	for (i in selects){
		var select = selects[i]
		var select_draw = select_draws[i]
		var num = select[1]
		var val = select[0]
		var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
		var x_index = x_vals.indexOf(val)
		var new_x = parseInt(val)+x_dif*shift_mul
		if (new_x <= x_vals[x_index-1]){
			new_x = parseInt(x_vals[x_index-1]) + 1
		}
		else if (new_x < parseInt(x_vals[0])){
			new_x = parseInt(x_vals[0])
		}
		if (new_x >= x_vals[x_index+1]){
			new_x = parseInt(x_vals[x_index+1]) - 1
		}
		else if (new_x > parseInt(x_vals[x_vals.length-1])){
			new_x = parseInt(x_vals[x_vals.length-1])
		}
		click_dict = click_coords[num]
		y_val = click_dict[select[0]]
		if (parseInt(select[0]) != parseInt(x_vals[0]) && parseInt(select[0]) != parseInt(x_vals[x_vals.length-1])){
			delete click_dict[select[0]]
		}
		else if (Object.keys(click_coords[num]).length >= 10){
			return
		}
		click_dict[new_x] = y_val
		selects[i] = [new_x.toString(),num]
		select_draw.remove()
		var draw = draws[num];
	    select_draws[i] = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)+7 ).attr({
	        'fill':'#d55',
	        'shape-rendering':'crispEdges',
	        'stroke-width': 0 
	    });
	}
	DrawLines(num)
	RenderGrid()
}

function DrawLines(num) {
	for (line of lines[num]) {
		line.remove()
	}
	lines[num] = []
	var draw = draws[num];
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	for (var b = 0; b < x_vals.length-1; b ++) {
		lines[num].push(draw.line(0, histo_hights[num], x_vals[b+1]-x_vals[b], (click_coords[num][x_vals[b+1]]-click_coords[num][x_vals[b]]-histo_hights[num])*(-1))
		.move(x_vals[b], (Math.max(click_coords[num][x_vals[b+1]],click_coords[num][x_vals[b]])-histo_hights[num])*(-1)+9).attr({
					fill: '#000'
			, 'stroke-opacity': line_opacidy
					, stroke: '#000'
			, 'stroke-width': 1 
				}));
		lines[num].push(draw.circle(3).move(parseInt(x_vals[b])-1.5, (click_coords[num][x_vals[b]]-histo_hights[num])*(-1)+7.5).attr({
					fill: '#000'
			, 'fill-opacity': line_opacidy
					, stroke: '#ee0'
			, 'stroke-width': 0 
				}));
	}
	b = x_vals.length-1
	lines[num].push(draw.circle(3).move(parseInt(x_vals[b])-1.5, (click_coords[num][x_vals[b]]-histo_hights[num])*(-1)+7.5).attr({
					fill: '#000'
			, 'fill-opacity': line_opacidy
					, stroke: '#ee0'
			, 'stroke-width': 0 
				}));
}

function invertHandeler(num, will_render) {
	click_dict = click_coords[num]
	var x_vals = Object.keys(click_dict).sort((a,b) => a - b); //sort the keys
	for (val of x_vals) {
		click_dict[val] = click_dict[val]*(-1)+histo_hights[num]
	}
	DrawLines(num)
	if (will_render){
		RenderGrid()
	}
}

function DrawSesonalitys(){
	if (season_draw){
		season_draw.clear()
		season_draw.remove()
	}
	var num_years = wx_data.length
	document.getElementById( 'gr_sesonalitys').innerHTML = ""; // clear existing
	var draw = SVG().addTo('#gr_sesonalitys').size( 52*9+36, data_len*season_hight+offset);
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	season_draw = draw
    let months_txt = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec' ];
    for ( i=0; i < months_txt.length; i++ ) {
        let btext = draw.text( `${months_txt[i]}-` ).font('size',12).font('family','Arial');
        let bw = btext.length();        
        let bh = btext.bbox().height/2; // bbox is double for some reason.
        let bx = month_to_week( i ) * 9 + off_x;
        btext.center(bx,bw/2).rotate(90);
		// if (i != 0) {
// 	        draw.rect( 1, num_years*9-1 ).move( bx-1.5, 1  ).attr({
// 	            'fill':'#ffffff37',
// 	            'shape-rendering':'crispEdges',
// 	            'stroke-width': 0
// 	        });
// 		}
    }
	var dupe_color_data = []
	for (var i = 0; i < color_data.length; i ++){
		dupe_color_data.push(color_data[i].slice())
	}
	var inverted_color_data = color_data[0].map((_, colIndex) => color_data.map(row => row[colIndex]));
	for (var week = 0; week < 52; week ++){
		var sorted_week = inverted_color_data[week].slice().sort((a, b) => b[1] - a[1]);
		var fillcols = []
		if (sorted_week.length > 0) {
			var cp = 0
			fillcols.push(sorted_week[0].slice())
			fillcols[0].push(1)
			fillcols[0].push(0)
			for ( p=1; p<sorted_week.length; p++ ){
				if (sorted_week[p][0] == sorted_week[cp][0]) {
					fillcols.at(-1)[2] ++ 
				} else {
					fillcols.push(sorted_week[p].slice())
					fillcols.at(-1).push(1)
					fillcols.at(-1).push(p)
					cp = p
				}
			}
		}
		var acc_ind = 0
		for (var i = 0; i < fillcols.length; i ++){
			if (fillcols[i][1] != null){
				if (acc_ind == 0 && i < fillcols.length-1 && fillcols[i+1][1] != null && fillcols[i][2]+fillcols[i+1][2] <= 3 && color_grads){
					acc_ind = 2
					var color1 = fillcols[i][0]
					var color2 = fillcols[i+1][0]
					//var color3 = sorted_week[year+2][0]
					color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
					color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
					//color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
					var color = '#'
					for (var k = 0; k < 3; k++){
						var color_part = parseInt((color1[k]+color2[k])/2).toString(16)
						if (color_part.length == 0){
							color_part = "00"
						} else if (color_part.length == 1){
							color_part = "0" + color_part
						}
						color += color_part
					}
			        draw.rect( 9, (fillcols[i][2]+fillcols[i+1][2])*season_hight ).move( week*9+35, (data_len-fillcols[i][3]-fillcols[i][2]-fillcols[i+1][2])*season_hight+offset).attr({
			            'fill':color,
			            'shape-rendering':'crispEdges',
			            'stroke-width': 0 
			        });
				} else if (acc_ind == 0) {
					acc_ind = 1
			        draw.rect( 9, fillcols[i][2]*season_hight ).move( week*9+35, (data_len-fillcols[i][3]-fillcols[i][2])*season_hight+offset).attr({
			            'fill':fillcols[i][0],
			            'shape-rendering':'crispEdges',
			            'stroke-width': 0 
			        });
				}
				acc_ind --
			}
		}
		// for (var year = 0; year < num_years; year ++){
// 			if (sorted_week[year][1] != null){
// 				if (year%2 == 0 && year < num_years-1 && sorted_week[year+1][1] != null){
// 					var color1 = sorted_week[year][0]
// 					var color2 = sorted_week[year+1][0]
// 					//var color3 = sorted_week[year+2][0]
// 					color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
// 					color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
// 					//color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
// 					var color = '#'
// 					for (var k = 0; k < 3; k++){
// 						var color_part = parseInt((color1[k]+color2[k])/2).toString(16)
// 						if (color_part.length == 0){
// 							color_part = "00"
// 						} else if (color_part.length == 1){
// 							color_part = "0" + color_part
// 						}
// 						color += color_part
// 					}
// 					draw.rect( 9, season_hight*2 ).move( week*9+35, (data_len-year)*season_hight+offset).attr({
// 			            'fill':color,
// 			            'shape-rendering':'crispEdges',
// 			            'stroke-width': 0
// 			        });
// 				} else if (year >= num_years-1 || sorted_week[year+1][1] == null) {
// 					draw.rect( 9, season_hight ).move( week*9+35, (data_len-year)*season_hight+offset).attr({
// 			            'fill':sorted_week[year][0],
// 			            'shape-rendering':'crispEdges',
// 			            'stroke-width': 0
// 			        });
// 				}
// 			}
// 		}
	}
	if (save_clicks_x.length != 0) {
		draw.rect( 52*9, (data_len)*season_hight).move(35,offset).attr({
            'fill':"#ffffffdd",
            'shape-rendering':'crispEdges',
            'stroke-width': 0
        });
		var filtered_data = new Array(52).fill().map(e => []);
		for (var index = 0; index < save_clicks_x.length; index ++){
			let year = wx_data.length - save_clicks_y[index] - 1
			let week = save_clicks_x[index]
			if (color_data[year][week][1] != null){
		        filtered_data[week].push(color_data[year][week])
			}
		}
		var max_len = 0
		for (var week = 0; week < 52; week ++){
			if (filtered_data[week].length > max_len){
				max_len = filtered_data[week].length
			}
		}
		var scale = data_len/max_len
		for (var week = 0; week < 52; week ++){
			var sorted_week = filtered_data[week].slice().sort((a, b) => b[1] - a[1]);
			var fillcols = []
			if (sorted_week.length > 0) {
				var cp = 0
				fillcols.push(sorted_week[0].slice())
				fillcols[0].push(1)
				fillcols[0].push(0)
				for ( p=1; p<sorted_week.length; p++ ){
					if (sorted_week[p][0] == sorted_week[cp][0]) {
						fillcols.at(-1)[2] ++ 
					} else {
						fillcols.push(sorted_week[p].slice())
						fillcols.at(-1).push(1)
						fillcols.at(-1).push(p)
						cp = p
					}
				}
			}
			var acc_ind = 0
			for (var i = 0; i < fillcols.length; i ++){
				if (fillcols[i][1] != null){
					if (acc_ind == 0 && i < fillcols.length-1 && fillcols[i+1][1] != null && fillcols[i][2]+fillcols[i+1][2] <= 3 && color_grads){
						acc_ind = 2
						var color1 = fillcols[i][0]
						var color2 = fillcols[i+1][0]
						//var color3 = sorted_week[year+2][0]
						color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
						color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
						//color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
						var color = '#'
						for (var k = 0; k < 3; k++){
							var color_part = parseInt((color1[k]+color2[k])/2).toString(16)
							if (color_part.length == 0){
								color_part = "00"
							} else if (color_part.length == 1){
								color_part = "0" + color_part
							}
							color += color_part
						}
				        draw.rect( 9, (fillcols[i][2]+fillcols[i+1][2])*season_hight*scale ).move( week*9+35, (data_len-(fillcols[i][3]+fillcols[i][2]+fillcols[i+1][2])*scale)*season_hight+offset).attr({
				            'fill':color,
				            'shape-rendering':'crispEdges',
				            'stroke-width': 0 
				        });
					} else if (acc_ind == 0) {
						acc_ind = 1
				        draw.rect( 9, fillcols[i][2]*season_hight*scale ).move( week*9+35, (data_len-(fillcols[i][3]+fillcols[i][2])*scale)*season_hight+offset).attr({
				            'fill':fillcols[i][0],
				            'shape-rendering':'crispEdges',
				            'stroke-width': 0 
				        });
					}
					acc_ind --
				}
			}
		}
	}
	// for (var week = 0; week < 52; week ++){
	// 	var sorted_week = inverted_color_data[week].slice().sort((a, b) => b[1] - a[1]);
	// 	for (var year = 0; year < compresed_data.length; year ++){
	// 		if (sorted_week[year][1] != null){
	// 			draw.rect( 9, 0.5 ).move( week*9+35, (data_len-year)*0.5+offset).attr({
	// 	            'fill':sorted_week[year][0],
	// 	            'shape-rendering':'crispEdges',
	// 	            'stroke-width': 0
	// 	        });
	// 		}
	// 	}
	// }
	
	// for (var i = 0; i < 52; i++) {
//
// 		var fillcol = '#ffffff'
//         draw.rect( 9, color_plot[2][i]*0.5 ).move( i*9+35, (data_len-color_plot[2][i])*0.5+offset).attr({
//             'fill':color_lists[color_num][2],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
//         draw.rect( 9, color_plot[1][i]*0.5 ).move( i*9+35, (data_len-(color_plot[2][i]+color_plot[1][i]))*0.5+offset).attr({
//             'fill':color_lists[color_num][1],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
//         draw.rect( 9, color_plot[0][i]*0.5 ).move( i*9+35, (data_len-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i]))*0.5+offset).attr({
//             'fill':color_lists[color_num][0],
//             'shape-rendering':'crispEdges',
//             'stroke-width': 0
//         });
// 	}
    for ( i=0; i < months_txt.length; i++ ) {
        let bx = month_to_week( i ) * 9 + 35;
		if (i != 0) {
	        draw.rect( 1, wx_data.length*0.5-1 ).move( bx-1.5, 1  ).attr({
	            'fill':'#ffffff37',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0
	        });
		}
    }
}
function DrawYears(){
	var num_years = wx_data.length
	if (year_draw){
		year_draw.clear()
		year_draw.remove()
	}
	var draw = SVG().addTo('#gr_years').size( 52*3 + 22, (wx_data.length+1)*10+10 );
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	year_draw = draw
	move = 0
	if (doPDO){
		move = 22
	}
	var line_years = []
	for (var year = 0; year < num_years; year ++){
        syear = num_years + start_year - year;    
        if ( !((syear-1)%5) ) {
			var opacity = "37"
			if (!((syear-1)%10)){
				var opacity = "bb" 
			}
			line_years.push([opacity,year])
		}
		var sorted_year = color_data[year].slice().sort((a, b) => b[1] - a[1]);
		var fillcols = []
		if (sorted_year.length > 0) {
			var cp = 0
			fillcols.push(sorted_year[0].slice())
			fillcols[0].push(1)
			fillcols[0].push(0)
			for ( p=1; p<sorted_year.length; p++ ){
				if (sorted_year[p][0] == sorted_year[cp][0]) {
					fillcols.at(-1)[2] ++ 
				} else {
					fillcols.push(sorted_year[p].slice())
					fillcols.at(-1).push(1)
					fillcols.at(-1).push(p)
					cp = p
				}
			}
		}
		var acc_ind = 0
		for (var i = 0; i < fillcols.length; i ++){
			if (fillcols[i][1] != null){
				if (acc_ind == 0 && i < fillcols.length-1 && fillcols[i+1][1] != null && fillcols[i][2]+fillcols[i+1][2] <= 2 && color_grads){
					acc_ind = 2
					var color1 = fillcols[i][0]
					var color2 = fillcols[i+1][0]
					//var color3 = sorted_week[year+2][0]
					color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
					color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
					//color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
					var color = '#'
					for (var k = 0; k < 3; k++){
						var color_part = parseInt((color1[k]+color2[k])/2).toString(16)
						if (color_part.length == 0){
							color_part = "00"
						} else if (color_part.length == 1){
							color_part = "0" + color_part
						}
						color += color_part
					}
			        draw.rect( (fillcols[i][2]+fillcols[i+1][2])*3, 9 ).move( move+fillcols[i][3]*3, (year+1)*9+data_len*season_hight+offset+5).attr({
			            'fill':color,
			            'shape-rendering':'crispEdges',
			            'stroke-width': 0 
			        });
				} else if (acc_ind == 0) {
					acc_ind = 1
			        draw.rect( fillcols[i][2]*3, 9 ).move( move+fillcols[i][3]*3, (year+1)*9+data_len*season_hight+offset+5).attr({
			            'fill':fillcols[i][0],
			            'shape-rendering':'crispEdges',
			            'stroke-width': 0 
			        });
				}
				acc_ind --
			}
		}
	}
	if (save_clicks_x.length != 0) {
        draw.rect( 52*3, (num_years+1)*9).move( move,data_len*season_hight+offset+5).attr({
            'fill':"#ffffffdd",
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
		var filtered_data = new Array(wx_data.length).fill().map(e => []);
		for (var index = 0; index < save_clicks_x.length; index ++){
			let year = wx_data.length - save_clicks_y[index] - 1
			let week = save_clicks_x[index]
			if (color_data[year][week][1] != null){
		        filtered_data[year].push(color_data[year][week])
			}
		}
		var max_len = 0
		for (var year = 0; year < num_years; year ++){
			if (filtered_data[year].length > max_len){
				max_len = filtered_data[year].length
			}
		}
		var scale = 52/max_len
		for (var year = 0; year < num_years; year ++){
	        syear = num_years + start_year - year;    
	        if ( !((syear-1)%5) ) {
				var opacity = "37"
				if (!((syear-1)%10)){
					var opacity = "bb" 
				}
				line_years.push([opacity,year])
			}
			var sorted_year = filtered_data[year].slice().sort((a, b) => b[1] - a[1]);
			var fillcols = []
			if (sorted_year.length > 0) {
				var cp = 0
				fillcols.push(sorted_year[0].slice())
				fillcols[0].push(1)
				fillcols[0].push(0)
				for ( p=1; p<sorted_year.length; p++ ){
					if (sorted_year[p][0] == sorted_year[cp][0]) {
						fillcols.at(-1)[2] ++ 
					} else {
						fillcols.push(sorted_year[p].slice())
						fillcols.at(-1).push(1)
						fillcols.at(-1).push(p)
						cp = p
					}
				}
			}
			var acc_ind = 0
			for (var i = 0; i < fillcols.length; i ++){
				if (fillcols[i][1] != null){
					if (acc_ind == 0 && i < fillcols.length-1 && fillcols[i+1][1] != null && fillcols[i][2]+fillcols[i+1][2] <= 2 && color_grads){
						acc_ind = 2
						var color1 = fillcols[i][0]
						var color2 = fillcols[i+1][0]
						//var color3 = sorted_week[year+2][0]
						color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
						color2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5),16)]
						//color3 = [parseInt(color3.slice(1,3),16),parseInt(color3.slice(3,5),16),parseInt(color3.slice(5),16)]
						var color = '#'
						for (var k = 0; k < 3; k++){
							var color_part = parseInt((color1[k]+color2[k])/2).toString(16)
							if (color_part.length == 0){
								color_part = "00"
							} else if (color_part.length == 1){
								color_part = "0" + color_part
							}
							color += color_part
						}
				        draw.rect( (fillcols[i][2]+fillcols[i+1][2])*3*scale, 9 ).move( move+fillcols[i][3]*3*scale, (year+1)*9+data_len*season_hight+offset+5).attr({
				            'fill':color,
				            'shape-rendering':'crispEdges',
				            'stroke-width': 0 
				        });
					} else if (acc_ind == 0) {
						acc_ind = 1
				        draw.rect( fillcols[i][2]*3*scale, 9 ).move( move+fillcols[i][3]*3*scale, (year+1)*9+data_len*season_hight+offset+5).attr({
				            'fill':fillcols[i][0],
				            'shape-rendering':'crispEdges',
				            'stroke-width': 0 
				        });
					}
					acc_ind --
				}
			}
		}
	}
	for (var i = 0; i < wx_data.length; i++) {
		        //
        // draw.rect( color_plot[2][i]*3, 9 ).move( move, (compresed_data.length-i)*9+data_len/2+offset+5).attr({
        //     'fill':color_lists[color_num][2],
        //     'shape-rendering':'crispEdges',
        //     'stroke-width': 0
        // });
        // draw.rect( color_plot[1][i]*3, 9 ).move( color_plot[2][i]*3 + move, (compresed_data.length-i)*9+data_len/2+offset+5).attr({
        //     'fill':color_lists[color_num][1],
        //     'shape-rendering':'crispEdges',
        //     'stroke-width': 0
        // });
        // draw.rect( color_plot[0][i]*3, 9 ).move( (color_plot[2][i]+color_plot[1][i])*3 + move, (compresed_data.length-i)*9+data_len/2+offset+5).attr({
        //     'fill':color_lists[color_num][0],
        //     'shape-rendering':'crispEdges',
        //     'stroke-width': 0
        // });
		if (doPDO){
			if ((i < PDO.length) && (PDO[i] > 0.75)) {
		        draw.circle( 8 ).move( 0, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][2],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0, 
		        });
			}
			else if ((i < PDO.length) && (PDO[i] > -0.75)) {
		        draw.circle( 8 ).move( 0, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][1],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0 , 
		        });
			}
			else if (i < PDO.length) {
		        draw.circle( 8 ).move( 0, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][0],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0 , 
		        });
			}
			if ((i < ENSO.length) && (ENSO[i] > 0.75)) {
		        draw.circle( 8 ).move( 11, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][2],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0 
		        });
			}
			else if ((i < ENSO.length) && (ENSO[i] > -0.75)) {
		        draw.circle( 8 ).move( 11, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][1],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0 
		        });
			}
			else if (i < ENSO.length) {
		        draw.circle( 8 ).move( 11, (wx_data.length-i)*9+data_len*season_hight+offset+5).attr({
		            'fill':color_lists[2][0],
		            'shape-rendering':'crispEdges',
		            'stroke-width': 0 
		        });
			}
		}
	}
	for (var i = 0; i < 4; i++) {
        draw.rect( 2, (compresed_data.length)*9 ).move( (i+1)*31+move, data_len*season_hight+offset+14  ).attr({
            'fill':'#ffffff66',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
	for (year of line_years) {
        draw.rect( 52*3 +22, 1 ).move( 0, year[1]*9+9+data_len*season_hight+offset+5).attr({
            'fill':'#ffffff'+year[0],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
	if (doPDO){
		var PDOoffset = wx_data.length-PDO.length
		var ENSOoffset = wx_data.length-ENSO.length
	
	    let btextPDO = draw.text( `- PDO` ).font('size',10).font('family','Arial');
	    let bwPDO = btextPDO.length();   
		let bhPDO = btextPDO.bbox().height; // bbox is double for some reason.     
	    btextPDO.center(4.5,wx_data.length/2+9*PDOoffset-2).rotate(270);
	
	    let btextENSO = draw.text( `- ENSO` ).font('size',10).font('family','Arial');
	    let bwENSO = btextENSO.length();   
		let bhENSO = btextENSO.bbox().height; // bbox is double for some reason.     
	    btextENSO.center(15.5 ,wx_data.length/2+9*ENSOoffset-5.5).rotate(270);
	}
//	year_histogram = color_plot
}

function getSizesBup(data,base_size,div){
	trend_list = []
	trend_type = null
	sizes = []
	for (var i = 0; i < data.length; i++){
		sizes.push([])
		for (var j = 0; j < data[i].length; j++){
			let val = data[i][j]
			let val_type = -1
            if ( val/255 < wx_range_val0 ){
                val_type = 0;
	        }
            else if ( val/255 < wx_range_val1 ){
                val_type = 1;
            }
            else {
                val_type = 2;
            }
			if (val == null){
				let step = base_size*div
				let t_len = trend_list.length
				for (var k = 0; k < t_len; k++){
					if (k < t_len/2){
						sizes[trend_list[k]].push(Math.min(step*(k+1),base_size))
					}
					else {
						sizes[trend_list[k]].push(Math.min(step*(t_len-k),base_size))
					}
				}
				trend_type = -1
				trend_list = []
				trend_list.push(i)
			}
			else if (trend_type == null || trend_type == val_type){
				trend_list.push(i)
				trend_type = val_type
			}
			else {
				let step = base_size*div
				let t_len = trend_list.length
				for (var k = 0; k < t_len; k++){
					if (k < t_len/2){
						sizes[trend_list[k]].push(Math.min(step*(k+1),base_size))
					}
					else {
						sizes[trend_list[k]].push(Math.min(step*(t_len-k),base_size))
					}
				}
				trend_type = val_type
				trend_list = []
				trend_list.push(i)
			}
		}
	}
	let step = base_size*div
	let t_len = trend_list.length
	for (var k = 0; k < t_len; k++){
		if (k < t_len/2){
			sizes[trend_list[k]].push(Math.min(step*(k+1),base_size))
		}
		else {
			sizes[trend_list[k]].push(Math.min(step*(t_len-k),base_size))
		}
	}
	return sizes;
}

function getSizes(data,base_size,sensetivity){
	var trend_list = new Array((sensetivity+1)).fill(0);
	let range = sensetivity*2+1
	sizes = []
	for (var i = 0; i < sensetivity; i++){
		let val = data[0][i]
		let val_num = 0
        if ( val/255 < wx_range_val0 ){
            val_num = 0;
        }
        else if ( val/255 < wx_range_val1 ){
            val_num = 1/2;
        }
        else {
            val_num = 2;
        }
		trend_list.push(val_num)
	}
	var c_total = trend_list.reduce((a, b) => a + b, 0)
	var st = sensetivity
	var ind = 0
	for (var i = 0; i < data.length; i++){
		sizes.push([])
		for (var j = st; j < data[i].length; j++){
			let val = data[i][j]
			let val_num = 0
            if ( val/255 < wx_range_val0 ){
                val_num = 0;
	        }
            else if ( val/255 < wx_range_val1 ){
                val_num = 1/2;
            }
            else {
                val_num = 2;
            }
			c_total -= trend_list.shift()
			trend_list.push(val_num)
			c_total += val_num
			sizes[ind].push(c_total/range)
			if (sizes[ind].length == 52){
				ind++
			}
		}
		st = 0
	}
	for (var i = 0; i < sensetivity; i++){
		c_total -= trend_list.shift()
		trend_list.push(0)
		sizes[ind].push(base_size*c_total/range)
		if (sizes[ind].length == 52){
			ind++
		}
	}
	var trend_len = 0
	var trends = new Array(sizes.length).fill().map(e => [])
	var ind = 0
	for (var i = 0; i < sizes.length; i++){
		for (var j = 0; j < sizes[i].length; j++){
			if (sizes[i][j] < 1){
				var size = 0
				if (trend_len >= sensetivity*2+1){
					size = base_size
				}
				for (var k = 0; k < trend_len; k++){
					trends[ind].push(size)
					if (trends[ind].length == 52){
						ind++
					}
				}
				trends[ind].push(0)
				if (trends[ind].length == 52){
					ind++
				}
				trend_len = 0
			} else {
				trend_len ++
			}
		}
	}
	return trends;
}
function getGradColor(val,log_vars){
	a = wx_range_val0
	b = wx_range_val1
	if (val < a) {
		t = val/a
		var prod = (-(t**3)+(t**2)+t)/3+2*a*((t**3)-(t**2))/(3*b)
	} else if (val < b){
		m1 = 2/(3*b)
		m2 = 2/(3*(1-a))
		t = (val-a)/(b-a)
		var prod = (-2*(t**3)+3*(t**2)+1)/3+((t**3)-2*(t**2)+t)*m1*(b-a)+((t**3)-(t**2))*m2*(b-a)
	} else {
		if (val == 1){
			var prod = 1
		} else {
			m2 = 2/(3*(1-a))
			t = (val-b)/(1-b)
			var prod = (5*(t**3)-7*(t**2)+2)/3+((t**3)-2*(t**2)+t)*m2*(1-b)+(-2*(t**3)+3*(t**2))
		}
	}
	if (prod < 0.5) {
		color0 = color_lists[color_num][0]
		color1 = color_lists[color_num][1]
		prod = (prod*2)**2
		
	} else {
		color0 = color_lists[color_num][1]
		color1 = color_lists[color_num][2]
		prod = 1-(2-prod*2)**2
	}
	var color0 = [parseInt(color0.slice(1,3),16),parseInt(color0.slice(3,5),16),parseInt(color0.slice(5),16)]
	var color1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5),16)]
	var color = '#'
	for (var i = 0; i < 3; i++){
		var color_part = parseInt((color1[i]-color0[i])*prod+color0[i]).toString(16)
		if (color_part.length == 0){
			color_part = "00"
		} else if (color_part.length == 1){
			color_part = "0" + color_part
		}
		color += color_part
	}
	return color
}

function RenderGrid(){
	//console.log("render")
	let t1 = Date.now()
    if ( wx_grdata == null )
        return;

	if (!has_reading)
		return;
	grid_cells = []
    var year_label_width = 35;
    var month_label_height = 25;
    off_x = year_label_width;         // grid offset
    var off_y = 1;
    var boxsize = 9;        // size of a grid unit
    var boxspace = boxsize;      // total space from unit to unit

    var num_weeks = 52;	
	wx_data = [];
    num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	var grids = [];
	for ( var i = 0; i < reading_types.length; i++ ){
		grids.push(wx_grdata[reading_types[i]][method_types[i]]);		
	};
	var num_years = grids[0].length;
	const total_weight = weight_vals.reduce((a, b) => a + b, 0); //summing the weights
	for ( var n = 0; n < num_years; n++ ) {
		wx_data.push([]);
		for ( var m = 0; m < num_weeks; m++ ) {
			var num = 0;
			for ( var k = 0; k < grids.length; k++ ){ 
				if (grids[k][n][m] == null){
					num = null
					break
				}
				var relev_coords = []
				var grid_val = grids[k][n][m]
				if (grid_val > 255){
					grid_val = 255
				}
				if (grid_val < 0){
					grid_val = 0
				}
				x_vals = Object.keys(click_coords[k]).sort((a,b) => a - b);
				for ( var j = 0; j < x_vals.length; j++ ){
					if (x_vals[j]-15 > grid_val) {
						relev_coords = [x_vals[j-1],x_vals[j]]
						break
					}
				}
				var ofset = click_coords[k][relev_coords[0]]*255/histo_hights[k]
				if (Math.abs(click_coords[k][relev_coords[0]]-click_coords[k][relev_coords[1]]) < 0.001){
					var mul = 0
				}
				else {
					var mul = (click_coords[k][relev_coords[1]]-click_coords[k][relev_coords[0]])*255/((relev_coords[1]-relev_coords[0])*histo_hights[k])
				}
				num += ((grid_val+15-relev_coords[0])*mul+ofset)*weight_vals[k];
			}
			// if (isNaN(num)){
// 				console.log("NaN")
// 			}
			if (num == null){
				wx_data[n].push(null)
			} else {
				wx_data[n].push(num/total_weight);
				// if (wx_data[n].at(-1) === NaN){
// 					console.log("NaN")
// 				}
			}
		}
	}
	compresed_data = wx_data
	DrawHistograms(wx_data)
	bsizes = []
	if (is_trend){
		bsizes = getSizes(compresed_data,boxsize,sensetivity)
	}
	else {
		bsizes = Array(num_years).fill().map(() => 
               Array(num_weeks).fill(boxsize));
	}
    var color0 = color_lists[color_num][0];
    var color1 = color_lists[color_num][1];
    var color2 = color_lists[color_num][2];
    // create the svg drawing object and draw the grid elements    
    var total_width = boxspace * num_weeks + year_label_width;
    var total_height = boxspace * num_years + off_y + month_label_height;
	if (grid_draw){
		grid_draw.clear()
		grid_draw.remove()
		gridlines = []
		outlines = []
	}
	let t2 = Date.now()
    var draw = SVG().addTo('#gr_grid').size( total_width+1, total_height);
    draw.attr({
        'shape-rendering':'crispEdges'
    });
	grid_draw = draw
	color_data = []
    for ( k=0; k<num_years; k++ ) {
		color_data.push([])
		grid_cells.push([])
        sy = k * boxspace + off_y;
        // draw year label every 3 rows, vertically centered on the row, to the left of the grid
        syear = num_years + start_year - k;  
		var opacity = "bb"      
        if ( !((syear-1)%5) || k == 0) {
			if (!((syear-1)%10)){
				opacity = "ff" 
			}
            var stext = draw.text( `${syear-1}` ).font('size',12).font('family','Arial');
            syear_width = stext.length()+6;
            syear_height = stext.bbox().height/2; // bbox is double for some reason.
            stext.move( off_x - syear_width, sy - 2 );
        }
		var fillcols = []
        for ( p=0; p<num_weeks; p++ ) {
            // var fillcol = color0;
            // if ( Math.floor(Math.random() * 6)==0 )
            //     fillcol = color1;
            // else if ( Math.floor(Math.random() * 9)==0 )
            //     fillcol = color2;

            // get measurement, years are reversed order, & calculate fill color
            var fillcol = 0;
	        let shape_rend = 'crispEdges';	// render the contigous blocks with crispedges
            var bsize = bsizes[num_years-1-k][p]
			var mb = (boxsize-bsize)/2
            var mx = wx_data[num_years-1-k][p];
            if ( mx == null ) {
                fillcol = null;    // nulls are this color
            } else {
                mx = mx / 255;
				if (color_grads){
					fillcol = getGradColor(mx,p == 0)
				} else {
	                if ( mx < wx_range_val0 ){
	                    fillcol = color0;
			            shape_rend = 'auto';		// draw the blue grid blocks with AntiAliasing
			        }
	                else if ( mx < wx_range_val1 ){
	                    fillcol = color1;
	                }
	                else {
	                    fillcol = color2;
	                }
				}
            }
			color_data[k].push([fillcol,mx])
			sx = p * boxspace + off_x;
			fillcols.push([fillcol,bsize,mb,shape_rend,sx,sy,1])
            // draw.rect( bsize, bsize ).move( sx+mb, sy+mb).attr({
//                 'fill':fillcol,
//                 'shape-rendering':shape_rend,
//                 'stroke-width': 0
//             });
		}
		var cp = 0
		for ( p=1; p<num_weeks; p++ ){
			if (fillcols[p][0] == fillcols[cp][0]) {
				fillcols[cp][6] ++
				fillcols[p][6] = 0
			} else {
				cp = p
			}
		}
		for ( p=0; p<num_weeks; p++ ) {
			if (fillcols[p][0] && fillcols[p][1] > 0 && fillcols[p][6] > 0){
	            var rect = draw.rect( fillcols[p][6]*fillcols[p][1], fillcols[p][1] ).move( fillcols[p][4]+fillcols[p][2], fillcols[p][5]+fillcols[p][2] ).attr({
	                'fill':fillcols[p][0],
	                'shape-rendering':fillcols[p][3],
	                'stroke-width': 0
	            });
			}
        }

        gridlines.push(draw.rect( (num_weeks) * boxspace, 1 ).move( off_x, sy ).attr({
            'fill':'#ffffff'+opacity,
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        }));
    }

    // draw bottom month labels
    let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec' ];
    let by = num_years * (boxspace) + off_y - (boxspace-boxsize);
    for ( i=0; i < months.length; i++ ) {
        let btext = draw.text( `-${months[i]}` ).font('size',12).font('family','Arial');
        let bw = btext.length();        
        let bh = btext.bbox().height/2; // bbox is double for some reason.
        let bx = month_to_week( i ) * boxspace + off_x;
        btext.center(bx,by+bw/2).rotate(90);
		if (i != 0) {
	        gridlines.push(draw.rect( 1, num_years*9-1 ).move( bx-1.5, 1  ).attr({
	            'fill':'#ffffff37',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        }));
		}
    }
	let t3 = Date.now()
	// DrawSesonalitys()
// 	DrawYears()
	let t4 = Date.now()
	DetectGridClick(null,true)
	// if (selected_years.length){
	// 	DetectYearClick(null,true)
	// }
	// if (selected_seasons.length){
	// 	DetectSeasonClick(null,true)
	// }
	let t5 = Date.now()
	// console.log(t5-t1)
// 	console.log(t2-t1)
// 	console.log(t3-t2)
// 	console.log(t4-t3)
// 	console.log(t5-t4)
};
//file:///Users/katmai/Downloads/test.json
//file:///Users/katmai/Downloads/test.json