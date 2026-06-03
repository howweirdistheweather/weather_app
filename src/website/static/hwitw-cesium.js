// Your access token can be found at: https://ion.cesium.com/tokens.
// Replace `your_access_token` with your Cesium ion access token.
// Cesium.Ion.defaultAccessToken = 'your_access_token';

const urlParams = new URLSearchParams(window.location.search);
var lat = urlParams.get('lat');
var lon = urlParams.get('lon');
console.log(lat)
var start_latitude = 59.44;
var start_longitude = -151.70;
const start_height = 45000;
var preserve_metrics = false
if (lat){
	start_latitude = parseFloat(lat)
}
if (lon){
	start_longitude = parseFloat(lon)
}
var map = true
var tutorial = false
var has_querry = false
console.log('awerstdyfg')

// Keep track of the last lat/lon string.
let lastPositionString = [];

// Set up the Cesium viewer.



Cesium.Ion.defaultAccessToken = null;



/* Per Carto's website regarding basemap attribution: https://carto.com/help/working-with-data/attribution/#basemaps */
let CartoAttribution = 'Map tiles by <a href="https://carto.com">Carto</a>, under CC BY 3.0. Data by <a href="https://www.openstreetmap.org/">OpenStreetMap</a>, under ODbL.'

// Create ProviderViewModel based on different imagery sources
// - these can be used without Cesium Ion
var imageryViewModels = [];

imageryViewModels.push(new Cesium.ProviderViewModel({
    name: 'OpenStreetMap',
    iconUrl: Cesium.buildModuleUrl('Widgets/Images/ImageryProviders/openStreetMap.png'),
    tooltip: 'OpenStreetMap (OSM) is a collaborative project to create a free editable \
map of the world.\nhttp://www.openstreetmap.org',
    creationFunction: function() {
    return new Cesium.UrlTemplateImageryProvider({
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        subdomains: 'abc',
        minimumLevel: 0,
        maximumLevel: 19
    });
    }
}));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Positron',
//     tooltip: 'CartoDB Positron basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/light_all/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Positron without labels',
//     tooltip: 'CartoDB Positron without labels basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/rastertiles/light_nolabels/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'https://{s}.basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Dark Matter',
//     tooltip: 'CartoDB Dark Matter basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/rastertiles/dark_all/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Dark Matter without labels',
//     tooltip: 'CartoDB Dark Matter without labels basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/rastertiles/dark_nolabels/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'https://{s}.basemaps.cartocdn.com/rastertiles/dark_nolabels/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Voyager',
//     tooltip: 'CartoDB Voyager basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/rastertiles/voyager_labels_under/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
// imageryViewModels.push(new Cesium.ProviderViewModel({
//     name: 'Voyager without labels',
//     tooltip: 'CartoDB Voyager without labels basemap',
//     iconUrl: 'http://a.basemaps.cartocdn.com/rastertiles/voyager_nolabels/5/15/12.png',
//     creationFunction: function() {
//     return new Cesium.UrlTemplateImageryProvider({
//         url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}.png',
//         credit: CartoAttribution,
//         minimumLevel: 0,
//         maximumLevel: 18
//     });
//     }
// }));
imageryViewModels.push(new Cesium.ProviderViewModel({
    name: 'National Map Satellite',
    iconUrl: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/4/6/4',
    creationFunction: function() {
    return new Cesium.UrlTemplateImageryProvider({
        url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}',
        credit: 'Tile data from <a href="https://basemap.nationalmap.gov/">USGS</a>',
        minimumLevel: 0,
        maximumLevel: 16
    });
    }
}));




// const viewer = new Cesium.Viewer("cesiumContainer", {
//       selectionIndicator: false,
//       infoBox: false,
// });
// Initialize the viewer - this works without a token!
const viewer = new Cesium.Viewer('cesiumContainer', {
    imageryProviderViewModels: imageryViewModels,
    selectedImageryProviderViewModel: imageryViewModels[0],
    animation: false,
    timeline: false,
    infoBox: false,
    homeButton: false,
    fullscreenButton: false,
    selectionIndicator: false,
});
// Remove the Terrain section of the baseLayerPicker
viewer.baseLayerPicker.viewModel.terrainProviderViewModels.removeAll()
const scene = viewer.scene;

// Base URL for How Weird Is The Weather.
const urlBase = "/static/index.html?";
//const urlBase = "http://192.168.194.103:5001/static/index.html?";

// Create the Cesium mouse event handler
const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

// Create the entity that will serve as the label that displays the lat/lon.
const label = viewer.entities.add({
      label: {
            show: false,
            showBackground: true,
            font: "14px monospace",
            horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
            verticalOrigin: Cesium.VerticalOrigin.TOP,
            pixelOffset: new Cesium.Cartesian2(15, 0),
      },
});

// Convert a cartographic coord to a fixed decimal string.
function formatCartographic(coordinate) {
      return Cesium.Math.toDegrees(coordinate).toFixed(2);
}

// Given mouse coordinates, get the lat/lon as a string
function getLatLonString(cartesian) {
      if (!cartesian) return;
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
      const longitudeString = formatCartographic(cartographic.longitude);
      const latitudeString = formatCartographic(cartographic.latitude);
      return [longitudeString, latitudeString];
}

// Format the lat/lon as a string for the HWITW URL.
function formatLatLonForHWITW(latLonArray) {
      const [longitudeString, latitudeString] = latLonArray;
      return `lat=${latitudeString}&lon=${longitudeString}`;
}

// Format the lat/lon as a string for the label.
function formatLatLonForLabel(latLonArray) {
      const [longitudeString, latitudeString] = latLonArray;
      return `Lat: ${latitudeString}\u00B0, Lon: ${longitudeString}\u00B0`;
}

// Update the label with the lat/lon string and position it on the globe.
function updateLabel(string, cartesian) {
      label.position = cartesian;
      label.label.show = true;
      label.label.text = string;
}

// Hide the label.
function hideLabel() {
      label.label.show = false;
}

// Show the position of the mouse on the globe while it's moving.
handler.setInputAction(function (movement) {
      const cartesian = viewer.camera.pickEllipsoid(
            movement.endPosition,
            scene.globe.ellipsoid
      );
      const posStrings = getLatLonString(cartesian);
      if (!posStrings) {
            hideLabel();
            return;
      }
      lastPositionString = posStrings; // For the click event.
      const labelString =
      "How Weird Is The Weather at\n" + formatLatLonForLabel(posStrings);
      
      updateLabel(labelString, cartesian);
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE);



var map_btn = document.getElementById("map_btn")

map_btn.addEventListener("click",function () {
	var cesiumContainer = document.getElementById("cesiumContainer")
	var hwitw = document.getElementById("hwitw")
	var hwitwContainer = document.getElementById("hwitw-container")
	if (map) {
		map = false
		// cesiumContainer.style.visibility = 'hidden';
// 		cesiumContainer.style.position = 'absolute';
		hwitw.style.width = '100vw';
		hwitwContainer.style.width = '100vw';
		hwitw.style.hight = '10000';
		hwitwContainer.style.hight = '10000';
		hwitw.style.border = 'none';
		map_btn.innerHTML = '>'
	} else {
		map = true
		hwitw.style.width = '';
		hwitwContainer.style.width = '';
		hwitw.style.hight = '';
		hwitwContainer.style.hight = '';
		hwitw.style.border = '';
		map_btn.innerHTML = '<'
	}
});

window.addEventListener("message", (event) => {
	console.log("ssdfdfgh")
 	if (event.data?.type === "queryString") {
		console.log("sdfgh")
    	const params = new URLSearchParams(event.data.value);
		var url = new URL(window.location.href);
		url.searchParams.set("state", params.get("state"));
		url.searchParams.set("tutorial", params.get("tutorial"));
		var cesiumContainer = document.getElementById("cesiumContainer")
		var hwitw = document.getElementById("hwitw")
		var hwitwContainer = document.getElementById("hwitw-container")
		if (params.get("tutorial") != 'null' && params.get("tutorial") != null){
			if (map){
				hwitw.style.width = '100vw';
				hwitwContainer.style.width = '100vw';
				hwitw.style.hight = '10000';
				hwitwContainer.style.hight = '10000';
				hwitw.style.border = 'none';
				map = false
			}
			map_btn.style.visibility = 'hidden'
			tutorial = true
		} else if (tutorial) {
			map = true
			hwitw.style.width = '';
			hwitwContainer.style.width = '';
			hwitw.style.hight = '';
			hwitwContainer.style.hight = '';
			hwitw.style.border = '';
			map_btn.innerHTML = '<'
			map_btn.style.visibility = 'visible'
		}
		window.history.pushState(null, null, url);
  	} else if (event.data?.type === "preserve_metrics"){
  		preserve_metrics = event.data.value
		console.log(preserve_metrics)
  	}
});
// Set the start position of the viewer and redirect HWITW to that location.
function setStartPosition() {
      const cartesian = Cesium.Cartesian3.fromDegrees(start_longitude, start_latitude, start_height);
      const posStrings = getLatLonString(cartesian);
      lastPositionString = posStrings;
      redirectHWITW();
      // Fly the camera to Juneau at the given longitude, latitude, and height.
      viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(start_longitude, start_latitude, start_height),
            orientation: {
                  heading: Cesium.Math.toRadians(0.0),
                  pitch: Cesium.Math.toRadians(-90.0),
            }
      });
      
}

// Redirect HWITW to the last known lat/lon position.
function redirectHWITW() {
	if (!lastPositionString || !lastPositionString.length) {
	    return;
	}
	// if (!preserve_metrics) {
// 		url.searchParams.set("state","");
// 		window.history.pushState(null, null, url);
// 	}
	const [longitudeString, latitudeString] = lastPositionString;
	var url = new URL(window.location.href);
	url.searchParams.set("lat", latitudeString);
	url.searchParams.set("lon", longitudeString);
	window.history.pushState(null, null, url);
	const locString = formatLatLonForHWITW(lastPositionString);
	const urlParams = new URLSearchParams(window.location.search);
	const tutorial = urlParams.get('tutorial');
	const state = urlParams.get('state');
	const tutorialString = `&tutorial=${tutorial}`;
	const stateString = `&state=${state}`;
	const cesiumString = `&cesium=1`;
	if (tutorial != 'null' && tutorial != null){
		var url = urlBase + tutorialString + cesiumString;
	} else if (state && state != 'null' && preserve_metrics){
		var url = urlBase + locString + tutorialString + stateString + cesiumString;
	} else {
		var url = urlBase + locString + cesiumString;
	}
	//const url = urlBase + locString + internalString;
	document.getElementById("hwitw").src = url;
}



setStartPosition();

// Redirect to HWITW on mouse click.
handler.setInputAction(redirectHWITW, Cesium.ScreenSpaceEventType.LEFT_CLICK);
