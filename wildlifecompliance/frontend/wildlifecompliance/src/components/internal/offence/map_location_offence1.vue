<template lang="html">
    <div>
        <div class="map-wrapper">
            <div class="search-box">
                <input :id="idSearchInput" class="search-input" />
            </div>
            <div :id="idMap" class="mapLeaf"></div>
            <div class="basemap-button">
                <img :id="idBasemapSat" class="basemap-button-img" src="../../../assets/img/satellite_icon.jpg" @click.stop="setBaseLayer('sat')" />
                <img :id="idBasemapOsm" class="basemap-button-img" src="../../../assets/img/map_icon.png" @click.stop="setBaseLayer('osm')" />
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
            <div v-if="offence.location">
                <input type="number" min="-90" max="90" class="form-control" v-model.number="offence.location.geometry.coordinates[1]" />
            </div>
        </div></div>
        <div class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Longitude:</label>
            <div v-if="offence.location">
                <input type="number" min="-180" max="180" class="form-control" v-model.number="offence.location.geometry.coordinates[0]" />
            </div>
        </div></div>

        <div :id="idLocationFieldsAddress">
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Street</label>
                <input class="form-control" v-model="offence.location.properties.street" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Town/Suburb</label>
                <input class="form-control" v-model="offence.location.properties.town_suburb" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">State</label>
                <input class="form-control" v-model="offence.location.properties.state" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Postcode</label>
                <input class="form-control" v-model="offence.location.properties.postcode" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Country</label>
                <input class="form-control" v-model="offence.location.properties.country" readonly />
            </div></div>
        </div>

        <div :id="idLocationFieldsDetails">
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Details</label>
                <textarea class="form-control location_address_field" v-model="offence.location.properties.details" />
            </div></div>
        </div>
    
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
      iconUrl: require("../../../assets/marker-gray-locked.svg"),
      ...baseDic
    });
    vm.icon_enquiery = Leaf.icon({
      iconUrl: require("../../../assets/marker-green-locked.svg"),
      ...baseDic
    });
    vm.icon_complaint = Leaf.icon({
      iconUrl: require("../../../assets/marker-red-locked.svg"),
      ...baseDic
    });
    vm.icon_incident = Leaf.icon({
      iconUrl: require("../../../assets/marker-yellow-locked.svg"),
      ...baseDic
    });
    vm.guid = guid();

    return {
      defaultCenter: defaultCentre,
      projection: null,
      mapOffence: null,
      popup: null,
      element: null,
      base_layer: "osm",
      awe: null,
      suggest_list: [],
      feature_marker: null,
      cursor_location: null,
      idMap: vm.guid + "mapLeaf",
      idLocationFieldsAddress: vm.guid + "LocationFieldsAddress",
      idLocationFieldsDetails: vm.guid + "LocationFieldsDetails",
      idSearchInput: vm.guid + "SearchInput",
      idBasemapSat: vm.guid + "BasemapSat",
      idBasemapOsm: vm.guid + "BasemapOsm"
    };
  },
  computed: {
    ...mapGetters("callemailStore", {
      call_email: "call_email"
    }),
    ...mapGetters("offenceStore", {
      offence: "offence",
      offence_latitude: "offence_latitude",
      offence_longitude: "offence_longitude"
    })
  },
  watch: {
    call_email: {
      handler: function() {
        this.setMarkerIcon();
      },
      deep: true
    },
    offence_latitude: {
      handler: function() {
        this.setMarkerLocation();
      }
    },
    offence_longitude: {
      handler: function() {
        this.setMarkerLocation();
      }
    }
  },
  mounted: function() {
    let vm = this;

    vm.$nextTick(function() {
      vm.initMap();
      vm.setBaseLayer("osm");
      vm.initAwesomplete();
      if (vm.offence.location && vm.offence.location &&
          vm.offence.location.geometry && vm.offence.location.geometry.coordinates &&
          vm.offence.location.geometry.coordinates.length > 0){
          /* If there is a location loaded, add a marker to the map */
          vm.addMarker([vm.offence.location.geometry.coordinates[1], vm.offence.location.geometry.coordinates[0]]);
          vm.refreshMarkerLocation();
      }
      vm.showHideAddressDetailsFields(false, false);
    });
  },
  methods: {
    ...mapActions("offenceStore", {
      // saveLocation: 'saveLocation',
      setLocationPoint: "setLocationPoint",
      setLocationAddress: "setLocationAddress",
      setLocationAddressEmpty: "setLocationAddressEmpty",
      setLocationDetailsFieldEmpty: "setLocationDetailsFieldEmpty"
    }),
    setMarkerCentre: function() {
      let vm = this;
      let lat = vm.offence.location.geometry.coordinates[1];
      let lng = vm.offence.location.geometry.coordinates[0];
      vm.mapOffence.flyTo({ lat: lat, lng: lng }, 12, {
        animate: true,
        duration: 1.5
      });
    },
    mapTabClicked: function(){
      let vm = this;
      setTimeout(function(){
         /*
          * Map size is changed somehow after the mapInit().  
          * Therefore you need to call this method, otherwise you will get errors once you click on the map
          * Ref: https://gis.stackexchange.com/questions/157128/leaflet-map-isnt-loading-in-the-correct-location
          */
         vm.mapOffence.invalidateSize();
      }, 300);
    },
    setMarkerLocation: function() {
      let vm = this;
      let lat = vm.offence.location.geometry.coordinates[1];
      let lng = vm.offence.location.geometry.coordinates[0];
      if (-90 < lat && lat < 90) {
        if (-180 < lng < 180) {
          let lnglat = [lng, lat];
          vm.feature_marker.setLatLng({ lat: lat, lng: lng });
          vm.mapOffence.flyTo({ lat: lat, lng: lng }, 12, {
            animate: true,
            duration: 1.5
          });
          vm.reverseGeocoding(lnglat);
        }
      }
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
        //ev.preventDefault();
        vm.feature_marker.setIcon(myIcon);
      });
      //vm.feature_marker.bindTooltip("click to lock/unlock");
      vm.feature_marker.addTo(vm.mapOffence);
      vm.setMarkerIcon();
    },
    // saveInstanceLocation: async function() {
    //     await this.$nextTick();
    //     this.saveLocation();
    // },
    reverseGeocoding: function(coordinates_4326) {
      var self = this;

      $.ajax({
        url:
          "https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/" +
          coordinates_4326[0] +
          "," +
          coordinates_4326[1] +
          ".json?" +
          $.param({
            limit: 1,
            types: "address"
          }),
        dataType: "json",
        success: function(data, status, xhr) {
          let address_found = false;
          if (data.features && data.features.length > 0) {
            for (var i = 0; i < data.features.length; i++) {
              if (data.features[i].place_type.includes("address")) {
                self.updateAddressFields(data.features[i]);
                address_found = true;
              }
            }
          }
          if (address_found) {
            self.showHideAddressDetailsFields(true, false);
            self.setLocationDetailsFieldEmpty();
          } else {
            self.showHideAddressDetailsFields(false, true);
            self.setLocationAddressEmpty();
          }
        }
      });
    },
    search: function(place) {
      var self = this;

      var latlng = this.mapOffence.getCenter();
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
              //self.mapOffence.setView(latlng, 13);
              self.mapOffence.flyTo(latlng, 13, {
                animate: true,
                duration: 1.5
              });

              if (!self.feature_marker) {
                self.addMarker([latlng.lat, latlng.lng]);
              }

              self.relocateMarker(latlng);
              if (self.suggest_list[i].feature.place_type.includes("address")) {
                /* Selection has address ==> Update address fields */
                self.showHideAddressDetailsFields(true, false);
                self.updateAddressFields(self.suggest_list[i].feature);
                self.setLocationDetailsFieldEmpty();
              } else {
                self.showHideAddressDetailsFields(false, true);
                self.setLocationAddressEmpty();
              }
            }
          }
          return false;
        });
    },
    updateAddressFields(feature) {
      let properties_for_update = new Object();
      let state_abbr_list = {
        "New South Wales": "NSW",
        Queensland: "QLD",
        "South Australia": "SA",
        Tasmania: "TAS",
        Victoria: "VIC",
        "Western Australia": "WA",
        "Northern Territory": "NT",
        "Australian Capital Territory": "ACT"
      };
      let address_arr = feature.place_name.split(",");
      /* street */
      properties_for_update.street = address_arr[0];
      /*
       * Split the string into suburb, state and postcode
       */
      let reg = /^([a-zA-Z0-9\s]*)\s(New South Wales|Queensland|South Australia|Tasmania|Victoria|Western Australia|Northern Territory|Australian Capital Territory){1}\s+(\d{4})$/gi;
      let result = reg.exec(address_arr[1]);
      /* suburb */
      properties_for_update.town_suburb = result[1].trim();
      /* state */
      let state_abbr = state_abbr_list[result[2].trim()];
      properties_for_update.state = state_abbr;
      /* postcode */
      properties_for_update.postcode = result[3].trim();
      /* country */
      properties_for_update.country = "Australia";
      /* update Vuex */
      this.setLocationAddress(properties_for_update);
    },
    setBaseLayer: function(selected_layer_name) {
      if (selected_layer_name == "sat") {
        this.mapOffence.removeLayer(this.tileLayer);
        this.mapOffence.addLayer(this.tileLayerSat);
        $("#" + this.idBasemapSat).hide();
        $("#" + this.idBasemapOsm).show();
      } else {
        this.mapOffence.removeLayer(this.tileLayerSat);
        this.mapOffence.addLayer(this.tileLayer);
        $("#" + this.idBasemapOsm).hide();
        $("#" + this.idBasemapSat).show();
      }
    },
    showHideAddressDetailsFields: function(
      showAddressFields,
      showDetailsFields
    ) {
      if (showAddressFields) {
        $("#" + this.idLocationFieldsAddress).fadeIn();
      } else {
        $("#" + this.idLocationFieldsAddress).fadeOut();
      }
      if (showDetailsFields) {
        $("#" + this.idLocationFieldsDetails).fadeIn();
      } else {
        $("#" + this.idLocationFieldsDetails).fadeOut();
      }
    },
    /* this function retrieve the coordinates from vuex and applys it to the marker */
    refreshMarkerLocation: function() {
      if (this.offence.location.geometry) {
        // this.feature_marker.setLatLng({lat: this.call_latitude, lng: this.call_longitude });
        this.feature_marker.setLatLng({
          lat: this.offence.location.geometry.coordinates[1],
          lng: this.offence.location.geometry.coordinates[0]
        });
        if (this.offence.location.geometry) {
          this.reverseGeocoding(this.offence.location.geometry.coordinates);
        }
      }
    },
    initMap: function() {
      this.mapOffence = Leaf.map(this.idMap).setView([-31.9505, 115.8605], 4);
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

      this.mapOffence
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
      measureControl.addTo(this.mapOffence);
      Leaf.control.locate().addTo(this.mapOffence);
      // this.mapOffence.flyTo({lat: 30, lng: 135}, 12,{
      //     animate: true,
      //     duration: 1.5
      // });
    },
    /* this function stores the coordinates into the vuex, then call refresh marker function */
    relocateMarker: function(latlng) {
      let lnglat = [latlng.lng, latlng.lat];
      this.setLocationPoint(lnglat);
      this.refreshMarkerLocation();
      this.reverseGeocoding(lnglat);
    },
    onMouseMove: function(e) {
      let vm = this;
      vm.cursor_location = vm.mapOffence.mouseEventToLatLng(e.originalEvent);
    },
    onMouseOut: function(e) {
      this.cursor_location = null;
    },
    onClick: function(e) {
      let self = this;
      let latlng = this.mapOffence.mouseEventToLatLng(e.originalEvent);
      if (!self.feature_marker) {
        self.addMarker([latlng.lat, latlng.lng]);
      }

      /* User clicked on a map, not on any feature */
      this.relocateMarker(latlng);
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
