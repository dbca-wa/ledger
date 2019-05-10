<template lang="html">
    <div>
        <div id="map-wrapper">
        <div id="search-box">
                <!-- input id="search-input" v-on:click.stop="()=>{}" v-on:dblclick.stop="()=>{}" / -->
                <input id="search-input" />
            </div>
        <div id="map">

        </div>
            <div id="basemap-button">
                <img id="basemap_sat" src="../../../assets/img/satellite_icon.jpg" @click.stop="setBaseLayer('sat')" />
                <img id="basemap_osm" src="../../../assets/img/map_icon.png" @click.stop="setBaseLayer('osm')" />
            </div>
        </div>

        <div id="lat" class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Latitude:</label>
            <div v-if="call_email.location">
                <input class="form-control" v-model="call_email.location.geometry.coordinates[1]" readonly />
            </div>
        </div></div>
        <div id="lon" class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Longitude:</label>
            <div v-if="call_email.location">
                <input class="form-control" v-model="call_email.location.geometry.coordinates[0]" readonly />
            </div>
        </div></div>

        <div id="location_fields_address">
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Street</label>
                <input class="form-control" v-model="call_email.location.properties.street" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Town/Suburb</label>
                <input class="form-control" v-model="call_email.location.properties.town_suburb" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">State</label>
                <input class="form-control" v-model="call_email.location.properties.state" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Postcode</label>
                <input class="form-control" v-model="call_email.location.properties.postcode" readonly />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Country</label>
                <input class="form-control" v-model="call_email.location.properties.country" readonly />
            </div></div>
        </div>

        <div id="location_fields_details">
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Details</label>
                <textarea id="location_address_field" class="form-control" v-model="call_email.location.properties.details" />
            </div></div>
        </div>
    
       <button @click.prevent="saveInstanceLocation" class="btn btn-primary pull-right">update</button>
    </div>
</template>

<script>
import Awesomplete from 'awesomplete';

import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default {
    name: "map-leaflet",
    data: function(){
        const defaultCentre = [13775786.985667605, -2871569.067879858];

        return {
            defaultCenter: defaultCentre,
            projection: null,
            map: null,
            popup: null,
            element: null,
            marker_locked: false,
            base_layer: 'osm',
            awe: null,
            suggest_list: [],
            feature_marker: null,
        };
    },
    computed: {
        ...mapGetters('callemailStore', {
            call_email: 'call_email',
        }),
    },
    mounted: function(){
        console.log("this.call_email.location");
        console.log(this.call_email.location);
        this.$nextTick(function() {
            console.debug('Start loading map');
            this.initMap();
            this.setBaseLayer('osm');
            this.initAwesomplete();
            this.addMarker([0, 0]);
            this.refreshMarkerLocation();
            console.debug('End loading map');
        });
    },

    methods: {
        ...mapActions('callemailStore', {
            saveLocation: 'saveLocation',
            setLocationPoint: 'setLocationPoint',
        }),
        addMarker(coord){
            let self = this;

            let testIcon = L.icon({
                iconUrl: require('../../../assets/marker-green-locked.svg'),
                shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
                shadowSize: [41, 41],
                shadowAnchor: [12, 41],
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -20]
            });

            let myIcon = L.icon({
                iconUrl: require('../../../assets/marker-green-unlocked.svg'),
                shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
                shadowSize: [41, 41],
                shadowAnchor: [12, 41],
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -20]
            });
            self.feature_marker = L.marker({lon: coord[1], lat: coord[0]}, {icon: myIcon}).on('click', function(ev){
                self.marker_locked = !self.marker_locked;
                if (self.marker_locked){
                    self.feature_marker.setIcon(testIcon);
                }else{
                    self.feature_marker.setIcon(myIcon);
                }
            });
            self.feature_marker.addTo(self.map);
        },
        saveInstanceLocation: async function() {
            await this.$nextTick();
            this.saveLocation();
        },
        reverseGeocoding: function(coordinates_4326){
            var self = this;

            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+coordinates_4326[0] + ',' + coordinates_4326[1] +'.json?'+ $.param({
                    limit: 1,
                    types: 'address'
                }),
                dataType: 'json',
                success: function(data, status, xhr) {
                    console.log('reverse results: ');
                    console.log(data);
                    let address_found = false;
                    if (data.features && data.features.length > 0){
                        for (var i = 0; i < data.features.length; i++){
                            if(data.features[i].place_type.includes('address')){
                                self.updateAddressFields(data.features[i]);
                                address_found = true;
                            }
                        }
                    }
                    if(address_found){
                        console.log("address found");
                        self.showHideAddressDetailsFields(true, false);
                    } else {
                        console.log("address not found");
                        self.showHideAddressDetailsFields(false, true);
                        self.clearAddressFields();
                    }
                }
            });
        },
        search: function(place){
            var self = this;

            var latlng = this.map.getCenter();
            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+encodeURIComponent(place)+'.json?'+ $.param({
                    country: 'au',
                    limit: 10,
                    proximity: ''+latlng.lng+','+latlng.lat,
                    //proximity: ''+centre[0]+','+centre[1],
                    bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
                    types: 'region,postcode,district,place,locality,neighborhood,address,poi'
                }),
                dataType: 'json',
                success: function(data, status, xhr) {
                    self.suggest_list = [];  // Clear the list first
                    if (data.features && data.features.length > 0){
                        for (var i = 0; i < data.features.length; i++){
                            self.suggest_list.push({ label: data.features[i].place_name,
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
        initAwesomplete: function(){
            var self = this;
            var element_search = document.getElementById('search-input');
            this.awe = new Awesomplete(element_search);
            $(element_search).on('keyup', function(ev){
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105)){
                    self.search(ev.target.value);
                    return false;
                }
            }).on('awesomplete-selectcomplete', function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                /* User selected one of the search results */
                for (var i=0; i<self.suggest_list.length; i++){
                    if (self.suggest_list[i].value == ev.target.value){
                        var latlng = {lat: self.suggest_list[i].feature.geometry.coordinates[1], lng: self.suggest_list[i].feature.geometry.coordinates[0]};
                        //self.map.setView(latlng, 13);
                        self.map.flyTo(latlng, 13,{
                            animate: true,
                            duration: 1.5
                        });

                        /* Do nothing if the marker is locked */
                        if(self.marker_locked){ return; }

                        self.relocateMarker(latlng);
                        if(self.suggest_list[i].feature.place_type.includes('address')){
                            /* Selection has address ==> Update address fields */
                            self.showHideAddressDetailsFields(true, false);
                            self.updateAddressFields(self.suggest_list[i].feature);
                        } else {
                            self.showHideAddressDetailsFields(false, true);
                            self.setLocationPropertiesEmpty();
                        }
                    }
                }
                return false;
            });
        },
        updateAddressFields(feature){
            console.log('updateAddressField');

            let state_abbr_list = {
                    "New South Wales": "NSW",
                    "Queensland": "QLD",
                    "South Australia": "SA",
                    "Tasmania": "TAS",
                    "Victoria": "VIC",
                    "Western Australia": "WA",
                    "Northern Territory": "NT",
                    "Australian Capital Territory": "ACT",
            };
            let address_arr = feature.place_name.split(',');

            /* street */
            this.call_email.location.properties.street = address_arr[0];

            /*
             * Split the string into suburb, state and postcode
             */
            let reg = /^([a-zA-Z0-9\s]*)\s(New South Wales|Queensland|South Australia|Tasmania|Victoria|Western Australia|Northern Territory|Australian Capital Territory){1}\s+(\d{4})$/gi;
            let result = reg.exec(address_arr[1]);

            /* suburb */
            this.call_email.location.properties.town_suburb = result[1].trim();

            /* state */
            let state_abbr = state_abbr_list[result[2].trim()]
            this.call_email.location.properties.state = state_abbr;

            /* postcode */
            this.call_email.location.properties.postcode = result[3].trim();
        },
        setBaseLayer: function(selected_layer_name){
            if (selected_layer_name == 'sat') {
                this.map.removeLayer(this.tileLayer);
                this.map.addLayer(this.tileLayerSat);
                $('#basemap_sat').hide();
                $('#basemap_osm').show();
            }
            else {
                this.map.removeLayer(this.tileLayerSat);
                this.map.addLayer(this.tileLayer);
                $('#basemap_osm').hide();
                $('#basemap_sat').show();
            }
        },
        showHideAddressDetailsFields: function(showAddressFields, showDetailsFields){
            if(showAddressFields){
                $("#location_fields_address").fadeIn();
            } else {
                $("#location_fields_address").fadeOut();
            }
            if(showDetailsFields){
                $("#location_fields_details").fadeIn();
            } else {
                $("#location_fields_details").fadeOut();
            }
        },
        /* this function retrieve the coordinates from vuex and applys it to the marker */
        refreshMarkerLocation: function(){
            if (this.call_email.location.geometry.coordinates.length > 0) {
                this.feature_marker.setLatLng({lat: this.call_email.location.geometry.coordinates[1], lng: this.call_email.location.geometry.coordinates[0]});
                this.reverseGeocoding(this.call_email.location.geometry);
            } 
        },
        initMap: function(){
            this.map = L.map('map').setView([-31.9505, 115.8605], 4);
            this.tileLayer = L.tileLayer(
                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                {
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, contributiors',
                }
            );

            this.tileLayerSat = L.tileLayer.wmts(
                'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                {
                    layer: 'public:mapbox-satellite',
                    tilematrixSet: 'mercator',
                    format: 'image/png',
                }
            );

            this.map.on('click', this.onClick);
            this.setBaseLayer('osm');
        },
        /* this function stores the coordinates into the vuex, then call refresh marker function */
        relocateMarker: function(latlng){ 
            let lnglat = [latlng.lng, latlng.lat];
            this.setLocationPoint(lnglat);
            this.refreshMarkerLocation();
            this.reverseGeocoding(lnglat);
        },
        onClick: function(e){
            let self = this;
            let latlng = this.map.mouseEventToLatLng(e.originalEvent);
            console.log(latlng);
            /* User clicked on a map, not on any feature */
            if(!this.marker_locked){
                this.relocateMarker(latlng);
            }
        }
    },
}
</script>

<style lang="css">
#map-wrapper {
    position: relative;
}
#map {
    position: relative;
    height: 500px;
    cursor: default;
}
#search-box {
    z-index: 1000;
    position: absolute;
    top: 10px;
    left: 50px;
}
#search-input {
    z-index: 1000;
    width: 300px;
    padding: 5px;
    -moz-border-radius: 5px;
    -webkit-border-radius: 5px;
    border-radius: 5px;
}
#basemap-button {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1000;
    -moz-box-shadow: 5px 5px 5px #555;
    -webkit-box-shadow: 5px 5px 5px #555;
    box-shadow: 5px 5px 5px #555;
    -moz-filter: brightness(1.0);
    -webkit-filter: brightness(1.0);
    filter: brightness(1.0);
}
#basemap_sat,#basemap_osm {
    border-radius: 5px;
}
#basemap-button:hover {
    cursor: pointer;
    -moz-filter: brightness(0.9);
    -webkit-filter: brightness(0.9);
    filter: brightness(0.9);
}
#basemap-button:active {
    top: 11px;
    right: 9px;
    -moz-box-shadow: 2px 2px 2px #555;
    -webkit-box-shadow: 2px 2px 2px #555;
    box-shadow: 2px 2px 2px #555;
    -moz-filter: brightness(0.8);
    -webkit-filter: brightness(0.8);
    filter: brightness(0.8);
}
#location_address_field {
    resize: vertical;
}
</style>