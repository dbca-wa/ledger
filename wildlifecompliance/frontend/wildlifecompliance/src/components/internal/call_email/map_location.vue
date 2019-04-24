<template lang="html">
    <div class="container">
        <div id="mapOL"></div>
        <div style="display: none;">
            <div id="popup"></div>
        </div>
        <div id="lon">Lat: {{ lat_4326_cursor }}</div>
        <div id="lon">Lng: {{ lng_4326_cursor }}</div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Street</label>
            <input v-model="street" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Town/Suburb</label>
            <input v-model="town_suburb" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">State</label>
            <input v-model="state" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Postcode</label>
            <input v-model="postcode" />
        </div></div>
        <div class="col-sm-12"><div class="row">
            <label class="col-sm-4">Contry</label>
            <input v-model="country" />
       </div></div>
    </div>
</template>

<script>
import MapData from './map_location_store.js';
import 'ol/ol.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import { defaults as defaultControls, ScaleLine} from 'ol/control.js';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer.js';
import { XYZ, OSM, WMTS } from 'ol/source';
import { get, addProjection, addCoordinateTransforms, transform } from 'ol/proj.js';
import Feature from 'ol/Feature.js';
import Overlay from 'ol/Overlay';
import Point from 'ol/geom/Point.js';
import VectorSource from 'ol/source/Vector.js';
import { Icon, Style } from 'ol/style.js';
import 'bootstrap/dist/css/bootstrap.css';

export default {
    name: "map-openlayers",
    data: function(){
        return {
            defaultCenter: MapData.data.defaultCenter,
            projection: null,
            map: null,
            popup: null,
            element: null,
            lat_4326_cursor: null,
            lng_4326_cursor: null,

            feature_marker: null,
            lat_4326: null,
            lng_4326: null,
            country: null,
            postcode: null,
            state: null,
            street: null,
            town_suburb: null,
        };
    },
    mounted: function(){
        console.debug('Start loading map');
        this.importMapData();
        this.initMap();
        console.debug('End loading map');
    },

    methods: {
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
            })
            .catch((response)=>{
                console.log(response);
            });
        },
        addMarker: function(){
             var iconFeature = new Feature({
               geometry: new Point(transform([this.lng_4326, this.lat_4326], 'EPSG:4326', 'EPSG:3857')),
             });
             this.feature_marker = iconFeature;

             var iconStyle = new Style({
               image: new Icon(/** @type {module:ol/style/Icon~Options} */ ({
                 anchor: [16, 32],
                 anchorXUnits: 'pixels',
                 anchorYUnits: 'pixels',
                 src: require('./pin_gray.png'),
               }))
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

            var rasterLayer = new TileLayer({source: new OSM()});


            this.map = new Map({
                controls: defaultControls().extend([
                    new ScaleLine({
                        units: 'metric'
                    })
                ]),
                target: 'mapOL',
                layers: [
                    rasterLayer,
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
                this.relocateMarker(coordinate);
                $(this.element).popover('destroy');
            };
        }
    },
}
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
