/// HWITW project Copyright (C) 2021
// initialize as an array LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value)of zeros. an empty grid.
var wx_grdata = {"":Array(60).fill().map(() => Array(52).fill(0))}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid
var o = [1,5,6,4,5,2,3]
o.splice(5,1)
console.log(o)

var histo_hights = []
document.onkeydown = function() {
    var key = event.keyCode || event.charCode;

    if ( key == 8 || key == 46 ) {
        HandleDelete()
	}
	if (key == 38) {
		arrowHandler(1)
	}
	if (key == 40) {
		arrowHandler(-1)
	}
	if (key == 37) {
		horizontalArrowHandler(-1)
	}
	if (key == 39) {
		horizontalArrowHandler(1)
	}
	if (key == 13) {
		select = null
		if (select_draw != null){
			select_draw.remove()
		}
		select_draw = null
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
//download('test.json', "Hello world!");
var lines = []
var year_draw = null
var season_draw = null
var highlights = []
var unit_sets = ['metric','american']
var unit_num = 0
var histo_data = []
var invert_btns = []
var file_names = []
var mins = []
var selected_years = []
var year_covers = []
var selected_seasons = []
var season_covers = []
var covers = []
var states = []
var state_index = null
var maxes = []
var select = null
var select_draw = null
var draws = []
var compresed_data = []
var is_valid = 1
var wx_grdata_min = 0.0;
var wx_grdata_max = 1.0;
var wx_range_val0 = 0.33;
var wx_range_val1 = 0.66;
var save_clicks_x = []
var save_clicks_y = []
var weight_val = 0.01
var weight_val2 = 0.01
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
var fade = null
var short_names = {}
var prevs = []
var PDO = [-2.24, -1.12, -1.55, -0.64, -0.4, -2.07, -1.81, 0.29, 0.86, 0.27, 0.04, -0.57, -1.1, -0.24, -0.89, -0.14, -0.44, -0.74, -0.15, -0.34, -0.4, -1.32, -1.14, -1.14, -0.3, -1.41, -0.15, 0.05, 0.07, 0.11, 0.31, 0.84, -0.26, 1.25, 0.6, 0.03, 1.01, 1.14, -0.04, -0.5, -0.83, -0.88, 0.76, 1.04, -0.49, 0.44, 0.68, 1.32, -0.48, -1.84, -1.13, -1.13, -0.44, 0.38, -0.22, -0.19, -0.35, -0.7, -1.66, -1.03, -1.06, -1.81, -1.73, -1.17, 0.55, 0.92, 0.67, -0.1, -0.36, -0.15, -1.14, -1.88]
var ENSO = [-1.31, 0.45, 0.03, 0.65, -0.45, -1.16, -0.97, 0.6, 0.58, 0.09, -0.13, -0.06, -0.34, 0.44, -0.55, 0.88, 0.46, -0.29, -0.05, 0.72, -0.3, -1.04, 0.96, -0.67, -1.0, -1.24, -0.04, 0.86, 0.03, 0.26, 0.31, -0.17, 0.97, 1.22, -0.32, -0.43, 0.3, 1.37, -0.87, -0.82, 0.18, 0.61, 1.16, 0.88, 0.5, -0.18, -0.61, 1.17, 0.32, -1.24, -0.85, -0.39, 0.35, 0.17, 0.14, -0.02, 0.02, -0.6, -1.09, -0.03, -0.89, -1.34, -0.32, -0.41, -0.02, 1.28, 0.45, -0.5, -0.29, 0.34, -0.59, -1.2]
var start_year = 0
var is_setting = false // dir_net
var is_active = true
var color_lists = [['#dadaeb','#9e9ac8','#54278f'],['#ffffb2','#fecc5c','#e31a1c'],['#1871bc','#f7e3f7','#ef8a62'],['#bdd7e7','#6baed6','#1871bc'],['#bae4b3','#74c476','#006d2c'],['#ffc','#b2aa93','#110800'],['#e9a3c9','#f7f7f7','#a1d76a']]
var color_num = 0
const input_dict = {"temperature":[-60,131.25,0.75],"ceiling":[0,6375,25], "precipitation":[0,.00255,.00001], "cloud cover":[0,1,0.004]};
var wxgrid_url = `/wxapp/getwxvar`;
fetch( wxgrid_url, {   method:'GET',
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
				start_year = start_data["data_specs"]["start_year"];
				document.getElementById( 'location' ).innerHTML = start_data["data_specs"]["Name"];
				compresion_types = start_data["compression"];
				compresion = {}
				start_data = start_data["variables"];
				all_data = {}
				for (mesurment of Object.keys(start_data)){
					compresion[mesurment] = {}
					all_data[mesurment] = {}
					short_names[mesurment] = {}
					for (func of Object.keys(start_data[mesurment])){
						compresion[mesurment][func] = compresion_types[start_data[mesurment][func]["compression"]]
						all_data[mesurment][func] = []
						short_names[mesurment][func] = start_data[mesurment][func]["short_name"]
						for (var i = 0; i < start_data[mesurment][func]["data"].length; i++){
							all_data[mesurment][func].push([])
							for (var j = 0; j < start_data[mesurment][func]["data"][i].length; j++){
								all_data[mesurment][func][i].push(0)
								if (start_data[mesurment][func]["data"][i][j] == 255 || start_data[mesurment][func]["data"][i][j] == null){
									all_data[mesurment][func][i][j] = null
								}
								else {
									all_data[mesurment][func][i][j] = start_data[mesurment][func]["data"][i][j]
								}
							}
						}
					}
				}
				unitNamesHandaler()
				unitMulHandaler()
				makeNewMeasurmeant(0)
            }
        );
    }
)
.catch(function(err) {
    console.error('Fetch Error -', err);
});
var color_selector = document.getElementById("color_selector")
color_selector.onchange =
		function () {
			color_num = parseInt(color_selector.value)
			RenderGrid()
		};
var unit_selector = document.getElementById("unit_selector")
unit_selector.onchange =
		function () {
			unit_num = parseInt(unit_selector.value)
			RenderGrid()
		};
var unit_names = {'metric':{'temperature':{'default':'°C'},'relative_humidity':{'default':'%'},'wind':{'default':' m/s','dir_modal':'°','dir_net':'°'},'precipitation':{'default':'cm'},'cloud_cover':{'default':'%'}},'american':{'temperature':{'default':'°F'},'relative_humidity':{'default':'%'},'wind':{'default':' mph','dir_modal':'°','dir_net':'°'},'precipitation':{'default':' in.'},'cloud_cover':{'default':'%'}}};
function unitNamesHandaler(){
	var reading_options = Object.keys(all_data)
	console.log(all_data)  
	console.log(reading_options) 
	for (unit_set of unit_sets){  
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]])
			for (var j=0; j < method_options.length; j++){ 
				console.log(unit_names[unit_set][reading_options[i]][method_options[j]])
				if (unit_names[unit_set][reading_options[i]][method_options[j]] == undefined){
					console.log(unit_names[unit_set][reading_options[i]][method_options[j]])
					unit_names[unit_set][reading_options[i]][method_options[j]] = unit_names[unit_set][reading_options[i]]['default']
					console.log(unit_names[unit_set][reading_options[i]][method_options[j]])
				}
			}
		}
	}
}
var unit_muls = {'metric':{'temperature':{'default':[1,0,1]},'relative_humidity':{'default':[100,0,0]},'wind':{'default':[1,0,0]},'precipitation':{'default':[100,0,2]},'cloud_cover':{'default':[100,0,0]}},'american':{'temperature':{'default':[9/5,32,1]},'relative_humidity':{'default':[100,0,0]},'wind':{'default':[2.237,0,0],'dir_modal':[1,0,0],'dir_net':[1,0,0]},'precipitation':{'default':[39.37,0,2]},'cloud_cover':{'default':[100,0,0]}}};
function unitMulHandaler(){
	var reading_options = Object.keys(all_data)
	console.log(all_data)  
	console.log(reading_options) 
	for (unit_set of unit_sets){  
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]])
			console.log(method_options) 
			for (var j=0; j < method_options.length; j++){ 
				
				if (unit_muls[unit_set][reading_options[i]][method_options[j]] == undefined){
					unit_muls[unit_set][reading_options[i]][method_options[j]] = unit_muls[unit_set][reading_options[i]]['default']
				}
			}
		}
	}
}
console.log(unit_muls)
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
function makeNewMeasurmeant(curent_id_num) {
//	console.log(curent_id_num)
	click_coords.push({})
	histo_hights.push(0)
	lines.push([])
	draws.push(null)
	maxes.push[0]
	mins.push[0]
	makeNewElement("histos","div",{"style":"text-align: center;","id":"histo"+curent_id_num},null);
	makeNewElement("measurements","div",{"style":"text-align: center;","id":"measurement"+curent_id_num},null);
	
//	makeNewElement("measurement"+curent_id_num,"div",{"style":"text-align: center;","id":"top_section"+curent_id_num},null);
	makeNewElement("measurement"+curent_id_num,"div",{"id":"histogram"+curent_id_num},null); //,"style":"display: inline-block;"
//	makeNewElement("top_section"+curent_id_num,"span",{"id":"close_measurement"+curent_id_num,"style":"display: inline-block;","class":"close"},"&times;");
//	close_btns.push(document.getElementById('close_measurement'+curent_id_num));
//	close_btns[curent_id_num].addEventListener("click", function () {
//		deleteMeasurementHandeler[curent_id_num]
//	});
	histograms.push(document.getElementById('histogram'+curent_id_num));
	
	AddClickHandler(curent_id_num)
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-reading_dropdown"+curent_id_num},null);
	reading_dropdowns.push(document.getElementById('gr-reading_dropdown'+curent_id_num));
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-method_dropdown"+curent_id_num},null);
	method_dropdowns.push(document.getElementById('gr-method_dropdown'+curent_id_num));
	
	LoadReadingDropdown(curent_id_num);
	
	makeNewElement("measurement"+curent_id_num,"button",{"id":"invert_buttion"+curent_id_num,"style":"font-size: 12px; height: 19px; background-color: #fff; border-width: thin; border-radius: 2px;"},"invert");
	invert_btns.push(document.getElementById('invert_buttion'+curent_id_num));
	invert_btns[curent_id_num].addEventListener("click", function() {
		invertHandeler(curent_id_num,true)
	});

	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+curent_id_num},null);
	makeNewElement("weight_slider_holder"+curent_id_num,"div",{"class":"weight_slider","id":"weight_slider"+curent_id_num},null);
	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+curent_id_num},null);
	makeNewElement("weight_stext_div"+curent_id_num,"div",{"class":"weight_setex","id":"weight_stext"+curent_id_num},null);
	
	weight_setexes.push(document.getElementById( 'weight_stext'+curent_id_num ));
	prevs.push(0.5)
	// create the range slider
	weight_sliders.push(document.getElementById('weight_slider'+curent_id_num));
	weight_vals.push(0)
	noUiSlider.create( weight_sliders[curent_id_num], {
	    start: [50],
	    connect: false,
	    range: {
	        'min': 1,
	        'max': 100
	    },     
	});
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
	method_dropdowns[curent_id_num].onchange =
		function () {
			if (!is_active) {
				return
			}
    		LoadWXGrid();
			click_coords[curent_id_num] = {}
			click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
			click_coords[curent_id_num][maxes[curent_id_num]*2+17] = histo_hights[curent_id_num]
			if (select != null && select[1] == measurement_index){
				select = null
				if (select_draw != null){
					select_draw.remove()
				}
				select_draw = null
			}
			DrawLines(curent_id_num)
			RenderGrid()
			updateStates()
		};
	reading_dropdowns[curent_id_num].onchange =
		function () {
			if (!is_active) {
				return
			}
			LoadMethodDropdown(curent_id_num);
		};
	reset_sliders(curent_id_num)
	click_coords[curent_id_num] = {}
	click_coords[curent_id_num][mins[curent_id_num]*2+13] = 0
	click_coords[curent_id_num][maxes[curent_id_num]*2+17] = histo_hights[curent_id_num]
	DrawLines(curent_id_num)
//	for (i = 0; i <= curent_id_num; i++){
//		DrawLines(i)
//	}
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
}


var measurement_button = document.getElementById('measurement_button');
measurement_button.addEventListener("click", newMeasurementHandeler);

var delete_measurement_button = document.getElementById('delete_measurement_button');
delete_measurement_button.addEventListener("click", deleteMeasurementHandeler);

var invert_all_button = document.getElementById('invert_all_button');
invert_all_button.addEventListener("click", function () {
	for (var i = 0; i <= measurement_index; i++) {
		invertHandeler(i,false)
	}
	RenderGrid()
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


function newMeasurementHandeler() {
	if ( measurement_index >= 4 || !is_active ){
		return;
	}
	measurement_index ++
	makeNewMeasurmeant(measurement_index)
}
function deleteMeasurementHandeler() {
	if (measurement_index > 0 || !is_active) {
		deleteMeasurement()
		DrawLines(measurement_index)
		LoadWXGrid()
		reset_sliders(measurement_index)
	}
	
}

function deleteMeasurement() {
	if (select != null && select[1] == measurement_index){
		select = null
		if (select_draw != null){
			select_draw.remove()
		}
		select_draw = null
	}
	var measurement = document.getElementById("measurement"+measurement_index)
	var histo = document.getElementById("histo"+measurement_index)
	reading_dropdowns.splice(-1)
	method_dropdowns.splice(-1)
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
	invert_btns.splice(-1)
	histo_data.splice(-1)
	measurement.remove()
	histo.remove()
	measurement_index --
	updateStates()
}

function reset_sliders(num){
	if (!is_active){
		return
	}
	is_setting = true
	for (var i = 0; i < num+1; i++){
		reset_slider(i,num)
	}
	is_setting = false
	RenderGrid()
}

function reset_slider(i,num){
	prevs[i] = 100/(num+1)
	document.getElementById("weight_slider_holder"+i).remove()
	document.getElementById("weight_stext_div"+i).remove()
	makeNewElement("measurement"+i,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+i});
	makeNewElement("weight_slider_holder"+i,"div",{"class":"weight_slider","id":"weight_slider"+i});
	makeNewElement("measurement"+i,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+i});
	makeNewElement("weight_stext_div"+i,"div",{"class":"weight_setex","id":"weight_stext"+i});
	
	weight_setexes[i] = document.getElementById( 'weight_stext'+i);
	weight_sliders[i] = document.getElementById('weight_slider'+i);
	noUiSlider.create( weight_sliders[i], {
	    start: [100/(num+1)],
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
		});
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
		RenderGrid()
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
		console.log(set_num)
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
			});
	}
	is_setting = false
}

function LoadReadingDropdown(num) {
    // get list of reading types
    reading_dropdowns[num].options.length = 0;
	reading_options = Object.keys(all_data)                 
    let option;
    for (var d = 0; d < reading_options.length; d++) {
        option = document.createElement('option');
        option.text = reading_options[d].split('_').join(' ');
        option.value = reading_options[d];
        reading_dropdowns[num].add(option);
    }
    reading_dropdowns[num].selectedIndex = 0;
	reading_types = [];
	for (dropdown of reading_dropdowns) {
		reading_types.push(dropdown.value);
	}
	has_reading = true
	LoadMethodDropdown(num)
}

function LoadMethodDropdown(num) {
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
    method_dropdowns[num].selectedIndex = 0;
	method_types = [];
	for (dropdown of method_dropdowns) {
		method_types.push(dropdown.value);
	}
	LoadWXGrid();
	click_coords[num] = {}
	click_coords[num][mins[num]*2+13] = 0
	click_coords[num][maxes[num]*2+17] = histo_hights[num]
	if (select != null && select[1] == num){
		select = null
		if (select_draw != null){
			select_draw.remove()
		}
		select_draw = null
	}
	DrawLines(num)
	RenderGrid()
	updateStates()
	
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
var wx_slider = document.getElementById('gr_slider');
noUiSlider.create( wx_slider, {
    start: [33, 66],
    connect: false,
    range: {
        'min': 0,
        'max': 100
    },     
});

// When the slider value changes, update the wx grid
wx_slider.noUiSlider.on('update', function (values, handle) {
    wx_range_val0 = values[0] / 100;
    wx_range_val1 = values[1] / 100;
    // update text and redraw wx grid
    wx_stext_val0.textContent = wx_range_val0.toFixed(2);
    wx_stext_val1.textContent = wx_range_val1.toFixed(2);
    RenderGrid();
});


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
//	console.log(reading_types);
	RenderGrid();
    // AJAX the JSON
    
}

function daysIntoYear( date ){
    return (Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) - Date.UTC(date.getFullYear(), 0, 0)) / 24 / 60 / 60 / 1000;
}

function month_to_week( nmonth ) {
    let day_of_year = daysIntoYear( new Date(2020, nmonth, 1) );
    let week = day_of_year * 52.0 / 365.0;
    return week;
}
function DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,colors,do_text){
	if (do_text){
		for (var j = 2; j < histo_plot.length-2; j++){
			if (histo_plot[j] >= 2){
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
					console.log(method_types[num])
			        let mode = draw.text( `${parseFloat(((((j*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',8).font('family','Arial');
					let mode_length = mode.length();
			        mode.move( j*2 - mode_length/2 + 15,125*0.5+1 ); // center vertically
				}
			}
		}
	    let min_extrem = draw.text( `${parseFloat(((((min_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',8).font('family','Arial');
		let min_extrem_length = min_extrem.length();
	    min_extrem.move( min_num*2 - min_extrem_length/2 + 15,125*0.5+1 ); // center vertically

	    let max_extrem = draw.text( `${parseFloat(((((max_num*2*compresion[reading_types[num]][method_types[num]]["scale"])**expon+compresion[reading_types[num]][method_types[num]]["min"])*unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][0]+unit_muls[unit_sets[unit_num]][reading_types[num]][method_types[num]][1])*mul).toFixed(2))}`+unit_names[unit_sets[unit_num]][reading_types[num]][method_types[num]] ).font('size',8).font('family','Arial');
		let max_extrem_length = max_extrem.length();
	    max_extrem.move( max_num*2 - max_extrem_length/2 + 15,125*0.5+1 ); // center vertically
	}
	var max_value = Math.max(...histo_plot)
	for (var i = 0; i < 128; i++) {
	
		var fillcol = '#ffffff'
        draw.rect( 2, color_plot[2][i]*0.5*125/max_value ).move( i*2+15, (125-color_plot[2][i]*125/max_value)*0.5 ).attr({
            'fill':colors[2],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 2, color_plot[1][i]*0.5*125/max_value ).move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i])*125/max_value)*0.5 ).attr({
            'fill':colors[1],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 2, color_plot[0][i]*0.5*125/max_value ).move( i*2+15, (125-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i])*125/max_value)*0.5 ).attr({
            'fill':colors[0],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
}
function DrawHistograms(compresed_data,inc_data){
	for (num = 0; num < measurement_index+1; num ++){
		var histo_plot_st = new Array(128).fill(0);
		var color_plot_st = [new Array(128).fill(0),new Array(128).fill(0),new Array(128).fill(0)]
		color_plot_str = JSON.stringify(color_plot_st)
		var relev_data = all_data[reading_types[num]][method_types[num]]
		for (var year = 0; year < relev_data.length; year ++){
			for (var week = 0; week < 52; week ++){
				if (relev_data[year][week] != null){
					histo_plot_st[parseInt(relev_data[year][week]/2)] += 1
					if (compresed_data[year][week] < wx_range_val0*255){
						color_plot_st[0][parseInt(relev_data[year][week]/2)] += 1
					}
					else if (compresed_data[year][week] < wx_range_val1*255){
						color_plot_st[1][parseInt(relev_data[year][week]/2)] += 1
					}
					else {
						color_plot_st[2][parseInt(relev_data[year][week]/2)] += 1
					}
				}
			}
		}
		var max_num = null
		var max_collor_nums = [null,null,null]
		for (var j = 0; j < histo_plot_st.length; j++){
			for (var i = 0; i < 3; i++){
				if (color_plot_st[i][j] != 0){
					max_collor_nums[i] = j
				}
			}
			if (histo_plot_st[j] != 0){
				max_num = j
			}
		}
		var min_num = null
		var min_collor_nums = [null,null,null]
		for (var j = histo_plot_st.length-1; j >= 0; j--){
			for (var i = 0; i < 3; i++){
				if (color_plot_st[i][j] != 0){
					min_collor_nums[i] = j
				}
			}
			if (histo_plot_st[j] != 0){
				min_num = j
			}
		}
		var histo_plot = histo_plot_st
		var color_plot = color_plot_st
		document.getElementById( 'histogram'+num ).innerHTML = ""; // clear existing
		var draw = SVG().addTo('#histogram'+num).size( 285, 125*0.5+9 );
		draw.attr({
		});
		draws[num] = draw
		var mul = 1
		var expon = 1
		if (compresion[reading_types[num]][method_types[num]]["type"] == "parabolic") {
			expon = 2
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
		if (save_clicks_x.length >= 20){
			DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,['#f4f4f4','#f4f4f4','#f4f4f4'])
			var histo_plot_st = new Array(128).fill(0);
			var color_plot_st = [new Array(128).fill(0),new Array(128).fill(0),new Array(128).fill(0)]
			color_plot_str = JSON.stringify(color_plot_st)
			var relev_data = all_data[reading_types[num]][method_types[num]]
			var compressed_coords_x = []
			var compressed_coords_y = []
			for (var i = 0; i < save_clicks_x.length; i++){
				compressed_coords_x.push(getCellCoords(save_clicks_x[i],save_clicks_y[i])[0])
				compressed_coords_y.push(getCellCoords(save_clicks_x[i],save_clicks_y[i])[1])
			}
			for (var year = 0; year < relev_data.length; year ++){
				for (var week = 0; week < 52; week ++){
					if (relev_data[year][week] != null && compressed_coords_y.includes(year) && compressed_coords_x.includes(week)){
						
						histo_plot_st[parseInt(relev_data[year][week]/2)] += 1
						if (compresed_data[year][week] < wx_range_val0*255){
							color_plot_st[0][parseInt(relev_data[year][week]/2)] += 1
						}
						else if (compresed_data[year][week] < wx_range_val1*255){
							color_plot_st[1][parseInt(relev_data[year][week]/2)] += 1
						}
						else {
							color_plot_st[2][parseInt(relev_data[year][week]/2)] += 1
						}
					}
				}
			}
			var max_num_new = null
			var max_collor_nums_new = [null,null,null]
			for (var j = 0; j < histo_plot_st.length; j++){
				for (var i = 0; i < 3; i++){
					if (color_plot_st[i][j] != 0){
						max_collor_nums_new[i] = j
					}
				}
				if (histo_plot_st[j] != 0){
					max_num_new = j
				}
			}
			var min_num_new = null
			var min_collor_nums_new = [null,null,null]
			for (var j = histo_plot_st.length-1; j >= 0; j--){
				for (var i = 0; i < 3; i++){
					if (color_plot_st[i][j] != 0){
						min_collor_nums_new[i] = j
					}
				}
				if (histo_plot_st[j] != 0){
					min_num_new = j
				}
			}
			var histo_plot_new = histo_plot_st
			var color_plot_new = color_plot_st
			DrawHistogram(draw,histo_plot_new,min_num_new,max_num_new,expon,mul,color_plot_new,num,color_lists[color_num],true)
		}
		else {
			DrawHistogram(draw,histo_plot,min_num,max_num,expon,mul,color_plot,num,color_lists[color_num],true)
		}
		histo_data[num] = {'histo_plot':histo_plot,'min_num':min_num,'max_num':max_num,'expon':expon,'mul':mul,'color_plot':color_plot}
//		console.log(min_num*2+15)
//		console.log(max_num*2+15)
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
		RegisterClick(num,event)
	});
}

function RegisterClick(num,event) {
	click_x = event.offsetX
	click_y = histo_hights[num]-event.offsetY
	if (click_y < 0 || click_x < mins[num]*2+13 || click_x > maxes[num]*2+17 ||  click_y > 71){
		return
	}
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	if (select != null)	{
		if (Math.abs(click_x-select[0]) < 4 && Math.abs(click_y-click_coords[num][select[0]]) < 4) {
			select = null
			if (select_draw != null){
				select_draw.remove()
			}
			select_draw = null
			return
		}
	}
	for (val of x_vals) {
		if (Math.abs(click_x-val) < 4 && Math.abs(click_y-click_coords[num][val]) < 4) {
			if (select != null)	{
				select = null
				if (select_draw != null){
					select_draw.remove()
				}
				select_draw = null
			}
			select = [val,num]
			var draw = draws[num];
	        select_draw = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)-2 ).attr({
	            'fill':'#d55',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
			
			return
		}
	}
	if (select != null){
		select = null
		if (select_draw != null){
			select_draw.remove()
		}
		if (select[1] == num){
			click_coords[num][select[0]] = click_y
			select_draw = null
			DrawLines(num)
			RenderGrid()
		}
		return
	}
	click_coords[num][click_x] = click_y
	DrawLines(num)
	RenderGrid()
	updateStates()
}

function getCellCoords(x,y){
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;	
	return [Math.floor((x-35)/9),Math.floor(num_years-y/9)]
}

function DetectYearClick(event,is_render_call){
	if (!is_render_call && !event.shiftKey){
		save_clicks_x = []
		save_clicks_y = []
		selected_years = []
		selected_seasons = []
	}
	if (!is_render_call && !event.shiftKey){ 
		var season_cover_length = season_covers.length
		for (let i=0; i < season_cover_length; i++){
			season_covers[season_covers.length-1].remove()
			season_covers.splice(-1)
		} 
	}
	if (!is_render_call && event.offsetY < compresed_data.length/2+14){
		if (!event.shiftKey){
			var year_cover_length = year_covers.length
			for (let i=0; i < year_cover_length; i++){
				year_covers[year_covers.length-1].remove()
				year_covers.splice(-1)
			}
		}
		DetectGridClick(null,true)
		return
	}
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		selected_years.push(Math.floor((event.offsetY-14)/9))
	}
	var year_cover_length = year_covers.length
	for (let i=0; i < year_cover_length; i++){
		year_covers[year_covers.length-1].remove()
		year_covers.splice(-1)
	} 
	if (!is_render_call){
		for (let i=0; i < 52; i++){
			var is_selected = false
			for (var j=0; j < save_clicks_x.length; j++){
				if (getCellCoords(i*9+36,event.offsetY-compresed_data.length/2-14)[0] == getCellCoords(save_clicks_x[j],save_clicks_y[j])[0] && getCellCoords(i*9+36,event.offsetY-compresed_data.length/2-14)[1] == getCellCoords(save_clicks_x[j],save_clicks_y[j])[1]){
					is_selected = true
					break
				}
			}
			if (!is_selected){
				save_clicks_x.push(i*9+36)
				save_clicks_y.push(event.offsetY-compresed_data.length/2-14)
			}
		}
	}
	for (let i=4; i < num_years+4; i++){
		if (!(selected_years.includes(i))){
			year_covers.push(year_draw.rect( 52*3, 9 ).move( 22, (i+2)*9-4).attr({
					fill: '#fff'
				, 'fill-opacity': 0.5
						, stroke: '#ee0'
				, 'stroke-width': 0 
					}));
		}
	}
	DetectGridClick(null,true)
}

function DetectSeasonClick(event,is_render_call){
	if (!is_render_call && !event.shiftKey){
		save_clicks_x = []
		save_clicks_y = []
		selected_years = []
		selected_seasons = []
	}
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		selected_seasons.push(Math.floor((event.offsetX)/9-4))
	}
	if (!is_render_call && !event.shiftKey){ 
		var year_cover_length = year_covers.length
		for (let i=0; i < year_cover_length; i++){
			year_covers[year_covers.length-1].remove()
			year_covers.splice(-1)
		} 
	}
	var season_cover_length = season_covers.length
	for (let i=0; i < season_cover_length; i++){
		season_covers[season_covers.length-1].remove()
		season_covers.splice(-1)
	} 
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	if (!is_render_call){
		for (let i=0; i < num_years; i++){
			var is_selected = false
			for (var j=0; j < save_clicks_x.length; j++){
				if (getCellCoords(event.offsetX,i*9+1)[0] == getCellCoords(save_clicks_x[j],save_clicks_y[j])[0] && getCellCoords(event.offsetX,i*9+1)[1] == getCellCoords(save_clicks_x[j],save_clicks_y[j])[1]){
					is_selected = true
					break
				}
			}
			if (!is_selected){
				save_clicks_y.push(i*9+1)
				save_clicks_x.push(event.offsetX)
			}
		}
	}
	for (let i=0; i < 52; i++){
		if (!(selected_seasons.includes(i))){
			season_covers.push(season_draw.rect( 9, num_years*0.5 ).move( i*9+35, 0).attr({
					fill: '#fff'
				, 'fill-opacity': 0.5
						, stroke: '#ee0'
				, 'stroke-width': 0 
					}));
		}
	}
	DetectGridClick(null,true)
}

function DetectGridClick(event,is_render_call){
	num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;	
	document.getElementById( "tables" ).innerHTML = "";
	document.getElementById( "heder" ).innerHTML = "";
	if (!is_render_call){
		click_x = event.offsetX
		click_y = event.offsetY
		if (event.shiftKey) {
			num = Math.max(save_clicks_x.length)
			var is_selected_cell = false;
			for (var i=0; i < num; i++){
				if (getCellCoords(click_x,click_y)[0] == getCellCoords(save_clicks_x[i],save_clicks_y[i])[0] && getCellCoords(click_x,click_y)[1] == getCellCoords(save_clicks_x[i],save_clicks_y[i])[1]){
					is_selected_cell = true
					break
				}
			}
			if (is_selected_cell){
//				console.log(save_clicks_x)
				save_clicks_x.splice(i,1)
//				console.log(save_clicks_x)
				save_clicks_y.splice(i,1)
				if (num == 1){
					save_clicks_x = [0]
					save_clicks_y = [num_years]
				}
			}
			else {
				save_clicks_x[num] = click_x
				save_clicks_y[num] = click_y
			}
		}
		else {
			save_clicks_x = [click_x]
			save_clicks_y = [click_y]
			selected_years = []
			selected_seasons = []
			var year_cover_length = year_covers.length
			for (let i=0; i < year_cover_length; i++){
				year_covers[year_covers.length-1].remove()
				year_covers.splice(-1)
			} 
			var season_cover_length = season_covers.length
			for (let i=0; i < season_cover_length; i++){
				season_covers[season_covers.length-1].remove()
				season_covers.splice(-1)
			}
		}
	}
//	console.log(outlines)
	var outline_length = outlines.length
	for (var i=0; i < outline_length; i++){
		outlines[outlines.length-1].remove()
		outlines.splice(-1)
	} 
//	console.log(covers)
	var cover_length = covers.length
	for (var i=0; i < cover_length; i++){
		covers[covers.length-1].remove()
		covers.splice(-1)
	}
	if (fade != null){
		fade.remove()
	}
	for (highlight of highlights) {
		var highlight_length = highlight.length
		for (var i=0; i < highlight_length; i++){
			highlight[highlight.length-1].remove()
			highlight.splice(-1)
		}
	}
	fade = null

	var can_fade = false
	var num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	for (var i=0; i < save_clicks_x.length; i++){
		var coords = getCellCoords(save_clicks_x[i],save_clicks_y[i])
		if (Math.min(...coords) > 0 && wx_grdata[reading_types[0]][method_types[0]][coords[1]][coords[0]] != null){
			can_fade = true
		}
	}
	if (can_fade) {
		fade = grid_draw.rect( 52*9, num_years*9 ).move( 35, 1).attr({
					fill: '#fff'
			, 'fill-opacity': 0.5
					, stroke: '#ee0'
			, 'stroke-width': 0 
				});
	}
	DrawHistograms(compresed_data)
	for (var i=0; i<save_clicks_x.length; i++){
		RegisterGridClick(null,save_clicks_x[i],save_clicks_y[i],null)
	}
	if (can_fade){
		var txt = ""
		for (var i=0; i < reading_options.length; i++){
			method_options = Object.keys(all_data[reading_options[i]]) 
			makeNewElement("tables","table",{"id":"table"+(i+1),"style":"display: inline-block; text-align: center; margin-left: 10px float: top;" },null);
			makeNewElement("table"+(i+1),"tr",{"id":"measurementy"+(i+1)},null);
			makeNewElement("measurementy"+(i+1),"th",{"id":"th"+(i+1)},reading_options[i].split('_').join(' '));
			for (var j=0; j < method_options.length; j++){
	//			console.log(all_data[reading_options[i]])
	//			console.log(method_options[j])
				relev_data = all_data[reading_options[i]][method_options[j]]
				var mul = 1
				var expon = 1
				if (compresion[reading_options[i]][method_options[j]]["type"] == "parabolic") {
					expon = 2
				}
				var compressed_value = null
				var value_list = []
				for (var num=0; num < save_clicks_x.length; num++){
					var coords = getCellCoords(save_clicks_x[num],save_clicks_y[num])
					if (Math.min(...coords) > 0 && wx_grdata[reading_types[0]][method_types[0]][coords[1]][coords[0]] != null){
						value_list.push(((all_data[reading_options[i]][method_options[j]][Math.floor(num_years-save_clicks_y[num]/9)][Math.floor((save_clicks_x[num]-35)/9)]*compresion[reading_options[i]][method_options[j]]["scale"])**expon+compresion[reading_options[i]][method_options[j]]["min"])*unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][0]+unit_muls[unit_sets[unit_num]][reading_options[i]][method_options[j]][1]);
					}
				}
				if ([method_options[j]] == 'min'){
					compressed_value = Math.min(...value_list)
				}
				else if ([method_options[j]] == 'max'){
					compressed_value = Math.max(...value_list)
				}
				else {
					compressed_value = value_list.reduce((a, b) => a + b, 0)/value_list.length
				}
				makeNewElement("table"+(i+1),"tr",{"id":"methody"+(i+1)+','+j},null);
				makeNewElement("methody"+(i+1)+','+j,"td",{"id":"td"+(i+1)+','+j},short_names[reading_options[i]][method_options[j]]+': '+ parseFloat(compressed_value).toFixed(2)+unit_names[unit_sets[unit_num]][reading_options[i]][method_options[j]]);
			}
		}
	}
}
function RegisterGridClick(event,click_x,click_y,num) {
	var num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	var coords = getCellCoords(click_x,click_y)
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
	outlines.push(grid_draw.rect( 9, 8 ).move( Math.floor((click_x)/9)*9-1, Math.floor((click_y)/9)*9+2).attr({
			fill: fillcol
		, 'fill-opacity': 1
			, stroke: '#ee0'
		, 'stroke-width': 0 
        }));
	covers.push(grid_draw.rect( 9, 8 ).move( Math.floor(click_x/9)*9-1, Math.floor(click_y/9)*9+2).attr({
			fill: fillcol
		, 'fill-opacity': 0
			, stroke: '#000'
		, 'stroke-width': 1 
        }));
	if (save_clicks_x.length < 20){
		for (var num = 0; num < measurement_index+1; num ++){
			var max_value = Math.max(...histo_data[num]['histo_plot'])
			var data = wx_grdata[reading_types[num]][method_types[num]][coords[1]][coords[0]]
			histo_index = parseInt(data/2)
			draw = draws[num]
			if (highlights[num] == null){
				highlights[num] = []
			}
	        highlights[num].push(draw.rect( 2, histo_data[num]['histo_plot'][histo_index]*0.5*125/max_value ).move( histo_index*2+15,(125-histo_data[num]['histo_plot'][histo_index]*125/max_value)*0.5).attr({
	            'fill':'#eeee00',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0
	        }));
		}
	}
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
	var year = coords[1]+parseInt(start_year) 
	txt = (display_day+1)+'/'+(month+1)+'/'+year
	if (unit_sets[unit_num] == "american"){
		txt = (month+1)+'/'+(display_day+1)+'/'+year
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
	txt2 = (display_day+1)+'/'+(month+1)+'/'+year
	if (unit_sets[unit_num] == "american"){
		txt2 = (month+1)+'/'+(display_day+1)+'/'+year
	}
	document.getElementById( "heder" ).innerHTML = "details frome the week "+txt+"-"+txt2;
//	document.getElementById( 'txt' ).innerHTML = txt;
	
}
	
function HandleDelete() {
	if (select == null){
		return
	}
	num = select[1]
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	click_dict = click_coords[num]
	select_draw.remove()
	select_draw = null
	if (select[0] == x_vals[0]){
		click_coords[num][x_vals[0]] = click_coords[num][x_vals[1]]
		DrawLines(num)
		select = null
		RenderGrid()
		return
	}
	else if (select[0] == x_vals[x_vals.length-1]){
		click_coords[num][x_vals[x_vals.length-1]] = click_coords[num][x_vals[x_vals.length-2]]
		DrawLines(num)
		select = null
		RenderGrid()
		return
	}
	delete click_dict[select[0]]
	select = null
	DrawLines(num)
	RenderGrid()
	updateStates()
}

function arrowHandler(y_dif) {
	if (select == null){
		return
	}
	var shift_mul = 1
	if (event.shiftKey){
		shift_mul = 10
	}
	num = select[1]
	val = select[0]
	click_dict = click_coords[num]
	click_dict[select[0]] += y_dif*shift_mul
	if (click_dict[select[0]] > histo_hights[num]){
		click_dict[select[0]] = histo_hights[num]
	}
	if (click_dict[select[0]] < 0){
		click_dict[select[0]] = 0
	}
	select_draw.remove()
	select_draw = null
	var draw = draws[num];
    select_draw = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)-2 ).attr({
        'fill':'#d55',
        'shape-rendering':'crispEdges',
        'stroke-width': 0 
    });
	DrawLines(num)
	RenderGrid()
	updateStates()
}

function horizontalArrowHandler(x_dif) {
	if (select == null){
		return
	}
	var shift_mul = 1
	if (event.shiftKey){
		shift_mul = 10
	}
	var num = select[1]
	var val = select[0]
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	var x_index = x_vals.indexOf(val)
	console.log("x_index: " + x_index)
	var new_x = parseInt(val)+x_dif*shift_mul
	console.log(new_x)
	console.log(x_vals[x_index-1])
	console.log(x_vals[x_index+1])
	if (new_x <= x_vals[x_index-1]){
		new_x = parseInt(x_vals[x_index-1]) + 1
	}
	else if (new_x < parseInt(x_vals[0])){
		console.log(new_x)
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
	click_dict[new_x] = y_val
	console.log(select)
	select = [new_x.toString(),num]
	console.log(select)
	select_draw.remove()
	select_draw = null
	var draw = draws[num];
    select_draw = draw.rect( 4, 4 ).move( val-2, (click_coords[num][val]-histo_hights[num])*(-1)-2 ).attr({
        'fill':'#d55',
        'shape-rendering':'crispEdges',
        'stroke-width': 0 
    });
	DrawLines(num)
	RenderGrid()
	updateStates()
}

function DrawLines(num) {
	for (line of lines[num]) {
		line.remove()
	}
	lines[num] = []
	var draw = draws[num];
	var x_vals = Object.keys(click_coords[num]).sort((a,b) => a - b); //sort the keys
	console.log(x_vals)
	for (var b = 0; b < x_vals.length-1; b ++) {
		lines[num].push(draw.line(0, histo_hights[num], x_vals[b+1]-x_vals[b], (click_coords[num][x_vals[b+1]]-click_coords[num][x_vals[b]]-histo_hights[num])*(-1))
		.move(x_vals[b], (Math.max(click_coords[num][x_vals[b+1]],click_coords[num][x_vals[b]])-histo_hights[num])*(-1)).stroke({ color: '#000', width: 1, linecap: 'round' }))
		lines[num].push(draw.circle(3).move(parseInt(x_vals[b])-1.5, (click_coords[num][x_vals[b]]-histo_hights[num])*(-1)-1.5).fill('#000'))
	}
	b = x_vals.length-1
	lines[num].push(draw.circle(3).move(parseInt(x_vals[b])-1.5, (click_coords[num][x_vals[b]]-histo_hights[num])*(-1)-1.5).fill('#000'))
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

function DrawSesonalitys(compresed_data,months){
	var color_plot = [new Array(52).fill(0),new Array(52).fill(0),new Array(52).fill(0)]
	color_plot_str = JSON.stringify(color_plot)
	for (var year = 0; year < compresed_data.length; year ++){
		for (var week = 0; week < 52; week ++){
			if (compresed_data[year][week] != null){
				if (compresed_data[year][week] < wx_range_val0*255){
					color_plot[0][week] += 1
				}
				else if (compresed_data[year][week] < wx_range_val1*255){
					color_plot[1][week] += 1
				}
				else {
					color_plot[2][week] += 1
				}
			}
		}
	}
	document.getElementById( 'gr_sesonalitys').innerHTML = ""; // clear existing
	var draw = SVG().addTo('#gr_sesonalitys').size( 52*9+35, compresed_data.length*0.5 );
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	for (var i = 0; i < 52; i++) {
		
		var fillcol = '#ffffff'
        draw.rect( 9, color_plot[2][i]*0.5 ).move( i*9+35, (compresed_data.length-color_plot[2][i])*0.5 ).attr({
            'fill':color_lists[color_num][2],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 9, color_plot[1][i]*0.5 ).move( i*9+35, (compresed_data.length-(color_plot[2][i]+color_plot[1][i]))*0.5 ).attr({
            'fill':color_lists[color_num][1],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 9, color_plot[0][i]*0.5 ).move( i*9+35, (compresed_data.length-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i]))*0.5 ).attr({
            'fill':color_lists[color_num][0],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
    for ( i=0; i < months.length; i++ ) {
        let bx = month_to_week( i ) * 9 + 35;
		if (i != 0) {
	        draw.rect( 1, compresed_data.length*0.5-1 ).move( bx-1.5, 1  ).attr({
	            'fill':'#ffffff37',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
    }
	season_draw = draw
}
function DrawYears(compresed_data,num_years){
	var color_plot = [new Array(compresed_data.length).fill(0),new Array(compresed_data.length).fill(0),new Array(compresed_data.length).fill(0)]
	color_plot_str = JSON.stringify(color_plot)
	var line_years = []
	for (var year = 0; year < compresed_data.length; year ++){
        syear = num_years + start_year - year;    
        if ( !((syear-1)%5) ) {
			var opacity = "37"
			if (!((syear-1)%10)){
				var opacity = "bb" 
			}
			line_years.push([opacity,year])
		}
		for (var week = 0; week < 52; week ++){
			if (compresed_data[year][week] != null){
				if (compresed_data[year][week] < wx_range_val0*255){
					color_plot[0][year] += 1
				}
				else if (compresed_data[year][week] < wx_range_val1*255){
					color_plot[1][year] += 1
				}
				else {
					color_plot[2][year] += 1
				}
			}
		}
	}
	document.getElementById( 'gr_years').innerHTML = ""; // clear existing
	var draw = SVG().addTo('#gr_years').size( 52*3 + 22, (compresed_data.length+1)*9.5+10 );
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	console.log(compresed_data.length)
	for (var i = 0; i < compresed_data.length; i++) {
		
        draw.rect( color_plot[2][i]*3, 9 ).move( 22, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
            'fill':color_lists[color_num][2],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( color_plot[1][i]*3, 9 ).move( color_plot[2][i]*3 + 22, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
            'fill':color_lists[color_num][1],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( color_plot[0][i]*3, 9 ).move( (color_plot[2][i]+color_plot[1][i])*3 + 22, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
            'fill':color_lists[color_num][0],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
		if ((i < PDO.length) && (PDO[i] > 0.75)) {
	        draw.circle( 8 ).move( 0, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][2],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
		else if ((i < PDO.length) && (PDO[i] > -0.75)) {
	        draw.circle( 8 ).move( 0, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][1],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
		else if (i < PDO.length) {
	        draw.circle( 8 ).move( 0, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][0],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
		if ((i < ENSO.length) && (ENSO[i] > 0.75)) {
	        draw.circle( 8 ).move( 11, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][2],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
		else if ((i < ENSO.length) && (ENSO[i] > -0.75)) {
	        draw.circle( 8 ).move( 11, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][1],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
		else if (i < ENSO.length) {
	        draw.circle( 8 ).move( 11, (compresed_data.length-i)*9 + compresed_data.length/2+5).attr({
	            'fill':color_lists[2][0],
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
	}
	for (var i = 0; i < 4; i++) {
        draw.rect( 2, (compresed_data.length+1)*9.5+10 ).move( i*31+53, 0  ).attr({
            'fill':'#ffffff66',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
	for (year of line_years) {
        draw.rect( 52*3 +22, 1 ).move( 0, year[1]*9+9 + compresed_data.length/2+5).attr({
            'fill':'#ffffff'+year[0],
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
	var PDOoffset = compresed_data.length-PDO.length
	var ENSOoffset = compresed_data.length-ENSO.length
    let btextPDO = draw.text( `- PDO` ).font('size',10).font('family','Arial');
    let bwPDO = btextPDO.length();   
	let bhPDO = btextPDO.bbox().height; // bbox is double for some reason.     
    btextPDO.center(4.5,compresed_data.length/2+9*PDOoffset-2).rotate(270);
	
    let btextENSO = draw.text( `- ENSO` ).font('size',10).font('family','Arial');
    let bwENSO = btextENSO.length();   
	let bhENSO = btextENSO.bbox().height; // bbox is double for some reason.     
    btextENSO.center(15.5 ,compresed_data.length/2+9*ENSOoffset-5.5).rotate(270);
	year_draw = draw
//	year_histogram = color_plot
}
function updateStates(){
	state_dict = {
		'mins':mins.slice(),
		'maxes':maxes.slice(),
		'compresed_data':compresed_data.slice(),
		'is_valid':is_valid,
		'wx_grdata_min':wx_grdata_min,
		'wx_grdata_max':wx_grdata_max,
		'wx_range_val0':wx_range_val0,
		'wx_range_val1':wx_range_val1,
		'weight_val':weight_val,
		'weight_val2':weight_val2,
		'click_coords':click_coords.slice(),
		'weight_vals':weight_vals.slice(),
		'close_btns':close_btns,
		'measurement_index':measurement_index,
		'reading_types':reading_types.slice(),
		'method_types':method_types.slice(),
		'prevs':prevs.slice()
	}
	if (state_index != null){
		states = states.slice(0,state_index+1)
	}
	state_index ++
	states.push(state_dict)
	console.log(states)
}
// Renders SVG weather grid/heatmap thing
function RenderGrid(){
    if ( wx_grdata == null )
        return;

	if (!has_reading)
		return;
    var year_label_width = 35;
    var month_label_height = 25;
    var off_x = year_label_width;         // grid offset
    var off_y = 1;
    var boxsize = 9;        // size of a grid unit
    var boxspace = 9;      // total space from unit to unit

    var num_weeks = 52;	
	var wx_data = [];
    num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
	var grids = [];
//	console.log('rend')
//	console.log(reading_types)
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
				x_vals = Object.keys(click_coords[k]).sort((a,b) => a - b);
				for ( var j = 0; j < x_vals.length; j++ ){
					if (x_vals[j]-15 > grids[k][n][m]) {
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
//				console.log(((grids[k][n][m]+15-relev_coords[0])*mul+ofset)*weight_valys[k])
				num += ((grids[k][n][m]+15-relev_coords[0])*mul+ofset)*weight_vals[k];
			}
			if (num == null){
				wx_data[n].push(null)
			}
			else {
				wx_data[n].push(num/total_weight);
			}
		}
	}
	compresed_data = wx_data
	DrawHistograms(wx_data)
    // var color0 = '#edf8b1';
    // var color1 = '#7fcdbb';
    // var color2 = '#2c7fb8';
    var color0 = color_lists[color_num][0];
    var color1 = color_lists[color_num][1];
    var color2 = color_lists[color_num][2];

    // create the svg drawing object and draw the grid elements    
    var total_width = boxspace * num_weeks + year_label_width;
    var total_height = boxspace * num_years + off_y + month_label_height;

    document.getElementById( 'gr_grid' ).innerHTML = ""; // clear existing
    var draw = SVG().addTo('#gr_grid').size( total_width, total_height);
    draw.attr({
        'shape-rendering':'crispEdges'
    });
	grid_draw = draw
    for ( k=0; k<num_years; k++ )
    {
        sy = k * boxspace + off_y;
        // draw year label every 3 rows, vertically centered on the row, to the left of the grid
        syear = num_years + start_year - k;  
		var opacity = "bb"      
        if ( !((syear-1)%5) ) {
			if (!((syear-1)%10)){
				opacity = "ff" 
			}
            var stext = draw.text( `${syear-1}` ).font('size',12).font('family','Arial');
            syear_width = stext.length()+6;
            syear_height = stext.bbox().height/2; // bbox is double for some reason.
            stext.move( off_x - syear_width, sy - (syear_height/2) );
        }

        for ( p=0; p<num_weeks; p++ )
        {
            // var fillcol = color0;
            // if ( Math.floor(Math.random() * 6)==0 )
            //     fillcol = color1;
            // else if ( Math.floor(Math.random() * 9)==0 )
            //     fillcol = color2;

            // get measurement, years are reversed order, & calculate fill color
            var fillcol = 0;
	        let shape_rend = 'crispEdges';	// render the contigous blocks with crispedges
            var bsize = boxsize
            var mx = wx_data[num_years-1-k][p];
            if ( mx == null )
                fillcol = '#FFFFFF';    // nulls are this color
            else
            {
                mx = Number.parseFloat( mx );
                mx = mx / 255; // normalize mx 0..1
                if ( mx < wx_range_val0 ){
                    fillcol = color0;
		            shape_rend = 'auto';		// draw the blue grid blocks with AntiAliasing
		        }
                else if ( mx < wx_range_val1 ){
                    fillcol = color1;
                    bsize = boxspace;   // bigger square
                }
                else {
                    fillcol = color2;
                    bsize = boxspace;   // bigger square
                }
            }

            // draw rect
            sx = p * boxspace + off_x;
            var rect = draw.rect( bsize, bsize ).move( sx, sy ).attr({
                'fill':fillcol,
                'shape-rendering':shape_rend,
                'stroke-width': 0 
            });
//			rect.addEventListener('click', function () {
//				console.log("txt")
//				var gr_sesonalitys = document.getElementById('gr_sesonalitys')
//				gr_sesonalitys.title = "txt"				
//			});
        }
		
        draw.rect( (num_weeks) * boxspace, 1 ).move( off_x, sy ).attr({
            'fill':'#ffffff'+opacity,
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
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
	        draw.rect( 1, num_years*9-1 ).move( bx-1.5, 1  ).attr({
	            'fill':'#ffffff37',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
    }
	DrawSesonalitys(wx_data,months)
	DrawYears(wx_data,num_years)
	DetectGridClick(null,true)
	if (selected_years.length){
		DetectYearClick(null,true)
	}
	console.log(selected_seasons)
	if (selected_seasons.length){
		DetectSeasonClick(null,true)
	}
};
//file:///Users/katmai/Downloads/test.json
//file:///Users/katmai/Downloads/test.json 