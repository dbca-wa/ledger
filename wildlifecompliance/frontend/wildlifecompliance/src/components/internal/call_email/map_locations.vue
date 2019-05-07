
<template lang="html">
    <div>
        <div id="mapOL">
        </div>
    </div>
</template>

<script>
import pin from '../../../assets/pin.svg';
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
    name: "map-openlayers-dashboard",
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
    mounted: function(){
        console.debug('Start loading map');
        this.initMap();
        this.setBaseLayer('osm');
        this.addMarker();
        console.debug('End loading map');
    },

    methods: {
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
            if (selected_layer_name == 'sat') {
                $('#basemap_sat').hide();
                $('#basemap_osm').show();
            }
            else {
                $('#basemap_osm').hide();
                $('#basemap_sat').show();
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