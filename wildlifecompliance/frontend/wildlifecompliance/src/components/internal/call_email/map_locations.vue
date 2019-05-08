<template lang="html">
    <div class="container">
        <div id="map">
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
import pin from '../../../assets/pin.svg';
import 'leaflet.markercluster';  /* This should be imported after leaflet */

import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

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
        }
    },
    created() {
            this.vars = {
                    pin_green: '<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="32" height="32" viewBox="0 0 32 32.000001" id="svg4513" version="1.1" inkscape:version="0.92.1 r" sodipodi:docname="pin.svg"> <defs id="defs4515" /> <sodipodi:namedview id="base" pagecolor="#ffffff" bordercolor="#666666" borderopacity="1.0" inkscape:pageopacity="0.0" inkscape:pageshadow="2" inkscape:zoom="1" inkscape:cx="-213.23428" inkscape:cy="-88.560157" inkscape:document-units="px" inkscape:current-layer="layer1" showgrid="true" units="px" inkscape:window-width="1452" inkscape:window-height="1093" inkscape:window-x="281" inkscape:window-y="81" inkscape:window-maximized="0" inkscape:snap-global="true"> <inkscape:grid type="xygrid" id="grid5061" /> </sodipodi:namedview> <metadata id="metadata4518"> <rdf:RDF> <cc:Work rdf:about=""> <dc:format>image/svg+xml</dc:format> <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage" /> <dc:title /> </cc:Work> </rdf:RDF> </metadata> <g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1" transform="translate(0,-1020.3622)"> <g id="g3726" transform="translate(-33)"> <path transform="translate(0,1020.3622)" sodipodi:nodetypes="csccccc" inkscape:connector-curvature="0" id="path3680" d="M 61,12 C 61,5.372583 55.627417,0 49,0 42.372583,0 37,5.372583 37,12 c 0.0053,2.513648 0.799861,4.962162 2.260742,7 L 49,32 58.742185,19 C 60.203913,16.961457 60.996382,14.513003 61,12 Z" style="fill:#4e9a06;fill-opacity:1;stroke:none;stroke-width:1.26315784" /> <path id="path3680-3" transform="translate(0,1020.3622)" d="m 49,0.98046875 c -6.096539,0 -11.018456,4.92127815 -11.019531,11.01757825 0.0049,2.3084 0.734093,4.557587 2.076172,6.429687 L 49,30.365234 57.945312,18.427734 C 59.287721,16.555634 60.015801,14.307 60.019531,12 60.019531,5.9028 55.097205,0.98046875 49,0.98046875 Z" style="fill:#8be233;fill-opacity:1;stroke:none;stroke-width:1.26315784" inkscape:connector-curvature="0" /> <circle r="6" cy="1032.3622" cx="49" id="path3704" style="fill:#4e9a06;fill-opacity:1;stroke:none;stroke-width:1.5" /> <circle r="5" cy="1032.3622" cx="49" id="path3704-6" style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:1.25" /> </g> </g> </svg>'
            }
    },
    mounted(){
        this.initMap();
        this.addMarkers();
    },
    methods: {
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

            this.popup = L.popup();
            this.map.on('click', this.onClick);
            this.setBaseLayer('osm');
        },
        addMarkers(){
            let self = this;
            var markers = L.markerClusterGroup();

            $.ajax({
                url: '/api/call_email_location/',
                dataType: 'json',
                success: function(data, status, xhr){
                    if (data.results && data.results.features && data.results.features.length > 0){
                        for (var i = 0; i < data.results.features.length; i++){
                            if(data.results.features[i].geometry){
                                let feature = data.results.features[i];
                                let coords = feature.geometry.coordinates;

                                /* create marker */
                                let myIcon = L.icon({
                                    iconUrl: 'data:image/svg+xml;base64,' + btoa(self.vars.pin_green),
                                    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),

                                    /* Accessing external file for now, but this should point to the local file */
                                    shadowSize: [41, 41],
                                    shadowAnchor: [12, 41],
                                    iconSize: [32, 32],
                                    iconAnchor: [16, 32],
                                    popupAnchor: [0, -20]
                                });
                                let myMarker = L.marker([coords[1], coords[0]], {icon: myIcon});

                                /* construct popup */
                                let myPopup = L.popup().setContent(
                                      '<div class="popup-coords">'
                                    + 'Lat: ' + coords[1] + '<br />'
                                    + 'Lng: ' + coords[0] 
                                    + '</div>'

                                    + '<div class="popup-address">'
                                    + feature.properties.street + '<br />'
                                    + feature.properties.town_suburb + '<br />'
                                    + feature.properties.state + '<br />'
                                    + feature.properties.postcode
                                    + '</div>'

                                    + '<div class="popup-link">'
                                    + '<a src="">Link (not implemented yet)</a>'
                                    + '</div>'
                                    );

                                myMarker.bindPopup(myPopup);
                                markers.addLayer(myMarker);
                            }
                        }
                        self.map.addLayer(markers);
                    }
                }
            });
        },
    },
}
</script>

<style lang="css">
#map {
    height: 700px;
    margin-bottom: 50px;
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
.popup-coords {
    margin: 10px;
}
.popup-address {
    margin: 10px;
}
.popup-link {
    margin: 10px;
}
</style>
