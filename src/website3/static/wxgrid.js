/// HWITW project Copyright (C) 2021
// initialize as an array LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value)of zeros. an empty grid.
var wx_grdata = {"":Array(60).fill().map(() => Array(52).fill(0))}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid
var wx_grdata_min = 0.0;
var wx_grdata_max = 1.0;
var wx_range_val0 = 0.33;
var wx_range_val1 = 0.66;
var weight_val = 0.01
var weight_val2 = 0.01
var reading_dropdowns = []
var direction_dropdowns = []
var method_dropdowns = []
var weight_sliders = []
var histograms = []
var weight_setexes = []
var weight_vals = []
var measurement_index = 0
let cred_str = 'weird:weather'  // TODO: remove. handy for devel
var wxapp_folder = '/wxapp/'    // base folder/url of python app stuff
var reading_types = []
var method_types = []
var has_reading = false
var all_data = []
var prevs = []
var start_year = 0
const input_dict = {"temperature":[-60,131.25,0.75],"ceiling":[0,6375,25], "precipitation":[0,.00255,.00001], "cloud cover":[0,1,0.005]};
var is_setting = false
var wxgrid_url = `http://localhost:5000/wxapp/getwxvar`;
fetch( wxgrid_url, {   method:'GET',
                        headers: {'Authorization': 'Basic ' + btoa(cred_str)}
                    }
)
.then(
    function( response ) {
        if ( response.status !== 200 ) {
            console.warn('Problemo with fetch wxgrid. Status Code: ' + response.status );
            return;
        }

        response.json().then(
            function(data) {
                // parse JSON and determine some stuff
                all_data = data;//JSON.parse( data.response );
				start_year = all_data["data_specs"]["start_year"];
				all_data = all_data["data"];
				for (mesurment of Object.keys(all_data)){
					for (func of Object.keys(all_data[mesurment])){
						for ( var i = 0; i < all_data[mesurment][func].length; i++ ){
							for ( var j = 0; j < all_data[mesurment][func][i].length; j++ ){
								all_data[mesurment][func][i][j] = compress(all_data[mesurment][func][i][j],input_dict[mesurment])
							}
						}
					}
				}
				makeNewMeasurmeant(0)
            }
        );
    }
)
.catch(function(err) {
    console.error('Fetch Error -', err);
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

function makeNewElement(id, type, atributes) {
	var theDiv = document.getElementById(id);
	var content = document.createElement(type);
	var atibutes_to_set = Object.keys(atributes);
	for (atibute_to_set of atibutes_to_set) {
		content.setAttribute(atibute_to_set, atributes[atibute_to_set]);
	}
	theDiv.appendChild(content);
}
function makeNewMeasurmeant(curent_id_num) {
//	console.log(curent_id_num)
	makeNewElement("measurements","div",{"style":"text-align: center;","id":"measurement"+curent_id_num});
	
	makeNewElement("measurement"+curent_id_num,"div",{"id":"histogram"+curent_id_num});
	histograms.push(document.getElementById('histogram'+curent_id_num));
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-reading_dropdown"+curent_id_num});
	reading_dropdowns.push(document.getElementById('gr-reading_dropdown'+curent_id_num));
	
	makeNewElement("measurement"+curent_id_num,"select",{"id":"gr-method_dropdown"+curent_id_num});
	method_dropdowns.push(document.getElementById('gr-method_dropdown'+curent_id_num));
	
	makeNewElement("measurement"+curent_id_num,"select",{"style":"","id":"gr-direction_dropdown"+curent_id_num});
	direction_dropdowns.push(document.getElementById('gr-direction_dropdown'+curent_id_num));
	
	LoadDirectionDropdown(curent_id_num);
	
	LoadReadingDropdown(curent_id_num);

	
	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+curent_id_num});
	makeNewElement("weight_slider_holder"+curent_id_num,"div",{"class":"weight_slider","id":"weight_slider"+curent_id_num});
	makeNewElement("measurement"+curent_id_num,"div",{"style":"padding-bottom: 10px;","id":"weight_stext_div"+curent_id_num});
	makeNewElement("weight_stext_div"+curent_id_num,"div",{"class":"weight_setex","id":"weight_stext"+curent_id_num});
	
	weight_setexes.push(document.getElementById( 'weight_stext'+curent_id_num ));
	prevs.push(0.5)
	// create the range slider
	weight_sliders.push(document.getElementById('weight_slider'+curent_id_num));
	weight_vals.push(0)
	noUiSlider.create( weight_sliders[curent_id_num], {
	    start: [50],
	    connect: false,
	    range: {
	        'min': 0,
	        'max': 100
	    },     
	});
	direction_dropdowns[curent_id_num].onchange =
    	function () {
        	RenderGrid();
    	};
	weight_sliders[curent_id_num].noUiSlider.on('update', function (values, handle) {
	    var weight_val = values[0] / 100;
	    // update text and redraw wx grid
		weight_vals[curent_id_num] = parseFloat(weight_val)
	    weight_setexes[curent_id_num].textContent = weight_val.toFixed(2);
		handleSlider(curent_id_num)
		});
	method_dropdowns[curent_id_num].onchange =
		function () {
    		LoadWXGrid();
		};
	reading_dropdowns[curent_id_num].onchange =
		function () {
			LoadMethodDropdown(curent_id_num);
		};
	reset_sliders(curent_id_num)
}
// make wx_grdata an array of zeros
function ClearWXGridData() {
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

function newMeasurementHandeler() {
	if ( measurement_index == 4 ){
		return;
	}
	measurement_index ++
	makeNewMeasurmeant(measurement_index)
}
function deleteMeasurementHandeler() {
	if (measurement_index > 0) {
		var measurement = document.getElementById("measurement"+measurement_index)
		reading_dropdowns.splice(-1)
		direction_dropdowns.splice(-1)
		method_dropdowns.splice(-1)
		weight_sliders.splice(-1)
		weight_setexes.splice(-1)
		weight_vals.splice(-1)
		prevs.splice(-1)
		measurement.remove()
		measurement_index --
		LoadWXGrid()
		reset_sliders(measurement_index)
	}
	
}

function reset_sliders(num){
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
	    weight_setexes[i].textContent = weight_val.toFixed(2);
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
			redoSlider(i,num,total_weght)
		}
		RenderGrid()
		is_setting = false
	}
	prevs[num] = weight_val
}
function redoSlider(i,num,total_weght) {
	if (i != num) {
		console.log(total_weght)
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
		console.log('r')
		console.log(weight_vals[num])
		noUiSlider.create( weight_sliders[i], {
		    start: [(i_setex+wegth_i*(prevs[num]-weight_vals[num]))*100],
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
		    weight_setexes[i].textContent = weight_val.toFixed(2);
			handleSlider(i,weight_val)
			});
	}
}

function LoadReadingDropdown(num) {
    // get list of reading types
    reading_dropdowns[num].options.length = 0;
	reading_options = Object.keys(all_data)                 
    let option;
    for (let i = 0; i < reading_options.length; i++) {
        option = document.createElement('option');
        option.text = reading_options[i].split('_').join(' ');
        option.value = reading_options[i];
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
	console.log(reading_types)                
    let option;
    for (let i = 0; i < method_options.length; i++) {
        option = document.createElement('option');
        option.text = method_options[i].split('_').join(' ');
        option.value = method_options[i];
        method_dropdowns[num].add(option);
    }
    method_dropdowns[num].selectedIndex = 0;
	method_types = [];
	for (dropdown of method_dropdowns) {
		method_types.push(dropdown.value);
	}
	LoadWXGrid();
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
//    diffDivs[0].innerHTML = values[1] - values[0];
  //  diffDivs[1].innerHTML = values[2] - values[1];
    //diffDivs[2].innerHTML = values[3] - values[2];
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
	for ( var i = 0; i < reading_types.length; i++ ){
		wx_grdata[reading_types[i]][method_types[i]] = all_data[reading_types[i]][method_types[i]];		
	};
//	console.log(reading_types);
	RenderGrid();
    // AJAX the JSON
    
}

function DrawHistogram(compresed_data,data_min,data_range){
	for (num = 0; num < measurement_index+1; num ++){
		var histo_plot_st = new Array(128).fill(0);
		console.log('l')
		var color_plot_st = [new Array(128).fill(0),new Array(128).fill(0),new Array(128).fill(0)]
		color_plot_str = JSON.stringify(color_plot_st)
		var relev_data = all_data[reading_types[num]][method_types[num]]
		for (var year = 0; year < relev_data.length; year ++){
			for (var week = 0; week < 52; week ++){
				if (relev_data[year][week] != null){
					histo_plot_st[parseInt(relev_data[year][week]/2)] += 0.5
					if (compresed_data[year][week] < wx_range_val0*data_range+data_min){
						color_plot_st[0][parseInt(relev_data[year][week]/2)] += 0.5
					}
					else if (compresed_data[year][week] < wx_range_val1*data_range+data_min){
						color_plot_st[1][parseInt(relev_data[year][week]/2)] += 0.5
					}
					else {
						color_plot_st[2][parseInt(relev_data[year][week]/2)] += 0.5
					}
				}
			}
		}
		var min_num = null
		var min_collor_nums = [null,null,null]
		for (var j = 0; j < histo_plot_st.length; j++){
			for (var i = 0; i < 3; i++){
				if (color_plot_st[i][j] != 0 && min_collor_nums[i] == null){
					min_collor_nums[i] = j
				}
			}
			if (histo_plot_st[j] != 0){
				min_num = j
			}
		}
		var max_num = null
		var max_collor_nums = [null,null,null]
		for (var j = histo_plot_st.length-1; j >= 0; j--){
			for (var i = 0; i < 3; i++){
				if (color_plot_st[i][j] != 0 && max_collor_nums[i] == null){
					max_collor_nums[i] = j
				}
			}
			if (histo_plot_st[j] != 0){
				max_num = j
			}
		}
		var histo_plot = new Array(128).fill(0)
		var color_plot = [new Array(128).fill(0),new Array(128).fill(0),new Array(128).fill(0)]
		for (var j = 1; j < histo_plot_st.length-1; j++){
			if (j != max_num && j != min_num){
				histo_plot[j] = (histo_plot_st[j-1] + histo_plot_st[j] + histo_plot_st[j+1])/3
				for (var i = 0; i < 3; i++){
					if (j >= max_collor_nums[i]){
						color_plot[i][j] = (color_plot_st[i][j-1] + color_plot_st[i][j] + color_plot_st[i][j+1])/3
					}
					else if (j <= min_collor_nums[i]){
						color_plot[i][j] = (color_plot_st[i][j-1] + color_plot_st[i][j] + color_plot_st[i][j+1])/3
					}
					else {
						color_plot[i][j] = (color_plot_st[i][j-1] + color_plot_st[i][j] + color_plot_st[i][j+1])/3
					}
				}
			}
		}
		console.log(histo_plot)
		document.getElementById( 'histogram'+num ).innerHTML = ""; // clear existing
		var draw = SVG().addTo('#histogram'+num).size( 270, Math.min(Math.max(...histo_plot),125)*0.5+9 );
		draw.attr({
		    'shape-rendering':'crispEdges'
		});
		for (var j = 0; j < histo_plot.length; j++){
			if (histo_plot[j] != 0){
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
			        let mode = draw.text( `${parseInt(j*2*input_dict[reading_types[num]][2]+input_dict[reading_types[num]][0])}` ).font('size',8).font('family','Arial');
					let mode_length = mode.length();
			        mode.move( j*2 - mode_length/2,Math.min(Math.max(...histo_plot),125)*0.5+1 ); // center vertically
				}
			}
		}
        let min_extrem = draw.text( `${parseInt(min_num*2*input_dict[reading_types[num]][2]+input_dict[reading_types[num]][0])}` ).font('size',8).font('family','Arial');
		let min_extrem_length = min_extrem.length();
        min_extrem.move( min_num*2 - min_extrem_length/2,Math.min(Math.max(...histo_plot),125)*0.5+1 ); // center vertically
		
        let max_extrem = draw.text( `${parseInt(max_num*2*input_dict[reading_types[num]][2]+input_dict[reading_types[num]][0])}` ).font('size',8).font('family','Arial');
		let max_extrem_length = max_extrem.length();
        max_extrem.move( max_num*2 - max_extrem_length/2,Math.min(Math.max(...histo_plot),125)*0.5+1 ); // center vertically
		for (var i = 0; i < 128; i++) {
			
			var fillcol = '#ffffff'
	        draw.rect( 2, color_plot[2][i]*0.5 ).move( i*2, (Math.min(Math.max(...histo_plot),125)-color_plot[2][i])*0.5 ).attr({
	            'fill':'#54278f',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
	        draw.rect( 2, color_plot[1][i]*0.5 ).move( i*2, (Math.min(Math.max(...histo_plot),125)-(color_plot[2][i]+color_plot[1][i]))*0.5 ).attr({
	            'fill':'#9e9ac8',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
	        draw.rect( 2, color_plot[0][i]*0.5 ).move( i*2, (Math.min(Math.max(...histo_plot),125)-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i]))*0.5 ).attr({
	            'fill':'#bcbddc',
	            'shape-rendering':'crispEdges',
	            'stroke-width': 0 
	        });
		}
	}
}

function DrawSesonalitys(compresed_data,data_min,data_range){
	console.log('l')
	var color_plot = [new Array(52).fill(0),new Array(52).fill(0),new Array(52).fill(0)]
	color_plot_str = JSON.stringify(color_plot)
	for (var year = 0; year < compresed_data.length; year ++){
		for (var week = 0; week < 52; week ++){
			if (compresed_data[year][week] != null){
				if (compresed_data[year][week] < wx_range_val0*data_range+data_min){
					color_plot[0][week] += 1
				}
				else if (compresed_data[year][week] < wx_range_val1*data_range+data_min){
					color_plot[1][week] += 1
				}
				else {
					color_plot[2][week] += 1
				}
			}
		}
	}
	document.getElementById( 'gr_sesonalitys').innerHTML = ""; // clear existing
	var draw = SVG().addTo('#gr_sesonalitys').size( 523, compresed_data.length*0.5 );
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	for (var i = 0; i < 52; i++) {
		
		var fillcol = '#ffffff'
        draw.rect( 9, color_plot[2][i]*0.5 ).move( i*9+55, (compresed_data.length-color_plot[2][i])*0.5 ).attr({
            'fill':'#54278f',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 9, color_plot[1][i]*0.5 ).move( i*9+55, (compresed_data.length-(color_plot[2][i]+color_plot[1][i]))*0.5 ).attr({
            'fill':'#9e9ac8',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( 9, color_plot[0][i]*0.5 ).move( i*9+55, (compresed_data.length-(color_plot[2][i]+color_plot[1][i]+color_plot[0][i]))*0.5 ).attr({
            'fill':'#bcbddc',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
}
function DrawYears(compresed_data,data_min,data_range){
	console.log('l')
	var color_plot = [new Array(compresed_data.length).fill(0),new Array(compresed_data.length).fill(0),new Array(compresed_data.length).fill(0)]
	color_plot_str = JSON.stringify(color_plot)
	for (var year = 0; year < compresed_data.length; year ++){
		for (var week = 0; week < 52; week ++){
			if (compresed_data[year][week] != null){
				if (compresed_data[year][week] < wx_range_val0*data_range+data_min){
					color_plot[0][year] += 1
				}
				else if (compresed_data[year][week] < wx_range_val1*data_range+data_min){
					color_plot[1][year] += 1
				}
				else {
					color_plot[2][year] += 1
				}
			}
		}
	}
	document.getElementById( 'gr_years').innerHTML = ""; // clear existing
	var draw = SVG().addTo('#gr_years').size( 52*3, (compresed_data.length+1)*9 );
	draw.attr({
	    'shape-rendering':'crispEdges'
	});
	for (var i = 0; i < compresed_data.length; i++) {
		
        draw.rect( color_plot[2][i]*3, 9 ).move( 0, (compresed_data.length-i)*9 ).attr({
            'fill':'#54278f',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( color_plot[1][i]*3, 9 ).move( color_plot[2][i]*3, (compresed_data.length-i)*9 ).attr({
            'fill':'#9e9ac8',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
        draw.rect( color_plot[0][i]*3, 9 ).move( (color_plot[2][i]+color_plot[1][i])*3, (compresed_data.length-i)*9  ).attr({
            'fill':'#bcbddc',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
	for (var i = 0; i < 4; i++) {
        draw.rect( 2, (compresed_data.length+1)*9 ).move( i*31+31, 0  ).attr({
            'fill':'#ffffff66',
            'shape-rendering':'crispEdges',
            'stroke-width': 0 
        });
	}
}

// Renders SVG weather grid/heatmap thing
function RenderGrid(){
    if ( wx_grdata == null )
        return;

	if (!has_reading)
		return;
    var year_label_width = 55;
    var month_label_height = 55;
    var off_x = year_label_width;         // grid offset
    var off_y = 10;
    var boxsize = 8;        // size of a grid unit
    var boxspace = 9;      // total space from unit to unit

    var num_weeks = 52;

	var modifiers = [];
	//Convert the values from the dropdowns (back) into numbers
	for (direction_dropdown of direction_dropdowns){ 
		modifiers.push([parseInt(direction_dropdown.value.split(',')[0]),parseInt(direction_dropdown.value.split(',')[1])]);
	}
	for ( var i = 0; i < modifiers.length; i++ ){
		for ( var k = 0; k < 2; k++ ){
			modifiers[i][k] = parseInt(modifiers[i][k]);
		}
	}	
	var wx_data = [];
    num_years = Object.keys(wx_grdata[reading_types[0]][method_types[0]]).length;
    num_weeks = Object.keys(wx_grdata[reading_types[0]][method_types[0]][0]).length;
	var weight_vals = [];
	for (var i = 0; i < weight_setexes.length; i++) {
		weight_vals.push(parseFloat(weight_setexes[i].textContent));
	}	
	var grids = [];
//	console.log('rend')
//	console.log(reading_types)
	for ( var i = 0; i < reading_types.length; i++ ){
		grids.push(wx_grdata[reading_types[i]][method_types[i]]);		
	};
	console.log(grids)
	var num_years = grids[0].length;
//	console.log(wx_grdata)
//	console.log(grids)
//	console.log(modifiers)
	const total_weight = weight_vals.reduce((a, b) => a + b, 0);//Effectively summing the weights
	for ( var n = 0; n < num_years; n++ ) {
		wx_data.push([]);
		for ( var m = 0; m < num_weeks; m++ ) {
			var num = 0;
			for ( var i = 0; i < grids.length; i++ ){ 
				if (grids[i][n][m] == null){
					num = null
					break
				}
				num += (grids[i][n][m]*modifiers[i][0]+modifiers[i][1])*weight_vals[i];
			}
			if (num == null){
				wx_data[n].push(null)
			}
			else {
				wx_data[n].push(num/total_weight);
			}
		}
	}
    // determine min/max
    num_n = Object.keys(wx_data).length;
    num_m = Object.keys(wx_data[0]).length;
    wx_data_min = Number.MAX_VALUE;
    wx_data_max = Number.MIN_VALUE;
    for ( var n = 0; n < num_n; n++ ){
        for ( var m = 0; m < num_m; m++ ){
            var val = wx_data[n][m];
            if ( val != null )
            {                    
                wx_data_min = parseFloat(Math.min( val, wx_data_min ).toFixed(3));
                wx_data_max = parseFloat(Math.max( val, wx_data_max ).toFixed(3));
            }
        }
    }
    var data_range = wx_data_max - wx_data_min;
	DrawHistogram(wx_data,wx_data_min,data_range)
	DrawSesonalitys(wx_data,wx_data_min,data_range)
	DrawYears(wx_data,wx_data_min,data_range)
    // var color0 = '#edf8b1';
    // var color1 = '#7fcdbb';
    // var color2 = '#2c7fb8';
    var color0 = '#bcbddc';
    var color1 = '#9e9ac8';
    var color2 = '#54278f';

    // create the svg drawing object and draw the grid elements    
    var total_width = boxspace * num_weeks + year_label_width;
    var total_height = boxspace * num_years + off_y * 2 + month_label_height;

    document.getElementById( 'gr_grid' ).innerHTML = ""; // clear existing
    var draw = SVG().addTo('#gr_grid').size( total_width, total_height+num_years );
    draw.attr({
        'shape-rendering':'crispEdges'
    });
    for ( j=0; j<num_years; j++ )
    {
        sy = j * boxspace + off_y;
        // draw year label every 3 rows, vertically centered on the row, to the left of the grid
        syear = num_years + start_year - j;        
        if ( !(j%3) ) {
            var stext = draw.text( `${syear-1} -` ).font('size',12).font('family','Arial');
            syear_width = stext.length();
            syear_height = stext.bbox().height/2; // bbox is double for some reason.
            stext.move( off_x - syear_width, sy - (syear_height/2) );
        }

        for ( i=0; i<num_weeks; i++ )
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
            var mx = wx_data[num_years-1-j][i];
            if ( mx == null )
                fillcol = '#FFFFFF';    // nulls are this color
            else
            {
                mx = Number.parseFloat( mx );
                mx = (mx - wx_data_min) / data_range; // normalize mx 0..1
                if ( mx < wx_range_val0 ){
                    fillcol = color0;
		            shape_rend = 'auto';		// draw the blue grid blocks with AntiAliasing
		        }
                else if ( mx < wx_range_val1 ){
                    fillcol = color1;
                    bsize = boxspace;   // bigger square
                }
                else{
                    fillcol = color2;
                    bsize = boxspace;   // bigger square
                }
            }

            // draw rect
            sx = i * boxspace + off_x;
            draw.rect( bsize, bsize-1 ).move( sx, sy ).attr({
                'fill':fillcol,
                'shape-rendering':shape_rend,
                'stroke-width': 0 
            });
        }
    }

    // draw bottom month labels
    function daysIntoYear( date ){
        return (Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) - Date.UTC(date.getFullYear(), 0, 0)) / 24 / 60 / 60 / 1000;
    }

    function month_to_week( nmonth ) {
        let day_of_year = daysIntoYear( new Date(2020, nmonth, 1) );
        let week = day_of_year * 52.0 / 365.0;
        return week;
    }

    let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec' ];
    let by = num_years * (boxspace) + off_y - (boxspace-boxsize);
    for ( i=0; i < months.length; i++ )
    {
        let btext = draw.text( `-${months[i]}` ).font('size',12).font('family','Arial');
        let bw = btext.length();        
        let bh = btext.bbox().height/2; // bbox is double for some reason.
        let bx = month_to_week( i ) * boxspace + off_x;
        btext.center(bx,by+bw/2).rotate(90);
    }

};