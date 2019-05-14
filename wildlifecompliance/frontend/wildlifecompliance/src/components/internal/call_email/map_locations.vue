<template lang="html">
    <div class="">
        <div id="map-wrapper">
            <div id="search-box">
                <input id="search-input" />
            </div>
            <div id="mapLeaf"> </div>
            <div id="basemap-button">
                <img id="basemap_sat" src="../../../assets/img/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                <img id="basemap_osm" src="../../../assets/img/map_icon.png" @click="setBaseLayer('osm')" />
            </div>
        </div>
    </div>
</template>

<script>
import L from 'leaflet';
import { api_endpoints, helpers } from '@/utils/hooks'
import 'leaflet.markercluster';  /* This should be imported after leaflet */
import Awesomplete from 'awesomplete';

import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';

L.TileLayer.WMTS = L.TileLayer.extend({
    defaultWmtsParams: {
        service: 'WMTS',
        request: 'GetTile',
        version: '1.0.0',
        layers: '',
        styles: '',
        tilematrixSet: '',
        format: 'image/jpeg'
    },

    initialize: function (url, options) { // (String, Object)
        this._url = url;
        var wmtsParams = L.extend({}, this.defaultWmtsParams);
        var tileSize = options.tileSize || this.options.tileSize;
        if (options.detectRetina && L.Browser.retina) {
            wmtsParams.width = wmtsParams.height = tileSize * 2;
        } else {
            wmtsParams.width = wmtsParams.height = tileSize;
        }
        for (var i in options) {
            // all keys that are not TileLayer options go to WMTS params
            if (!this.options.hasOwnProperty(i) && i!="matrixIds") {
                wmtsParams[i] = options[i];
            }
        }
        this.wmtsParams = wmtsParams;
        this.matrixIds = options.matrixIds||this.getDefaultMatrix();
        L.setOptions(this, options);
    },

    onAdd: function (map) {
        this._crs = this.options.crs || map.options.crs;
        L.TileLayer.prototype.onAdd.call(this, map);
    },

    getTileUrl: function (coords) { // (Point, Number) -> String
        var tileSize = this.options.tileSize;
        var nwPoint = coords.multiplyBy(tileSize);
        nwPoint.x+=1;
        nwPoint.y-=1;
        var sePoint = nwPoint.add(new L.Point(tileSize, tileSize));
        var zoom = this._tileZoom;
        var nw = this._crs.project(this._map.unproject(nwPoint, zoom));
        var se = this._crs.project(this._map.unproject(sePoint, zoom));
        var tilewidth = se.x-nw.x;
        //zoom = this._map.getZoom();
        var ident = this.matrixIds[zoom].identifier;
        var tilematrix = this.wmtsParams.tilematrixSet + ":" + ident;
        var X0 = this.matrixIds[zoom].topLeftCorner.lng;
        var Y0 = this.matrixIds[zoom].topLeftCorner.lat;
        var tilecol=Math.floor((nw.x-X0)/tilewidth);
        var tilerow=-Math.floor((nw.y-Y0)/tilewidth);
        var url = L.Util.template(this._url, {s: this._getSubdomain(coords)});
        return url + L.Util.getParamString(this.wmtsParams, url) + "&tilematrix=" + tilematrix + "&tilerow=" + tilerow +"&tilecol=" + tilecol;
        /*
        var tileBounds = this._tileCoordsToBounds(coords);
        var zoom = this._tileZoom;
        var nw = this._crs.project(tileBounds.getNorthWest());
        var se = this._crs.project(tileBounds.getSouthEast());
        var tilewidth = se.x-nw.x;
        var ident = this.matrixIds[zoom].identifier;
        var X0 = this.matrixIds[zoom].topLeftCorner.lng;
        var Y0 = this.matrixIds[zoom].topLeftCorner.lat;
        var tilecol=Math.floor((nw.x+1-X0)/tilewidth);
        var tilerow=-Math.floor((nw.y-1-Y0)/tilewidth);
        var url = L.Util.template(this._url, {s: this._getSubdomain(coords)});
        console.log(L.Util.getParamString(this.wmtsParams, url) + "&tilematrix=" + ident + "&tilerow=" + tilerow +"&tilecol=" + tilecol );
        return url + L.Util.getParamString(this.wmtsParams, url) + "&tilematrix=" + ident + "&tilerow=" + tilerow +"&tilecol=" + tilecol ;
        */
    },

    setParams: function (params, noRedraw) {
        L.extend(this.wmtsParams, params);
        if (!noRedraw) {
            this.redraw();
        }
        return this;
    },
    
    getDefaultMatrix : function () {
        /**
         * the matrix3857 represents the projection 
         * for in the IGN WMTS for the google coordinates.
         */
        var matrixIds3857 = new Array(22);
        for (var i= 0; i<22; i++) {
            matrixIds3857[i]= {
                identifier    : "" + i,
                topLeftCorner : new L.LatLng(20037508.3428,-20037508.3428)
            };
        }
        return matrixIds3857;
    }
});
L.tileLayer.wmts = function (url, options) {
    return new L.TileLayer.WMTS(url, options);
};

/* To make default marker work with webpack */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});
/********************************************/

module.exports = {
    data: function(){
        return {
            map: null,
            tileLayer: null,
            tileLayerSat: null,
            layers: [],
            popup: null,
            opt_url : helpers.add_endpoint_json(api_endpoints.call_email, "optimised"),
        }
    },
    mounted(){
        this.initMap();
        this.addMarkers();
        this.initAwesomplete();
    },
    methods: {
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
                    }
                }
                return false;
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
        onClick(e){
            console.log(e.latlng.toString());
        },
        initMap(){
            console.log('Start initMap()');

            this.map = L.map('mapLeaf').setView([-24.9505, 122.8605], 5);
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

            this.popup = L.popup();
            this.map.on('click', this.onClick);
            this.setBaseLayer('osm');
        },
        addMarkers(){
            let self = this;
            var markers = L.markerClusterGroup();

            console.log(this.opt_url);

            $.ajax({
                url: this.opt_url,
                dataType: 'json',
                success: function(data, status, xhr){
                    if (data && data.length > 0){
                        for (var i = 0; i < data.length; i++){
                            if(data[i].location){
                                let call_email = data[i];
                                let coords = call_email.location.geometry.coordinates;

                                /* Select a marker file, according to the classification */
                                let filename = 'marker-gray-locked.svg';
                                if (call_email.classification){
                                    if (call_email.classification.id == 1){
                                        filename = 'marker-yellow-locked.svg';
                                    } else if (call_email.classification.id == 2){
                                        filename = 'marker-green-locked.svg';
                                    } else if (call_email.classification.id == 3){
                                        filename = 'marker-red-locked.svg';
                                    }
                                }

                                /* create marker */
                                let myIcon = L.icon({
                                    iconUrl: require('../../../assets/' + filename),
                                    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
                                    shadowSize: [41, 41],
                                    shadowAnchor: [12, 41],
                                    iconSize: [32, 32],
                                    iconAnchor: [16, 32],
                                    popupAnchor: [0, -20]
                                });
                                let myMarker = L.marker([coords[1], coords[0]], {icon: myIcon});
                                let myPopup = L.popup();
                                myMarker.bindPopup(myPopup);
                                markers.addLayer(myMarker);

                                /* dynamically construct content of the popup */
                                myMarker.on('click', (ev)=>{
                                    let popup = ev.target.getPopup();
                                    self.$http.get('/api/call_email/' + call_email.id).then(response => {
                                        let call_email = response.body;
                                        popup.setContent(self.construct_content(call_email, coords));
                                    });
                                })
                            }
                        }
                        self.map.addLayer(markers);
                    }
                }
            });
        },
        construct_content: function (call_email, coords){
            let classification_str = '---';
            if (call_email.classification){
                classification_str = call_email.classification.name;
            }

            let report_type_str = '---';
            if (call_email.report_type){
                report_type_str = call_email.report_type.report_type;
            }

            let content = '<div class="popup-title popup-title-top">Classification</div>'
                        + '<div class="popup-coords">'
                        + classification_str
                        + '</div>'

            content    += '<div class="popup-title">Report Type</div>'
                        + '<div class="popup-address">'
                        + report_type_str
                        + '</div>'

            
            if (call_email.location.properties.street){
                content += '<div class="popup-title">Address</div>'
                + '<div class="popup-address">'
                + call_email.location.properties.street + '<br />'
                + call_email.location.properties.town_suburb + '<br />'
                + call_email.location.properties.state + '<br />'
                + call_email.location.properties.postcode
                + '</div>'

            }else{
                content += '<div class="popup-title">Details</div>'
                + '<div class="popup-address">'
                + call_email.location.properties.details.substring(0, 10)
                + '</div>'
            }

            content += '<div class="popup-link">'
                + '<a href="call_email/' + call_email.id + '">View</a>'
                + '</div>';

            return content;
        }
    },
}
</script>

<style lang="css">
#map-wrapper {
    position: relative;
}
#mapLeaf {
    position: relative;
    height: 800px;
    margin-bottom: 50px;
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
.popup-title {
    padding: 5px 5px 5px 10px;
    background: gray;
    font-size: 1.3em;
    font-weight: bold;
    color: white;
}
.popup-title-top {
    border-radius: 12px 12px 0 0;
}
.popup-coords {
    padding: 10px;
}
.popup-address {
    padding: 10px;
}
.popup-link {
    text-align: center;
    font-size: 1.2em;
    padding: 10px;
}
.leaflet-popup-content {
    margin: 0px !important;
}
.leaflet-popup-content-wrapper {
    padding: 0px !important;
}
</style>
