<template lang="html">
    <div class="container">
        <div id="mapOL"></div>
        <div style="display: none;">
            <div id="popup"></div>
        </div>

        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Lock Marker Location</label>
            <input type="checkbox" v-model="marker_locked" />
        </div></div>

        <div id="lon">Lat: {{ lat_4326_cursor }}</div>
        <div id="lon">Lng: {{ lng_4326_cursor }}</div>

        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Street</label>
            <input v-model="call_email.location.properties.street" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Town/Suburb</label>
            <input v-model="call_email.location.properties.town_suburb" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">State</label>
            <input v-model="call_email.location.properties.state" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Postcode</label>
            <input v-model="call_email.location.properties.postcode" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Contry</label>
            <input v-model="call_email.location.properties.country" />
       </div></div>
    </div>
</template>

<script>
import Map from "ol/Map.js";
import View from "ol/View.js";
import { defaults as defaultControls, ScaleLine } from "ol/control.js";
import { Tile as TileLayer, Vector as VectorLayer } from "ol/layer.js";
import { XYZ, OSM, WMTS } from "ol/source";
import {
  get,
  addProjection,
  addCoordinateTransforms,
  transform
} from "ol/proj.js";
import Feature from "ol/Feature.js";
import Overlay from "ol/Overlay";
import Point from "ol/geom/Point.js";
import VectorSource from "ol/source/Vector.js";
import { Icon, Style } from "ol/style.js";
import Geocoder from "ol-geocoder/dist/ol-geocoder.js";

import "ol/ol.css";
import "bootstrap/dist/css/bootstrap.css";
import "ol-geocoder/dist/ol-geocoder.css";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";

export default {
  name: "map-openlayers",
  data: function() {
    const defaultCentre = [13775786.985667605, -2871569.067879858];

    return {
      defaultCenter: defaultCentre,
      projection: null,
      map: null,
      popup: null,
      element: null,
      lat_4326_cursor: null,
      lng_4326_cursor: null,
      marker_locked: false,

      feature_marker: null,
      lat_4326: null,
      lng_4326: null,
      country: null,
      postcode: null,
      state: null,
      street: null,
      town_suburb: null
    };
  },
  computed: {
    ...mapGetters({
      call_email: "callemailStore/call_email",
      location: "callemailStore/location"
    }),
    setInitLocation: function() {
      console.log("importMapData");
      //this.call_email.location.geometry = new Point(transform([-31, 118], 'EPSG:4326', 'EPSG:3857'));

      // this is the call_email nested location
      this.call_email.location.geometry = new Point([-31, 118]);

      //this is the separate location vuex object
      this.location.geometry = new Point([-32, 119]);
    }
  },
  /*
  beforeRouteEnter: function(to, from, next) {
    console.log("before route enter");
    let initialisers = [];
    next(vm => {
      console.log("before route enter - next");
      vm.loadLocation({ call_email_id: to.params.call_email_id });
    });
  },
  */
  mounted: function() {
    console.debug("Start loading map");
    //this.importMapData();
    //this.loadLocation({ call_email_id: this.$route.params.call_email_id });
    this.initMap();
    console.debug("End loading map");
  },
  methods: {
    ...mapActions({
      //loadCallEmail: "callemailStore/loadCallEmail",
      //loadLocation: "callemailStore/loadLocation"
    }),
    addMarker: function() {
      var iconFeature = new Feature({
        //geometry: new Point(transform([this.lng_4326, this.lat_4326], 'EPSG:4326', 'EPSG:3857')),
        geometry: new Point(transform([-32, 119], "EPSG:4326", "EPSG:3857"))
      });
      this.feature_marker = iconFeature;
      var iconStyle = new Style({
        image: new Icon(
          /** @type {module:ol/style/Icon~Options} */ ({
            anchor: [16, 32],
            anchorXUnits: "pixels",
            anchorYUnits: "pixels",
            src: require("./pin_gray.png")
          })
        )
      });
      iconFeature.setStyle(iconStyle);
      var vectorSource = new VectorSource({
        features: [iconFeature]
      });
      var vectorLayer = new VectorLayer({
        source: vectorSource
      });
      this.map.addLayer(vectorLayer);
    },
    addGeocoder: function() {
      console.log(Geocoder);
      var geocoder = new Geocoder("nominatim", {
        provider: "osm",
        lang: "en",
        placeholder: "Search for ...",
        targetType: "text-input",
        limit: 5,
        debug: true,
        autoComplete: true,
        autoCompleteMinlength: 2,
        keepOpen: true
      });
      this.map.addControl(geocoder);

      var self = this; // Create a new variable to access data inside the function below.

      geocoder.on("addresschosen", function(evt) {
        console.log(evt);
        var layerAdded = geocoder.getLayer();
        console.log(layerAdded);
        self.map.removeLayer(layerAdded);
      });
    },

    initMap: function() {
      this.projection = get("EPSG:3857");

      var rasterLayer = new TileLayer({ source: new OSM() });
      //var rasterLayerSat = new TileLayer({source: new MapQuest({layer: 'sat'})});

      this.map = new Map({
        controls: defaultControls().extend([
          new ScaleLine({
            units: "metric"
          })
        ]),
        target: "mapOL",
        layers: [rasterLayer],
        view: new View({
          center: [0, 0],
          zoom: 5
        })
      });
      this.map.getView().setCenter(this.defaultCenter);
      this.map.on("click", this.mapClickHandler);

      this.element = document.getElementById("popup");

      this.popup = new Overlay({
        element: this.element,
        positioning: "bottom-center",
        stopEvent: false,
        offset: [0, -25]
      });
      this.map.addOverlay(this.popup);
    },
    relocateMarker: function(coordinates) {
      //this.feature_marker.getGeometry().setCoordinates(coordinates);
      this.call_email.location.getGeometry().setCoordinates(coordinates);
    },
    mapClickHandler: function(e) {
      var coordinate = e.coordinate;
      console.debug(coordinate);
      this.lng_4326_cursor = coordinate[0];
      this.lat_4326_cursor = coordinate[1];

      var lnglat_4326 = transform(
        [coordinate[0], coordinate[1]],
        "EPSG:3857",
        "EPSG:4326"
      );
      this.lng_4326_cursor = lnglat_4326[0];
      this.lat_4326_cursor = lnglat_4326[1];

      var feature = this.map.forEachFeatureAtPixel(e.pixel, function(feature) {
        return feature;
      });
      if (feature) {
        var coordinates = feature.getGeometry().getCoordinates();
        this.popup.setPosition(coordinates);
        $(this.element).popover({
          placement: "top",
          html: true,
          content:
            "<p>" +
            this.street +
            " " +
            this.town_suburb +
            "<br />" +
            this.state +
            " " +
            this.postcode +
            " " +
            this.country +
            "</p>"
        });
        $(this.element).popover("show");
      } else {
        if (!this.marker_locked) {
          this.relocateMarker(coordinate);
        }
        $(this.element).popover("destroy");
      }
    }
  }
};
</script>

<style lang="css">
#mapOL {
  /*    position: relative; */
  height: 400px;
}
.popover {
  position: relative;
}
</style>
