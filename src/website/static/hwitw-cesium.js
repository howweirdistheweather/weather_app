// Your access token can be found at: https://ion.cesium.com/tokens.
// Replace `your_access_token` with your Cesium ion access token.
// Cesium.Ion.defaultAccessToken = 'your_access_token';

const start_latitude = 58.35;
const start_longitude = -134.63;
const start_height = 45000;

// Keep track of the last lat/lon string.
let lastPositionString = [];

// Set up the Cesium viewer.
const viewer = new Cesium.Viewer("cesiumContainer", {
      selectionIndicator: false,
      infoBox: false,
});
const scene = viewer.scene;

// Base URL for How Weird Is The Weather.
const urlBase = "https://hwitw-dev.arcticdata.io/static/index.html?";

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
      const hwitwString = formatLatLonForHWITW(lastPositionString);
      const url = urlBase + hwitwString;
      document.getElementById("hwitw").src = url;
}

setStartPosition();

// Redirect to HWITW on mouse click.
handler.setInputAction(redirectHWITW, Cesium.ScreenSpaceEventType.LEFT_CLICK);
