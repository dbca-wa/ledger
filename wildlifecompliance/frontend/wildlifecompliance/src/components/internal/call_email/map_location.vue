<template lang="html">
    <div class="container">
        <div id="mapOL"><div id="popup"></div></div>
        <div id="lon">Lat: {{ lat_4326 }}</div>
        <div id="lon">Lng: {{ lng_4326 }}</div>
    </div>
</template>

<script>
import MapData from './map_location_store.js';
import 'ol/ol.css';
import 'bootstrap/dist/css/bootstrap.css';
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

export default {
    name: "map-openlayers",
    data: function(){
        return {
            defaultCenter: MapData.data.defaultCenter,
            item: MapData.data.item,
            projection: null,
            map: null,
            popup: null,
            element: null,
            lat_4326: null,
            lng_4326: null,
        };
    },
    mounted: function(){
        console.debug('Start loading map');
        this.initMap();
        console.debug('End loading map');
    },

    methods: {
        initMap: function(){
            console.debug(MapData);

            this.projection = get('EPSG:3857');

            var rasterLayer = new TileLayer({source: new OSM()});

            var iconFeature = new Feature({
               geometry: new Point(transform([this.item.location.lng, this.item.location.lat], 'EPSG:4326', 'EPSG:3857')),
               name: 'Null Island',
               description: this.item.description,
               population: 4000,
               rainfall: 500
             });

             var iconStyle = new Style({
               image: new Icon(/** @type {module:ol/style/Icon~Options} */ ({
                 anchor: [0.5, 46],
                 anchorXUnits: 'fraction',
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

            this.map = new Map({
                controls: defaultControls().extend([
                    new ScaleLine({
                        units: 'metric'
                    })
                ]),
                target: 'mapOL',
                layers: [
                    rasterLayer,
                    vectorLayer,
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
                offset: [0, 50]
            });
            this.map.addOverlay(this.popup);
        },

        mapClickHandler: function(e){
            var coordinate = e.coordinate;
            console.debug(coordinate);
            //this.lng = coordinate[0];
            //this.lat = coordinate[1];

            var lnglat_4326 = transform([coordinate[0], coordinate[1]], 'EPSG:3857', 'EPSG:4326')
            this.lng_4326 = lnglat_4326[0];
            this.lat_4326 = lnglat_4326[1];

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
                    content: feature.get('name')
                });
                $(this.element).popover('show');
            } else {
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
</style>
