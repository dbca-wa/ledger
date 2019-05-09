<template lang="html">
    <div>
        <div id="mapOL">
            <div id="search-box">
                <input id="search-input" />
            </div>

            <div id="basemap-button">
                <img id="basemap_sat" src="../../../assets/img/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                <img id="basemap_osm" src="../../../assets/img/map_icon.png" @click="setBaseLayer('osm')" />
            </div>
            <div style="display: none;">
                <div id="popup"></div>
            </div>
        </div>

        <div class="col-sm-12"><div class="row">
            <input type="checkbox" v-model="marker_locked" />
            <label class="col-sm-4">Lock Marker Location</label>
        </div></div>
        <div id="lat" class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Latitude:</label>
            <div v-if="call_email.location">
                <input class="form-control" v-model="call_email.location.geometry.coordinates[1]" />
            </div>
        </div></div>
        <div id="lon" class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Longitude:</label>
            <div v-if="call_email.location">
                <input class="form-control" v-model="call_email.location.geometry.coordinates[0]" />
            </div>
        </div></div>

        <div id="location_fields_address">
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Street</label>
                <input class="form-control" v-model="call_email.location.properties.street" />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Town/Suburb</label>
                <input class="form-control" v-model="call_email.location.properties.town_suburb" />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">State</label>
                <input class="form-control" v-model="call_email.location.properties.state" />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Postcode</label>
                <input class="form-control" v-model="call_email.location.properties.postcode" />
            </div></div>
            <div class="col-sm-12 form-group"><div class="row">
                <label class="col-sm-4">Country</label>
                <input class="form-control" v-model="call_email.location.properties.country" />
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
import pin from '../../../assets/pin.svg';
import Awesomplete from 'awesomplete';
import Map from 'ol/Map.js';
import tilegridWMTS from 'ol/tilegrid/WMTS.js';
import { getWidth, getTopLeft } from 'ol/extent.js';
import View from 'ol/View.js';
import { defaults as defaultControls, ScaleLine} from 'ol/control.js';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer.js';
import { XYZ, OSM, WMTS } from 'ol/source';
import { get, addProjection, addCoordinateTransforms, transform, toLonLat, fromLonLat } from 'ol/proj.js';
import Feature from 'ol/Feature.js';
import Overlay from 'ol/Overlay';
import Point from 'ol/geom/Point.js';
import VectorSource from 'ol/source/Vector.js';
import { Icon, Style } from 'ol/style.js';

import 'ol/ol.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'ol-geocoder/dist/ol-geocoder.css';
import 'awesomplete/awesomplete.css';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";

export default {
    name: "map-openlayers",
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
        this.$nextTick(function() {
        console.debug('Start loading map');
        this.initMap();
        this.setBaseLayer('osm');
        this.initAwesomplete();
        this.addMarker();
        this.refreshMarkerLocation();
        console.debug('End loading map');
        });
    },

    methods: {
        ...mapActions('callemailStore', {
            saveLocation: 'saveLocation',
            setLocationPoint: 'setLocationPoint',
            setLocationProperties: 'setLocationProperties',
            setLocationPropertiesEmpty: 'setLocationPropertiesEmpty'
        }),
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
                                console.log("data.features[i]");
                                console.log(data.features[i]);
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
                        self.setLocationPropertiesEmpty();
                    }
                }
            });
        },
        search: function(place){
            var self = this;

            var centre = toLonLat(this.map.getView().getCenter());
            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+encodeURIComponent(place)+'.json?'+ $.param({
                    country: 'au',
                    limit: 10,
                    proximity: ''+centre[0]+','+centre[1],
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
                /* User selected one of the search results */
                for (var i=0; i<self.suggest_list.length; i++){
                    if (self.suggest_list[i].value == ev.target.value){
                        self.moveMapCentre(self.suggest_list[i].feature.geometry.coordinates);

                        /* Do nothing if the marker is locked */
                        if(self.marker_locked){ return; }

                        self.relocateMarker4326(self.suggest_list[i].feature.geometry.coordinates);
                        if(self.suggest_list[i].feature.place_type.includes('address')){
                            /* Selection has address ==> Update address fields */
                            self.showHideAddressDetailsFields(true, false);
                            console.log("self.suggest_list[i].feature");
                            console.log(self.suggest_list[i].feature);
                            self.updateAddressFields(self.suggest_list[i].feature);
                        } else {
                            self.showHideAddressDetailsFields(false, true);
                            self.setLocationPropertiesEmpty();
                        }
                    }
                }
            });
        },
        
        updateAddressFields(feature){
            console.log('updateAddressField');

            let properties_for_update = new Object();

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
            properties_for_update.street = address_arr[0];

            /*
             * Split the string into suburb, state and postcode
             */
            let reg = /^([a-zA-Z0-9\s]*)\s(New South Wales|Queensland|South Australia|Tasmania|Victoria|Western Australia|Northern Territory|Australian Capital Territory){1}\s+(\d{4})$/gi;
            let result = reg.exec(address_arr[1]);

            /* suburb */
            properties_for_update.town_suburb = result[1].trim();

            /* state */
            let state_abbr = state_abbr_list[result[2].trim()]
            properties_for_update.state = state_abbr;

            /* postcode */
            properties_for_update.postcode = result[3].trim();

            /* country */
            properties_for_update.country = 'Australia';

            /* update Vuex */
            this.setLocationProperties(properties_for_update);
        },
        moveMapCentre: function(coordinates){
            let self = this;
            let view = self.map.getView();
            view.animate({
                center: fromLonLat(coordinates),
                zoom: 14,
                duration: 1000
            });
        },
        setBaseLayer: function(selected_layer_name){
            this.map.getLayers().forEach(function(layer){
                if (layer.type == 'TILE')
                {
                    if (layer.get('name') == selected_layer_name){
                        layer.setVisible(true);
                    }
                    else {
                        layer.setVisible(false);
                    }
                }
            });
            if (selected_layer_name == 'sat') {
                $('#basemap_sat').hide();
                $('#basemap_osm').show();
            }
            else {
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
        addGeocoder: function(){
            console.log(Geocoder);
            var geocoder = new Geocoder('nominatim', {
                provider: 'osm',
                lang: 'en',
                placeholder: 'Search for ...',
                targetType: 'text-input',
                limit: 5,
                debug: true,
                autoComplete: true,
                autoCompleteMinlength: 2,
                keepOpen: true
            });
            this.map.addControl(geocoder);

            var self = this;  // Create a new variable to access data inside the function below.

            geocoder.on('addresschosen', function(evt){
                console.log(evt);
                var layerAdded = geocoder.getLayer();
                console.log(layerAdded);
                self.map.removeLayer(layerAdded);
            });
        },
        /* this function retrieve the coordinates from vuex and applys it to the marker */
        refreshMarkerLocation: function(){
            if (this.call_email.location.geometry.coordinates.length > 0) {
                this.feature_marker.getGeometry().setCoordinates(
                    transform([this.call_email.location.geometry.coordinates[0], this.call_email.location.geometry.coordinates[1]], 'EPSG:4326', 'EPSG:3857')
                );
                this.reverseGeocoding(this.call_email.location.geometry);
            } 
        },
        addMarker: function(){
            var iconFeature = new Feature({
                geometry: new Point(transform([
                    null, null
                    ], 'EPSG:4326', 'EPSG:3857')),
                });
            this.feature_marker = iconFeature;

            var iconStyle = new Style({
                image: new Icon({
                    anchor: [16, 32],
                    anchorXUnits: 'pixels',
                    anchorYUnits: 'pixels',
                    opacity: 1,
                    src: pin,
                    scale: 1
                })
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

        initMap: function(){
            this.projection = get('EPSG:3857');
            this.matrixSet = 'mercator';

            this.projectionExtent = this.projection.getExtent();
            var size = getWidth(this.projectionExtent) / 256;
            this.matrixSet = 'mercator';
            this.resolutions = new Array(21);
            this.matrixIds = new Array(21);
            for (var z = 0; z < 21; ++z) {
                // generate resolutions and matrixIds arrays for this WMTS
                this.resolutions[z] = size / Math.pow(2, z);
                this.matrixIds[z] = this.matrixSet + ':' + z;
            }
            var tileGrid = new tilegridWMTS({
                origin: getTopLeft(this.projectionExtent),
                resolutions: this.resolutions,
                matrixIds: this.matrixIds
            });

            var rasterLayer = new TileLayer({source: new OSM()});
            var rasterLayerSat = new TileLayer({
                    source: new WMTS({
                        url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                        format: 'image/png',
                        layer: 'public:mapbox-satellite',
                        matrixSet: this.matrixSet,
                        projection: this.projection,
                        tileGrid: tileGrid
                    })
            });
            rasterLayer.set('name', 'osm');
            rasterLayerSat.set('name', 'sat');
            rasterLayer.set('button_id', 'basemap_osm');
            rasterLayerSat.set('button_id', 'basemap_satellite');

            this.map = new Map({
                controls: defaultControls().extend([
                    new ScaleLine({
                        units: 'metric'
                    })
                ]),
                target: 'mapOL',
                layers: [
                    rasterLayer,
                    rasterLayerSat,
                ],
                view: new View({
                    center: [0, 0],
                    zoom: 5
                })
            });
            this.map.getView().setCenter(this.defaultCenter);
            this.map.on('click', this.mapClickHandler);

            this.element = document.getElementById('popup');

            this.popup = new Overlay({
                element: this.element,
                positioning: 'bottom-center',
                stopEvent: false,
                offset: [0, -25]
            });
            this.map.addOverlay(this.popup);
        },
        getMarkerAddress: function(){

        },
        /* this function stores the coordinates into the vuex, then call refresh marker function */
        relocateMarker: function(coords_3857){ 
            let coords_4326 = transform([coords_3857[0], coords_3857[1]], 'EPSG:3857', 'EPSG:4326');
            this.setLocationPoint(coords_4326);
            this.refreshMarkerLocation();
            this.reverseGeocoding(coords_4326);
        },
        relocateMarker4326: function(coords_4326){
            this.relocateMarker(transform([coords_4326[0], coords_4326[1]], 'EPSG:4326', 'EPSG:3857'));
        },
        mapClickHandler: function(e){
            var coordinate = e.coordinate;
            console.debug(coordinate);

            var lnglat_4326 = transform([coordinate[0], coordinate[1]], 'EPSG:3857', 'EPSG:4326')

            var feature = this.map.forEachFeatureAtPixel(e.pixel,
                function(feature) {
                    return feature;
            });
            if (feature) {
                /* User clicked on a feature, such as a marker */
                var coordinates = feature.getGeometry().getCoordinates();
                this.popup.setPosition(coordinates);
                $(this.element).popover({
                    placement: 'top',
                    html: true,
                    content: '<p>' 
                    + this.call_email.location.properties.street + ' ' + this.call_email.location.properties.town_suburb + '<br />'
                    + this.call_email.location.properties.state + ' ' + this.call_email.location.properties.postcode + ' ' + this.call_email.location.properties.country 
                    + '</p>',
                });
                $(this.element).popover('show');
            } else {
                /* User clicked on a map, not on any feature */
                if(!this.marker_locked){
                    this.relocateMarker(coordinate);
                }
                $(this.element).popover('destroy');
            };
        }
    },
}
</script>

<style lang="css">
#mapOL {
    position: relative;
    height: 500px;
}
.popover {
    position: relative;
}
#search-box {
    position: absolute;
    z-index: 1000;
    top: 10px;
    left: 50px;
}
#search-input {
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