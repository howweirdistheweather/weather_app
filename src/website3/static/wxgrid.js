/// HWITW project Copyright (C) 2021
// initialize as an array LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value)of zeros. an empty grid.
var wx_grdata = {"Reading Type":Array(60).fill().map(() => Array(52).fill(0)),"Reading Type2":Array(60).fill().map(() => Array(52).fill(0))}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid
var wx_grdata_min = 0.0;
var wx_grdata_max = 1.0;
var wx_range_val0 = 0.33;
var wx_range_val1 = 0.66;
var weight_val = 0.01
var weight_val2 = 0.01
var wxapp_folder = '/wxapp/'    // base folder/url of python app stuff
var next_id_num = 0
var reding_dropdowns = []
var direction_dropdowns = []
var wheght_sliders = []
var wheght_setexis = []

function makeNewElement(id, type, atributes) {
	var theDiv = document.getElementById(id);
	var content = document.createElement(type);
	var atibutes_to_set = Object.keys(atributes);
	for (atibute_to_set of atibutes_to_set) {
		content.setAttribute(atibute_to_set, atributes[atibute_to_set]);
	}
	theDiv.appendChild(content);
}

function makeNewMeasurmeant() {
	makeNewElement("measurements","div",{"style":"text-align: center;","id":"measurement"+next_id_num});
	makeNewElement("measurement"+next_id_num,"select",{"id":"gr-reading_dropdown"+next_id_num});
	reding_dropdowns.push(document.getElementById('gr-reading_dropdown'+next_id_num));
	
	reading_dropdowns[next_id_num].onchange =
	    function () {
	        LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value);
	    };
	LoadReadingDropdown(next_id_num);
	
	makeNewElement("measurement"+next_id_num,"select",{"id":"gr-direction_dropdown"+next_id_num});
	
	// create direction dropdown
	var direction_dropdown = document.getElementById('gr-direction_dropdown'+next_id_num);
	direction_dropdown.onchange =
	    function () {
	        RenderGrid();
	    };
	LoadDirectionDropdown(next_id_num);
	
	makeNewElement("measurement"+next_id_num,"div",{"style":"padding-top: 10px;","id":"weight_slider_holder"+next_id_num});
	makeNewElement("weight_slider_holder"+next_id_num,"div",{"style":"margin: 0 auto; width: 200px; height: 20px;","id":"weight_slider"+next_id_num});
	makeNewElement("measurement"+next_id_num,"div",{"style":"padding-bottom: 20px;","class":"column","id":"weight_stext_div"+next_id_num});
	makeNewElement("weight_stext_div"+next_id_num,"div",{"style":"display: inline-block; margin-left: 10px; color: cornflowerblue; padding-top: 10px;","class":"row","id":"weight_stext"+next_id_num});
	
	wheght_setexis.push(document.getElementById( 'weight_stext'+next_id_num ));

	// create the range slider
	wheght_sliders.push(document.getElementById('weight_slider'+next_id_num));
	noUiSlider.create( weight_sliders[next_id_num], {
	    start: [50],
	    connect: false,
	    range: {
	        'min': 1,
	        'max': 100
	    },     
	});
	
	weight_sliders[next_id_num].noUiSlider.on('update', function (values, handle) {
	    var weight_val = values[0] / 100;
	    // update text and redraw wx grid
	    wheght_setexis[next_id_num].textContent = weight_val.toFixed(2);
		RenderGrid()
	});
	next_id_num++
}
// make wx_grdata an array of zeros
function ClearWXGridData( reading_type , reading_type2 ) {
	var reading_type = reading_type
    wx_grdata = {}; //Array.from(Array(50), () => new Array(52));   // init empty/zero grid
	wx_grdata[reading_type] = Array(60).fill().map(() => Array(52).fill(0))
	wx_grdata[reading_type2] = Array(60).fill().map(() => Array(52).fill(0))
    wx_grdata_min = 0.0;
    wx_grdata_max = 1.0;    
}

let cred_str = 'weird:weather'  // TODO: remove. handy for devel

// do country dropdown
var co_dropdown = document.getElementById('station-co_dropdown');
co_dropdown.options.length = 0;
let default_op0 = document.createElement('option');
default_op0.text = 'Choose Country';
co_dropdown.add(default_op0);
co_dropdown.selectedIndex = 0;
co_dropdown.onchange = 
    function () {
        LoadStates( co_dropdown.value );
    };

// do state dropdown
var state_dropdown = document.getElementById('station-state_dropdown');
function ResetStateDropdown() {
    state_dropdown.options.length = 0;
    let default_op2 = document.createElement('option');
    default_op2.text = 'Choose State';
    state_dropdown.add(default_op2);
    state_dropdown.selectedIndex = 0;
    state_dropdown.onchange = 
        function () {
            LoadStations( co_dropdown.value, state_dropdown.value );
        };
}

// do station dropdown
var st_dropdown = document.getElementById('station-st_dropdown');
function ResetStationDropdown() {
    st_dropdown.options.length = 0;
    let default_op1 = document.createElement('option');
    default_op1.text = 'Choose Station';
    st_dropdown.add(default_op1);
    st_dropdown.selectedIndex = 0;
    st_dropdown.onchange =
        function() {
            LoadWXGrid( st_dropdown.value, reading_dropdown.value, reading_dropdown2.value);
        };
}



function LoadReadingDropdown(num) {
    // get list of reading types
    const co_url = wxapp_folder + 'readingtypes.json'
    fetch( co_url, {    method:'GET',
                        headers: {'Authorization': 'Basic ' + btoa(cred_str)}
                    }
    )
    .then(
        function( response ) {
            if ( response.status !== 200 ) {
                console.warn('Problemo with fetch readingtypes. Status Code: ' + response.status );
                return;
            }

            response.json().then(
                function(data) {
                    reading_dropdowns[num].options.length = 0;                    
                    let option;
                    for (let i = 0; i < data.length; i++) {
                        option = document.createElement('option');
                        option.text = data[i];
                        option.value = data[i];
                        reading_dropdowns[num].add(option);
                    }
                    reading_dropdowns[num].selectedIndex = 1; // skip 0 station_id
                }
            );
        }
    )
    .catch(function(err) {
        console.error('Fetch Error -', err);
    });
}

function LoadDirectionDropdown(num) {
    // get list of reading types
    
    direction_dropdowns[num].options.length = 0;                    
    let option;
    for (let i = 0; i < 2; i++) {
        option = document.createElement('option');
        option.text = ['High','Low'][i];
        option.value = [[1,0],[(-1),1]][i];
        direction_dropdowns[num].add(option);
    }
    direction_dropdowns[num].selectedIndex = 0;
}
// create direction dropdown

// get list of countries
const co_url = wxapp_folder + 'stationsmeta.json'
fetch( co_url, {    method:'GET',
                    headers: {'Authorization': 'Basic ' + btoa(cred_str)}
                }
)
.then(
    function( response ) {
        if ( response.status !== 200 ) {
            console.warn('Problemo with fetch stationsmeta. Status Code: ' + response.status );
            return;
        }

        response.json().then(
            function(data) {
                let option;
                for (let i = 0; i < data.length; i++) {
                    option = document.createElement('option');
                    option.text = data[i].CTRY;
                    option.value = data[i].CTRY;
                    co_dropdown.add(option);
                }
                ResetStateDropdown();
                ResetStationDropdown();
            }
        );
    }
)
.catch(function(err) {
    console.error('Fetch Error -', err);
});

/// get list of states in selected country
/// get list of states in selected country
function LoadStates( current_country ) {
    ResetStateDropdown();

    const state_url = wxapp_folder + `stationsmeta.json?sm_type=co&sm_co=${current_country}`
    fetch( state_url, {   method:'GET',
                            headers: {'Authorization': 'Basic ' + btoa(cred_str)}
                        }
    )
    .then(
        function( response ) {
            if ( response.status !== 200 ) {
                console.warn('Problemo with fetch stationsmeta. Status Code: ' + response.status );
                return;
            }

            response.json().then(
                function(data) {
                    let option;
                    for (let i = 0; i < data.length; i++) {
                        option = document.createElement('option');
                        option.text = data[i].STATE;
                        option.value = data[i].STATE;
                  if ( data[i].CTRY == current_country ) {
                           state_dropdown.add(option);
                  }
                    }
                    ResetStationDropdown();
                }                
            );
        }
    )
    .catch(function(err) {
        console.error('Fetch Error -', err);
    });
}

/// get list of stations in country and state
function LoadStations( current_country, current_state ){
    ResetStationDropdown();

    const st_url = wxapp_folder + `stationsmeta.json?sm_type=state&sm_co=${current_country}&sm_state=${current_state}`
    fetch( st_url, {   method:'GET',
                            headers: {'Authorization': 'Basic ' + btoa(cred_str)}
                        }
    )
    .then(
        function( response ) {
            if ( response.status !== 200 ) {
                console.warn('Problemo with fetch stationsmeta. Status Code: ' + response.status );
                return;
            }

            response.json().then(
                function(data) {
                    let option;
                    for (let i = 0; i < data.length; i++) {
                        option = document.createElement('option');
                        option.text = data[i].STATIONNAME + '  ('+data[i].STATIONID+')';
                        option.value = data[i].WBAN;// .STATIONID;
                  if (data[i].STATE == current_state) {
                           st_dropdown.add(option);
                  }
                    }
                }
            );
        }
    )
    .catch(function(err) {
        console.error('Fetch Error -', err);
    });
}

// get slider range text objects
var wx_stext_val4 = document.getElementById( 'gr_stext0' );
var wx_stext_val5 = document.getElementById( 'gr_stext1' );

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
    wx_stext_val4.textContent = wx_range_val0.toFixed(2);
    wx_stext_val5.textContent = wx_range_val1.toFixed(2);
    RenderGrid();
//    diffDivs[0].innerHTML = values[1] - values[0];
  //  diffDivs[1].innerHTML = values[2] - values[1];
    //diffDivs[2].innerHTML = values[3] - values[2];
});

//var testurl = "plot0.json";
// using port 88 here to get around CORS block
//var testurl = "http://localhost:5000/plot0.json?df_station=13743 RONALD REAGAN WASHINGTON NATL AP&df_col=HourlySeaLevelPressure&df_method=MEDIAN";
function LoadWXGrid( station_id, reading_types) {
	// make modifiers into arrays
	
    // clear existing wxgriddata
    ClearWXGridData(reading_type, reading_type2);
    RenderGrid();
	makeNewMeasurmeant()
	document.getElementById('gr_title').textContent =  'Loading...';
    // AJAX the JSON
    var wxgrid_url = wxapp_folder + `plot0.json?df_station=${station_id}&df_methods=${reading_types}`;
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
                    wx_grdata = data;//JSON.parse( data.response );
					console.log( num_n + ' years & ' + num_m + ' weeks received.' );
					

                    // set the title and render the grig
                    wx_data = RenderGrid();
				    num_j = Object.keys(wx_data).length;
				    num_i = Object.keys(wx_data[0]).length;
					document.getElementById('gr_title').textContent =  num_j + ' years x ' + num_i + ' weeks received.';
                }
            );
        }
    )
    .catch(function(err) {
        console.error('Fetch Error -', err);
    });
}

// Renders SVG weather grid/heatmap thing
function RenderGrid()
{
    if ( wx_grdata == null )
        return;

    var range_bar_off_x = 10;
    var range_bar_label_off_x = 5;
    var range_bar_w = 15;
    var range_bar_label_w = 20;
    var range_bar_total_w = range_bar_off_x + range_bar_w + range_bar_label_off_x + range_bar_label_w;
    var year_label_width = 55;
    var month_label_height = 55;
    var off_x = year_label_width;         // grid offset
    var off_y = 10;
    var boxsize = 8;        // size of a grid unit
    var boxspace = 9;      // total space from unit to unit

    var num_weeks = 52;
    var num_years = 60;
    num_years = Object.keys(wx_grdata[reading_dropdown.value]).length;
    num_weeks = Object.keys(wx_grdata[reading_dropdown.value][0]).length;

    // autoscale/normalize
	var modifier = direction_dropdown.value.split(',')
	var modifier2 = direction_dropdown2.value.split(',')
	for ( var k = 0; k < 2; k++ ){
		modifier[k] = parseInt(modifier[k])
		modifier2[k] = parseInt(modifier2[k])
	}
	var wx_data = []
	// not sure why i had to put the constants but it was crashing otherwize
	var reading_type = reading_dropdown.value
	var reading_type2 = reading_dropdown2.value
	var grid1 = wx_grdata[reading_type];
	var grid2 = wx_grdata[reading_type2];
	for ( var n = 0; n < num_years; n++ ) {
		wx_data.push([]);
		for ( var m = 0; m < num_weeks; m++ ) {
			wx_data[n].push(((grid1[n][m]*modifier[0]+modifier[1])*weight_val + (grid2[n][m]*modifier2[0]+modifier2[1])*weight_val2)/(weight_val+weight_val2));
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

    // var color0 = '#edf8b1';
    // var color1 = '#7fcdbb';
    // var color2 = '#2c7fb8';
    var color0 = '#cde5f7';
    var color1 = '#e8841c';
    var color2 = '#b74926';

    // create the svg drawing object and draw the grid elements    
    var total_width = boxspace * num_weeks + off_x + year_label_width + range_bar_total_w;
    var total_height = boxspace * num_years + off_y * 2 + month_label_height;

    document.getElementById( 'gr_grid' ).innerHTML = ""; // clear existing
    var draw = SVG().addTo('#gr_grid').size( total_width, total_height );
    draw.attr({
        'shape-rendering':'crispEdges'
    });
    for( j=0; j<num_years; j++ )
    {
        sy = j * boxspace + off_y;
        // draw year label every 3 rows, vertically centered on the row, to the left of the grid
        syear = 2020 - j;        
        if ( !(j%3) ) {
            var stext = draw.text( `${syear} -` ).font('size',12).font('family','Arial');
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
            draw.rect( bsize, bsize ).move( sx, sy ).attr({
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
    let by = num_years * boxspace + off_y - (boxspace-boxsize);
    for ( i=0; i < months.length; i++ )
    {
        let btext = draw.text( `-${months[i]}` ).font('size',12).font('family','Arial');
        let bw = btext.length();        
        let bh = btext.bbox().height/2; // bbox is double for some reason.
        let bx = month_to_week( i ) * boxspace + off_x;
        btext.center(bx,by+bw/2).rotate(90);
    }

    // draw the range bar, 3 sections, top to bottom
    let off_rbx = off_x + num_weeks * boxspace + range_bar_off_x;
    let off_rby = off_y;
    let rb_w = range_bar_w;
    let rb_totalh = num_years * boxspace;

    let rb2_h = (1.0 - wx_range_val1) * rb_totalh;
    let rb2_y = off_rby;
    draw.rect( rb_w, rb2_h ).move( off_rbx, rb2_y ).attr({
        'fill':color2
    });

    let rb1_h = (1.0 - wx_range_val0) * rb_totalh - rb2_h;
    let rb1_y = off_rby + rb2_h;
    draw.rect( rb_w, rb1_h ).move( off_rbx, rb1_y ).attr({
        'fill':color1
    });

    let rb0_h = wx_range_val0 * rb_totalh;
    let rb0_y = off_rby + rb1_h + rb2_h;
    draw.rect( rb_w, rb0_h ).move( off_rbx, rb0_y ).attr({
        'fill':color0
    });

    // draw the 4 range bar labels
    function draw_rblabel( lstr, lx, ly ){
        let rtext = draw.text( lstr ).font('size',12).font('family','Arial');
        rtext_h = rtext.bbox().height/2; // bbox is double for some reason.
        rtext.move( lx, ly - (rtext_h/2) ); // center vertically
    }
    let off_rlabx = off_rbx + rb_w + range_bar_label_off_x;
    let rlab3 = `${wx_data_max}`;
    draw_rblabel( rlab3, off_rlabx, rb2_y );

    let rlab2 = (wx_data_min + (wx_range_val1 * data_range));
    draw_rblabel( rlab2.toFixed(3), off_rlabx, rb1_y );

    let rlab1 = wx_data_min + (wx_range_val0 * data_range);
    draw_rblabel( rlab1.toFixed(3), off_rlabx, rb0_y );

    let rlab0 = `${wx_data_min}`;
    draw_rblabel( rlab0, off_rlabx, rb2_y + rb_totalh );
	return wx_data;
}
