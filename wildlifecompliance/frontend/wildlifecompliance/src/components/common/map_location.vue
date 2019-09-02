<template lang="html">
    <div>
        <div class="map-wrapper">
            <div class="search-box">
                <input :id="idSearchInput" class="search-input" />
            </div>
            <div :id="idMap" class="mapLeaf"></div>
            <div class="basemap-button">
                <img :id="idBasemapSat" class="basemap-button-img" src="../../assets/img/satellite_icon.jpg" @click.stop="setBaseLayer('sat')" />
                <img :id="idBasemapOsm" class="basemap-button-img" src="../../assets/img/map_icon.png" @click.stop="setBaseLayer('osm')" />
            </div>
            <div class="cursor-location">
                <div v-if="cursor_location">
                    <span>{{ cursor_location.lat.toFixed(5) }}, {{ cursor_location.lng.toFixed(5) }}</span>
                </div>
            </div>
            <div class="centre_marker" @click.stop="setMarkerCentre()">
                CenterMarker
            </div>
        </div>

        <div class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Latitude:</label>
            <div v-if="marker_lat">
                <input type="number" min="-90" max="90" class="form-control" v-model.number="marker_lat" />
            </div>
        </div></div>
        <div class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Longitude:</label>
            <div v-if="marker_lng">
                <input type="number" min="-180" max="180" class="form-control" v-model.number="marker_lng" />
            </div>
        </div></div>
    </div>
</template>

<script>
import Leaf from "leaflet";
import "leaflet-measure"; /* This should be imported after leaflet */
import "leaflet.locatecontrol";
import Awesomplete from "awesomplete";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import { guid } from "@/utils/helpers";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";
import "leaflet/dist/leaflet.css";
import "leaflet-measure/dist/leaflet-measure.css";
import "leaflet.locatecontrol/dist/L.Control.Locate.min.css";

export default {
  name: "map-leaflet",
    props: {
        marker_longitude: {
            required: false,
            default: null,
        },
        marker_latitude: {
            required: false,
            default: null,
        }
    },
  data: function() {
    const defaultCentre = [13775786.985667605, -2871569.067879858];

    let vm = this;
    let baseDic = {
      shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
      shadowSize: [41, 41],
      shadowAnchor: [12, 41],
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -20]
    };
    vm.icon_default = Leaf.icon({
      iconUrl: require("../../assets/marker-gray-locked.svg"),
      ...baseDic
    });
    vm.guid = guid();

    return {
       // marker_lng: vm.marker_longitude,
       // marker_lat: vm.marker_latitude,
        marker_lng: null,
        marker_lat: null,
        defaultCenter: defaultCentre,
        projection: null,
        mainMap: null,
        popup: null,
        element: null,
        base_layer: "osm",
        awe: null,
        suggest_list: [],
        feature_marker: null,
        cursor_location: null,
        idMap: vm.guid + "mapLeaf",
        idSearchInput: vm.guid + "SearchInput",
        idBasemapSat: vm.guid + "BasemapSat",
        idBasemapOsm: vm.guid + "BasemapOsm"
    };
  },
    computed: {
      //  marker_lat: function() {
      //      return this.marker_latitude;
      //  },
      //  marker_lng: function() {
      //      return this.marker_longitude;
      //  },
    },
    watch: {
        marker_latitude: function(){
            this.marker_lat = this.marker_latitude;
        },
        marker_longitude: function(){
            this.marker_lng = this.marker_longitude;
        },
        marker_lat: function(){
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                this.refreshMarkerLocation();
            }
        },
        marker_lng: function(){
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                this.refreshMarkerLocation();
            }
        }
    },
    
  mounted: function() {
    let vm = this;

    //vm.$nextTick(function() {
      vm.initMap();
      vm.setBaseLayer("osm");
      vm.initAwesomplete();
      if (vm.marker_lat && vm.marker_lng){
          /* If there is a location loaded, add a marker to the map */
          vm.addMarker([vm.marker_lat, vm.marker_lng]);
      }
    //});
  },
  methods: {
    setMarkerCentre: function() {
        let z = this.mainMap.getZoom();
        if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
            let latlng = [this.marker_lat, this.marker_lng]

            this.mainMap.flyTo(latlng, z, {
                animate: true,
                duration: 1.5
            });
        }
    },
    invalidateSize: function(){
         /*
          * Call this method when the map is shown incompletely.
          * Ref: https://gis.stackexchange.com/questions/157128/leaflet-map-isnt-loading-in-the-correct-location
          * Ref: github.com/Leaflet/Leaflet/issues/4835
          */
      let vm = this;
      setTimeout(function(){
         vm.mainMap.invalidateSize();
      }, 300);
    },
    setMarkerIcon: function() {
      let vm = this;
      if (vm.feature_marker) {
        vm.feature_marker.setIcon(vm.icon_default);
      }
    },
    addMarker(latLngArr) {
      let vm = this;
      vm.feature_marker = Leaf.marker(
        { lon: latLngArr[1], lat: latLngArr[0] },
        { icon: vm.icon_default }
      ).on("click", function(ev) {
        //vm.feature_marker.setIcon(myIcon);
      });
      //vm.feature_marker.bindTooltip("click to lock/unlock");
      vm.feature_marker.addTo(vm.mainMap);
      vm.setMarkerIcon();
    },
    search: function(place) {
      var self = this;

      var latlng = this.mainMap.getCenter();
      $.ajax({
        url:
          "https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/" +
          encodeURIComponent(place) +
          ".json?" +
          $.param({
            country: "au",
            limit: 10,
            proximity: "" + latlng.lng + "," + latlng.lat,
            //proximity: ''+centre[0]+','+centre[1],
            bbox: "112.920934,-35.191991,129.0019283,-11.9662455",
            types:
              "region,postcode,district,place,locality,neighborhood,address,poi"
          }),
        dataType: "json",
        success: function(data, status, xhr) {
          self.suggest_list = []; // Clear the list first
          if (data.features && data.features.length > 0) {
            for (var i = 0; i < data.features.length; i++) {
              self.suggest_list.push({
                label: data.features[i].place_name,
                value: data.features[i].place_name,
                feature: data.features[i]
              });
            }
          }

          self.awe.list = self.suggest_list;
          self.awe.evaluate();
        }
      });
    },
    initAwesomplete: function() {
      var self = this;
      var element_search = document.getElementById(self.idSearchInput);
      this.awe = new Awesomplete(element_search);
      $(element_search)
        .on("keyup", function(ev) {
          var keyCode = ev.keyCode || ev.which;
          if (
            (48 <= keyCode && keyCode <= 90) ||
            (96 <= keyCode && keyCode <= 105) ||
            keyCode == 8 ||
            keyCode == 46
          ) {
            self.search(ev.target.value);
            return false;
          }
        })
        .on("awesomplete-selectcomplete", function(ev) {
          ev.preventDefault();
          ev.stopPropagation();
          /* User selected one of the search results */
          for (var i = 0; i < self.suggest_list.length; i++) {
            if (self.suggest_list[i].value == ev.target.value) {
              var latlng = {
                lat: self.suggest_list[i].feature.geometry.coordinates[1],
                lng: self.suggest_list[i].feature.geometry.coordinates[0]
              };

              self.mainMap.flyTo(latlng, 13, {
                animate: true,
                duration: 1.5
              });

              if (!self.feature_marker) {
                self.addMarker([latlng.lat, latlng.lng]);
              } else {
                    self.marker_lat = latlng.lat;
                    self.marker_lng = latlng.lng;
              }
            }
          }
          return false;
        });
    },
    setBaseLayer: function(selected_layer_name) {
      if (selected_layer_name == "sat") {
        this.mainMap.removeLayer(this.tileLayer);
        this.mainMap.addLayer(this.tileLayerSat);
        $("#" + this.idBasemapSat).hide();
        $("#" + this.idBasemapOsm).show();
      } else {
        this.mainMap.removeLayer(this.tileLayerSat);
        this.mainMap.addLayer(this.tileLayer);
        $("#" + this.idBasemapOsm).hide();
        $("#" + this.idBasemapSat).show();
      }
    },
    /* this function retrieve the coordinates from vuex and applys it to the marker */
    refreshMarkerLocation: function() {
        if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
            let latlng = [this.marker_lat, this.marker_lng];
            console.log('refreshMarkerLocation');
            console.log(latlng);

            if (!this.feature_marker) {
                this.addMarker(latlng);
            }
            this.feature_marker.setLatLng({
                lat: this.marker_lat,
                lng: this.marker_lng,
            });
            //this.setMarkerCentre();

            this.$emit('location-updated', {'lat': this.marker_lat, 'lng': this.marker_lng});
      }
    },
    initMap: function() {
        if (this.marker_lat && this.marker_lng) {
            this.mainMap = Leaf.map(this.idMap).setView([this.marker_lat, this.marker_lng], 12);
        } else {
            this.mainMap = Leaf.map(this.idMap).setView([-31.9505, 115.8605], 4);
        }

      this.tileLayer = Leaf.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
          attribution:
            '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, contributiors'
        }
      );

      this.tileLayerSat = Leaf.tileLayer.wmts(
        "https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts",
        {
          layer: "public:mapbox-satellite",
          tilematrixSet: "mercator",
          format: "image/png"
        }
      );

      this.mainMap
        .on("click", this.onClick)
        .on("mousemove", this.onMouseMove)
        .on("mouseout", this.onMouseOut);
      this.setBaseLayer("osm");
      let measureControl = new Leaf.Control.Measure({
        position: "topleft",
        primaryLengthUnit: "meters",
        activeColor: "#ff7f50",
        completedColor: "#228b22"
      });
      measureControl.addTo(this.mainMap);
      Leaf.control.locate().addTo(this.mainMap);
    },
    onMouseMove: function(e) {
      let vm = this;
      vm.cursor_location = vm.mainMap.mouseEventToLatLng(e.originalEvent);
    },
    onMouseOut: function(e) {
      this.cursor_location = null;
    },
    onClick: function(e) {
      let self = this;
      let latlng = this.mainMap.mouseEventToLatLng(e.originalEvent);
      if (!self.feature_marker) {
        self.addMarker([latlng.lat, latlng.lng]);
      }

      /* User clicked on a map, not on any feature */
        this.marker_lat = latlng.lat;
        this.marker_lng = latlng.lng;
    }
  }
};
</script>

<style scoped lang="css">
.map-wrapper {
  position: relative;
}
.mapLeaf {
  /* position: relative; */
  height: 500px;
  /* width: 800px; */
  cursor: default;
}
.search-box {
  z-index: 1000;
  position: absolute;
  top: 10px;
  left: 50px;
}
.search-input {
  z-index: 1000;
  width: 300px;
  padding: 5px;
  -moz-border-radius: 5px;
  -webkit-border-radius: 5px;
  border-radius: 5px;
}
.basemap-button {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 400;
  -moz-box-shadow: 3px 3px 3px #777;
  -webkit-box-shadow: 3px 3px 3px #777;
  box-shadow: 3px 3px 3px #777;
  -moz-filter: brightness(1);
  -webkit-filter: brightness(1);
  filter: brightness(1);
  border: 2px white solid;
}
.basemap-button-img {
  /* border-radius: 5px; */
}
.basemap-button:hover {
  cursor: pointer;
  -moz-filter: brightness(0.9);
  -webkit-filter: brightness(0.9);
  filter: brightness(0.9);
}
.basemap-button:active {
  top: 11px;
  right: 9px;
  -moz-box-shadow: 2px 2px 2px #555;
  -webkit-box-shadow: 2px 2px 2px #555;
  box-shadow: 2px 2px 2px #555;
  -moz-filter: brightness(0.8);
  -webkit-filter: brightness(0.8);
  filter: brightness(0.8);
}
.basemap-button:active {
  top: 11px;
  right: 9px;
  -moz-box-shadow: 2px 2px 2px #555;
  -webkit-box-shadow: 2px 2px 2px #555;
  box-shadow: 2px 2px 2px #555;
  -moz-filter: brightness(0.8);
  -webkit-filter: brightness(0.8);
  filter: brightness(0.8);
}
.location_address_field {
  resize: vertical;
}
.cursor-location {
  position: absolute;
  bottom: 0px;
  color: white;
  background-color: rgba(37, 45, 51, 0.6);
  z-index: 1050;
  font-size: 0.9em;
  padding: 5px;
}
.centre_marker {
  position: absolute;
  bottom: 30px;
  color: white;
  background-color: rgba(37, 45, 51, 0.6);
  z-index: 1050;
  font-size: 0.9em;
  padding: 5px;
  cursor: pointer;
}
</style>
