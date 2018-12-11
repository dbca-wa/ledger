<template lang="html">
<div  id="cg_attr" >
	<div v-show="!isLoading">
		<form id="attForm">
		<div class="col-sm-12">
			<alert :show.sync="showUpdate" type="success" :duration="7000">
				<p>Mooring successfully updated</p>
			</alert>
			<alert :show.sync="showError" type="danger">
				<p>{{errorString}}<p/>
			</alert>
					<div class="row">
						<div class="col-lg-12">
                            <div class="row">
                                <div class="col-sm-12 features">
                                    <div>
                                        <div id="map" class="map" style='height:80%'>
                                        </div>
                                        <input type='hidden' value='' iname='location_coordinates' id='location_coordinates'>
                                        <input type='hidden' value='Point' name='type' id='type'>
                                        <div class="col-lg-12" style="margin-top:20px;">
                                            <div class="col-lg-6">
                                                <div class="form-group">
                                                    <label class="control-label">Longitude</label>
                                                    <input type='text' name='longitude' id='longitude' class="form-control" v-on:change="setCoordinates()"> 
                                                </div>
                                            </div>
                                            <div class="col-lg-6">
                                                <div calss="form-group">
                                                    <label class="control-label">Latitude</label>
                                                    <input type='text' name='latitude' id='latitude' class="form-control" v-on:change="setCoordinates()">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top: 40px;display:none;">
                                <div class="col-md-12">
                                    <div class="form-group">
                                        <label class="control-label" >Description</label>
                                        <div id="editorhidden" class="form-control"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top:20px;">
                                <div class="col-sm-8">
                                </div>
                                <div class="col-sm-4">
                                    <div class="col-sm-12">
                                        <div class="form-group pull-right">
                                            <a href="#" v-if="createCampground" class="btn btn-primary" @click.prevent="create">Create</a>
                                            <a href="#" v-else class="btn btn-primary" @click.prevent="update">Update</a>
                                            <a href="#" class="btn btn-default" @click.prevent="goBack">Cancel</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

			</form>
		</div>
		<loader :isLoading.sync="isLoading">Loading...</loader>
	</div>
</template>
<style>
.alert{
    display:none;
    height:30px;
    line-height:30px;
    padding:7px 9px;
}
.ol-box{box-sizing:border-box;border-radius:2px;border:2px solid #00f}.ol-mouse-position{top:8px;right:8px;position:absolute}.ol-scale-line{background:rgba(0,60,136,.3);border-radius:4px;bottom:8px;left:8px;padding:2px;position:absolute}.ol-scale-line-inner{border:1px solid #eee;border-top:none;color:#eee;font-size:10px;text-align:center;margin:1px;will-change:contents,width}.ol-overlay-container{will-change:left,right,top,bottom}.ol-unsupported{display:none}.ol-unselectable,.ol-viewport{-webkit-touch-callout:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent}.ol-selectable{-webkit-touch-callout:default;-webkit-user-select:auto;-moz-user-select:auto;-ms-user-select:auto;user-select:auto}.ol-grabbing{cursor:-webkit-grabbing;cursor:-moz-grabbing;cursor:grabbing}.ol-grab{cursor:move;cursor:-webkit-grab;cursor:-moz-grab;cursor:grab}.ol-control{position:absolute;background-color:rgba(255,255,255,.4);border-radius:4px;padding:2px}.ol-control:hover{background-color:rgba(255,255,255,.6)}.ol-zoom{top:.5em;left:.5em}.ol-rotate{top:.5em;right:.5em;transition:opacity .25s linear,visibility 0s linear}.ol-rotate.ol-hidden{opacity:0;visibility:hidden;transition:opacity .25s linear,visibility 0s linear .25s}.ol-zoom-extent{top:4.643em;left:.5em}.ol-full-screen{right:.5em;top:.5em}@media print{.ol-control{display:none}}.ol-control button{display:block;margin:1px;padding:0;color:#fff;font-size:1.14em;font-weight:700;text-decoration:none;text-align:center;height:1.375em;width:1.375em;line-height:.4em;background-color:rgba(0,60,136,.5);border:none;border-radius:2px}.ol-control button::-moz-focus-inner{border:none;padding:0}.ol-zoom-extent button{line-height:1.4em}.ol-compass{display:block;font-weight:400;font-size:1.2em;will-change:transform}.ol-touch .ol-control button{font-size:1.5em}.ol-touch .ol-zoom-extent{top:5.5em}.ol-control button:focus,.ol-control button:hover{text-decoration:none;background-color:rgba(0,60,136,.7)}.ol-zoom .ol-zoom-in{border-radius:2px 2px 0 0}.ol-zoom .ol-zoom-out{border-radius:0 0 2px 2px}.ol-attribution{text-align:right;bottom:.5em;right:.5em;max-width:calc(100% - 1.3em)}.ol-attribution ul{margin:0;padding:0 .5em;font-size:.7rem;line-height:1.375em;color:#000;text-shadow:0 0 2px #fff}.ol-attribution li{display:inline;list-style:none;line-height:inherit}.ol-attribution li:not(:last-child):after{content:" "}.ol-attribution img{max-height:2em;max-width:inherit;vertical-align:middle}.ol-attribution button,.ol-attribution ul{display:inline-block}.ol-attribution.ol-collapsed ul{display:none}.ol-attribution.ol-logo-only ul{display:block}.ol-attribution:not(.ol-collapsed){background:rgba(255,255,255,.8)}.ol-attribution.ol-uncollapsible{bottom:0;right:0;border-radius:4px 0 0;height:1.1em;line-height:1em}.ol-attribution.ol-logo-only{background:0 0;bottom:.4em;height:1.1em;line-height:1em}.ol-attribution.ol-uncollapsible img{margin-top:-.2em;max-height:1.6em}.ol-attribution.ol-logo-only button,.ol-attribution.ol-uncollapsible button{display:none}.ol-zoomslider{top:4.5em;left:.5em;height:200px}.ol-zoomslider button{position:relative;height:10px}.ol-touch .ol-zoomslider{top:5.5em}.ol-overviewmap{left:.5em;bottom:.5em}.ol-overviewmap.ol-uncollapsible{bottom:0;left:0;border-radius:0 4px 0 0}.ol-overviewmap .ol-overviewmap-map,.ol-overviewmap button{display:inline-block}.ol-overviewmap .ol-overviewmap-map{border:1px solid #7b98bc;height:150px;margin:2px;width:150px}.ol-overviewmap:not(.ol-collapsed) button{bottom:1px;left:2px;position:absolute}.ol-overviewmap.ol-collapsed .ol-overviewmap-map,.ol-overviewmap.ol-uncollapsible button{display:none}.ol-overviewmap:not(.ol-collapsed){background:rgba(255,255,255,.8)}.ol-overviewmap-box{border:2px dotted rgba(0,60,136,.7)}.ol-overviewmap .ol-overviewmap-box:hover{cursor:move}

</style>

<script>
import {
    $,
    api_endpoints,
    helpers,
    validate
}
from '../../hooks.js'
import {
    bus,
    select2
}
from '../utils/eventBus.js';
import OpenLayers from 'openlayers';
import ol from 'openlayers';
import Editor from 'quill';
import Render from 'quill-render';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
import {mapGetters} from 'vuex'
export default {
    name: 'cg_attr',
    components: {
        alert,
        loader,
    },
    data: function() {
        let vm = this;
        return {
            editor: null,
            editor_updated: false,
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            reload : false,
            features_selected: [],
        }
    },
    props: {
        createCampground: {
            default: function() {
                return true;
            }
        },
        campground: {
            default: function() {
                return {
                    address: {},
                    images: []
                };
            },
            type: Object
        },
        loadingMap: {
            type: Boolean,
            default: function(){
                return false;
            }
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
 
    },
    watch: {
        loadingMap: {
            immediate: true,
            deep: true,
            handler: function(n, o){
                this.isLoading = n;
            }
        },
        campground: {
            handler: function() {
                // this.loadSelectedFeatures();
            },
            deep: true

        }
    },
    methods: {
		goBack: function() {
            helpers.goBack(this);
        },
        create: function() {
            console.log("CREATE");
            this.sendData(api_endpoints.campgrounds, 'POST');
        },
        update: function() {
            this.sendData(api_endpoints.campground(this.campground.id), 'PUT',true);
        },
        validateEditor: function(el){
            let vm = this;
			if (el.parents('.form-group').hasClass('has-error')) {
				el.tooltip("destroy");
				el.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
			}
            if (vm.editor.getText().trim().length == 0) {
                // add or update tooltips
                el.tooltip({
                        trigger: "focus"
                    })
                    .attr("data-original-title", 'Description is required')
                    .parents('.form-group').addClass('has-error');
                return false;
            }
            return true;
        },
        sendData: function(url, method, reload=false) {
            let vm = this;
            vm.isLoading =true;
            vm.reload = reload;
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "map");
        },
        showAlert: function() {
            bus.$emit('showAlert', 'alert1');
        },
        fetchCampground:function () {
            let vm =this;
            $.ajax({
                url: api_endpoints.campground(vm.$route.params.id),
                dataType: 'json',
                async: false,
                success: function(data, stat, xhr) {
                    vm.campground = data;
                    bus.$emit('campgroundFetched');
                    for (var i = 0; i < data.features.length; i++){
                        vm.features_selected.push(data.features[i].id);
                    }
                    vm.campground.features = vm.features_selected;
                    console.log("Features updated");
                    vm.$emit('updated', vm.campground);
                }
            });
        },
        setCoordinates: function() { 
		    console.log('gps changes');
            var longitude = $('#longitude').val();
		    var latitude = $('#latitude').val();
            $('#location_coordinates').val("POINT ("+longitude+" "+latitude+")");
            console.log("setCoordinates");
            console.log(this.campground.wkb_geometry);
            var coord = new Object();
            coord.coordinates = [parseFloat(longitude),parseFloat(latitude)];
            coord.type = "Point";
            this.campground.wkb_geometry = coord;
            console.log("NBEXT");
            console.log(this.campground.wkb_geometry);
	    }
    },
    mounted: function() {
        let vm = this;
        vm.fetchCampground();

        vm.editor = new Editor('#editorhidden', {
            modules: {
                toolbar: true
            },
            theme: 'snow'
        });
        // vm.editor.clipboard.dangerouslyPasteHTML(0, vm.campground.description, 'api');
        vm.editor.on('text-change', function(delta, oldDelta, source) {
            var text = $('#editorhidden >.ql-editor').html();
            vm.campground.description = text;
			vm.validateEditor($('#editorhidden'));
        });
        
        vm.form = $('#attForm');
        // Load Map Point Selection
        var raster = new ol.layer.Tile({
            source: new ol.source.OSM({noWrap: true, wrapX: false,})
        });


//       var raster = new ol.layer.Tile({
//             source: new ol.source.WMTS({
//                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
//                format: 'image/png',
//                layer: 'public:mapbox-streets',
//		})
//       });

var iconFeature = null;
var lat = 0;
var lon = 0;
if (vm.campground.wkb_geometry) {
    console.log("GSPPP");
    console.log(vm.campground.wkb_geometry);
    if (vm.campground.wkb_geometry.coordinates) {
	lat = vm.campground.wkb_geometry.coordinates[0];
	lon = vm.campground.wkb_geometry.coordinates[1];
        $('#longitude').val(lat);
        $('#latitude').val(lon);

    }
}
var coords = ol.proj.transform([lat,lon], 'EPSG:4326', 'EPSG:3857');
// var coords = ol.proj.transform([-106.63694687814734,42.46614905892275], 'EPSG:4326', 'EPSG:3857');

var iconFeature;
if (lat == 0 && lon == 0) { 
iconFeature = new ol.Feature({
    saved_coordinates: 'yes',
  });

} else {
iconFeature = new ol.Feature({
    geometry: new ol.geom.Point(coords),
    saved_coordinates: 'yes',
  });
}
console.log(iconFeature);
var source = new ol.source.Vector({wrapX: false, features: [iconFeature]});

   var vector = new ol.layer.Vector({
       source: source
   });

   var map = new ol.Map({
        layers: [raster, vector],
        target: 'map',
         view: new ol.View({
            center: [-11000000, 4600000],
            zoom: 5
        })
   });

   var typeSelect = document.getElementById('type');

   var draw; // global so we can remove it later
   function addInteraction() {
            var value = typeSelect.value;
            var value = 'Point';
            var lastFeature; 
            //if (value === 'None') {
            //} else {
                var geometryFunction;
                    console.log(value);
                    draw = new ol.interaction.Draw({
                        source: source,
                        type: /** @type {ol.geom.GeometryType} */(typeSelect.value),
                    });

                    draw.on('drawend', function (e) {
                      // Filter on points ONLY
                      if (value === 'Point') {
                           if (lastFeature) { 
			      source.removeFeature(lastFeature);
                           }
                      }
                      lastFeature = e.feature;
                   });

                 map.addInteraction(draw);
            //}
        };

        if (lat == 0 && lon == 0 ) {
                console.log('no coor'); 
		map.getView().setCenter(ol.proj.transform([114.85900618716143, -29.714142674457065], 'EPSG:4326', 'EPSG:3857'));
        } else {
	        map.getView().setCenter(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857'));
        }

        map.on('singleclick', function(ev) {
          console.log('clicked');

         // Remove Prepopulated Point From Map
         var features = source.getFeatures();
         features.forEach((feature) => {
		console.log(feature);
                var properties = feature.getProperties();
                if ('saved_coordinates' in properties) { 
                  console.log(properties.saved_coordinates);
                  if (properties.saved_coordinates == 'yes') {
                    source.removeFeature(feature);
                  }
                }

         });

         // Save Long and Lat to hidden input field.
          var mouseCoords = [ev.originalEvent.offsetX, ev.originalEvent.offsetY];
          console.log(ev.coordinate);
          var latLon = ol.proj.transform(ev.coordinate, 'EPSG:3857', 'EPSG:4326');
          console.log("GPS SELECT");
          console.log(latLon);
          $('#longitude').val(latLon[0]);
          $('#latitude').val(latLon[1]);
          $('#location_coordinates').val("POINT ("+latLon[0]+" "+latLon[1]+")");
          // console.log("vm.campground.wkb_geometry.coordinates -START");
          var coord = new Object();
          coord.coordinates = latLon;
          coord.type = "Point";
          vm.campground.wkb_geometry = coord;
         

         // Add Point
         addInteraction();

        });
        console.log("ENDED");

        // End Map Point Selection

        $('.form-control').blur(function(){
            vm.$emit('updated', vm.campground);
        });
    },
    updated: function() {
        let vm = this;
        var changed = false;
        if (vm.campground.description != null && vm.editor_updated == false) {
            vm.editor.clipboard.dangerouslyPasteHTML(0, vm.campground.description, 'api');
            changed = true;
        }
        if (changed) {
            vm.editor_updated = true;
        }
    }
}

</script>

<style lang="css">
    #editorhidden{
        height: 200px;
    }
    .features >.panel>.panel-body{
        padding:0;
        max-height: 300px;
        min-height: 300px;
        overflow: auto;
    }
    .features .list-group{
        margin-bottom: 0;
    }
    .features .list-group-item{
        border-radius: 0;
    }
    .list-group-item:last-child{
        border-bottom-left-radius: 5px;
        border-bottom-right-radius: 5px;
    }
    .empty-features{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;
        color: #ccc;
        font-size: 2em;
    }
</style>
