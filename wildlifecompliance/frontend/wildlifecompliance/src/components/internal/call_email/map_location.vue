<template lang="html">
    <div class="container">
        <div id="map" class="map"></div>
    </div>
</template>

<script>
var L = require('leaflet');
module.exports = {
    data: function(){
        return {
            map: null,
            tileLayer: null,
            layers: [],
        }
    },
    mounted(){
        this.initMap();
        this.initLayers();
    },
    methods: {
        initMap() {
            this.map = L.map('map').setView([38.63, -90.23], 12);
            this.tileLayer = L.tileLayer(
                'https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}.png',
                {
                    maxZoom: 18,
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
                } 
            );
            this.tileLayer.addTo(this.map);
        },
        initLayers(){

        },
    },
}
</script>

<style lang="css">
.map { 
    height: 400px; 
    width: 400px; 
}
</style>