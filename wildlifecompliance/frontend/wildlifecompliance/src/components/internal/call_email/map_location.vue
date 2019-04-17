<template lang="html">
    <div class="container">
        <div id="mapOL"></div>
    </div>
</template>

<script>
import 'ol/ol.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import { defaults as defaultControls, ScaleLine} from 'ol/control.js';
import TileLayer from 'ol/layer/Tile.js';
import OSM from 'ol/source/OSM';
import BingMaps from 'ol/source/BingMaps';
import {addProjection, addCoordinateTransforms, transform} from 'ol/proj.js';


export default {
    name: "map-openlayers",
    data: function(){

    },
    mounted: function(){
        var coords = transform([10.0, 10.0], 'EPSG:4326', 'EPSG:3857');

        let map = new Map({
            controls: defaultControls().extend([
                new ScaleLine({
                    units: 'metric'
                })
            ]),
            target: 'mapOL',
            layers: [
                new TileLayer({source: new OSM()}),
                //new TileLayer({source: new BingMaps()}),
            ],
            view: new View({
                center: [0, 0],
                zoom: 5
            })
        });
        map.getView().setCenter(transform([114.85, -29.714], 'EPSG:4326', 'EPSG:3857'));
    },

    methods: {

    },
}
</script>

<style lang="css">
#mapOL {
    height: 400px;
}
</style>
