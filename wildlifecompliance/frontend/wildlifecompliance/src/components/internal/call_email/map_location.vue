<template lang="html">
    <div class="container">
        <div id="mapOL">
            <div id="search-box">
                <input id="search-input" />
            </div>

            <div id="basemap-button">
                <img id="basemap_sat" src="../../../assets/img/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                <img id="basemap_osm" src="../../../assets/img/map_icon.png" @click="setBaseLayer('osm')" />
            </div>
        </div>

        <div style="display: none;">
            <div id="popup"></div>
        </div>

        <div class="col-sm-12"><div class="row">
            <label class="col-sm-2">Lock Marker Location</label>
            <input type="checkbox" v-model="marker_locked" />
        </div></div>


        <div id="lon">Lat: {{ lat_4326_cursor }}</div>
        <div id="lon">Lng: {{ lng_4326_cursor }}</div>
        {{ call_email.location.geometry.coordinates }}
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
//import Geocoder from 'ol-geocoder/dist/ol-geocoder.js';
//import pin_gray from '../../../assets/map_pins/pin_gray.png';

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
            lat_4326_cursor: null,
            lng_4326_cursor: null,
            marker_locked: false,
            base_layer: 'osm',
            awe: null,
            suggest_list: [],

            feature_marker: null,
            //lat_4326: -32,
            //lng_4326: 121,
            country: null,
            postcode: null,
            state: null,
            street: null,
            town_suburb: null,
        };
    },
    computed: {
    
    ...mapGetters('callemailStore', {
      call_email: 'call_email',
      //call_coordinates: 'call_coordinates',
    }),
    /*
    ...mapState('callemailStore', {
        call_email: state => state.call_email,

    }),
    */
    },
    mounted: function(){
        console.debug('Start loading map');
        //this.importMapData();
        this.initLocation();
        this.$nextTick();
        this.initMap();
        this.setBaseLayer('osm');
        this.initAwesomplete();
        this.addMarker();
        console.debug('End loading map');
    },

    methods: {
        ...mapActions('callemailStore', {
            saveLocation: 'saveLocation',
            setLocationPoint: 'setLocationPoint',
        }),
        initLocation: function() {
            console.log("initLocation");
            console.log(this.dummyPoint);
            if (this.call_email.location.geometry.coordinates == null) {
                this.setLocationPoint(this.dummyPoint);
            }
        },
        saveInstanceLocation: async function() {
            await this.$nextTick();
            this.saveLocation();
        },
        search: function(place){
            var self = this;

            var centre = toLonLat(this.map.getView().getCenter());
            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+encodeURIComponent(place)+'.json?'+ $.param({
                    country: 'au',
                    proximity: ''+centre[0]+','+centre[1],
                    bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
                    types: 'region,postcode,place,locality,neighborhood,address'
                }),
                dataType: 'json',
                success: function(data, status, xhr) {
                    self.suggest_list = [];
                    if (data.features && data.features.length > 0){
                        for (var i = 0; i < data.features.length; i++){
                            self.suggest_list.push({ label: data.features[i].place_name, value: data.features[i].place_name, geometry: data.features[i].geometry });
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
                for (var i=0; i<self.suggest_list.length; i++){
                    if (self.suggest_list[i].value == ev.target.value){

                        self.moveMapCentre(self.suggest_list[i].geometry.coordinates);
                    }
                }
            });
        },
        moveMapCentre: function(coordinates){
            var self = this;
            var view = self.map.getView();
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
            if (selected_layer_name == 'sat')
            {
                $('#basemap_osm').show();
                $('#basemap_sat').hide();
            }
            else
            {
                $('#basemap_osm').hide();
                $('#basemap_sat').show();
            }
        },
        /*
        importMapData: function(){
            this.$http.get("http://ubuntu-18:8071/api/call_email_location/7/")
            .then((response)=>{
                console.log(response.data);
                var geojson = response.data;
                this.lat_4326 = geojson.geometry.coordinates[1];
                this.lng_4326 = geojson.geometry.coordinates[0];
                this.country = geojson.properties.country;
                this.postcode = geojson.properties.postcode;
                this.state = geojson.properties.state;
                this.street = geojson.properties.street;
                this.town_suburb = geojson.properties.town_suburb;
                this.addMarker();
                //this.addGeocoder();
            })
            .catch((response)=>{
                console.log(response);
            });
        },
        */
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
        addMarker: function(){
            console.log(this.call_email);
             var iconFeature = new Feature({
               geometry: new Point(transform([
                   //this.call_coordinates[1], 
                   //this.call_coordinates[0], 
                   this.call_email.location.geometry.coordinates[1], 
                   this.call_email.location.geometry.coordinates[0], 
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
        relocateMarker: function(coordinates){
            this.feature_marker.getGeometry().setCoordinates(coordinates);
            this.setLocationPoint(coordinates);
        },
        mapClickHandler: function(e){
            var coordinate = e.coordinate;
            console.debug(coordinate);
            this.lng_4326_cursor = coordinate[0];
            this.lat_4326_cursor = coordinate[1];

            var lnglat_4326 = transform([coordinate[0], coordinate[1]], 'EPSG:3857', 'EPSG:4326')
            this.lng_4326_cursor = lnglat_4326[0];
            this.lat_4326_cursor = lnglat_4326[1];

            var feature = this.map.forEachFeatureAtPixel(e.pixel,
                function(feature) {
                    return feature;
            });
            if (feature) {
                var coordinates = feature.getGeometry().getCoordinates();
                this.popup.setPosition(coordinates);
                $(this.element).popover({
                    placement: 'top',
                    html: true,
                    content: '<p>' + this.street + ' ' + this.town_suburb + '<br />' + this.state + ' ' + this.postcode + ' ' + this.country + '</p>',
                });
                $(this.element).popover('show');
            } else {
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
    height: 400px;
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
</style>