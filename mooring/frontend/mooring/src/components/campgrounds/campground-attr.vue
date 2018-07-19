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
							<div class="panel panel-primary">
								<div class="panel-heading">
									<h3 class="panel-title">Mooring Details</h3>
								</div>
								<div class="panel-body">
									<div class="row">
										<div class="col-md-4">
											<div class="form-group">
												<label class="control-label" >Mooring Name</label>
												<input type="text" name="name" id="name" class="form-control" v-model="campground.name" required/>
											</div>
										</div>
										<div class="col-md-4">
											<div class="form-group">
												<label class="control-label" >Mooring Oracle Code</label>
												<input type="text" name="oracle_code" id="oracle_code" class="form-control" v-model="campground.oracle_code" required/>
											</div>
										</div>
										<div class="col-md-4">
											<div class="form-group ">
												<label class="control-label" >Park</label>
												<select name="park" v-show="!parks.length > 0" class="form-control" >
													<option >Loading...</option>
												</select>
												<select name="park" v-if="parks.length > 0" class="form-control" v-model="campground.park">
													<option v-for="park in parks" :value="park.id">{{ park.name }}</option>
												</select>
											</div>
										</div>
									</div>
									<div class="row">
										<div class="col-md-4">
											<div class="form-group ">
												<label class="control-label" >Mooring Type</label>
												<select id="campground_type" name="campground_type" class="form-control"  v-model="campground.mooring_type">
													<option value="0">Bookable Online</option>
													<option value="1">Not Bookable Online</option>
													<option value="2">Public</option>
													<option value="3">Unpublished</option>
												</select>
											</div>
										</div>
										<div class="col-md-4">
											<div class="form-group ">
												<label class="control-label" >Booking Configuration</label>
												<select id="site_type" name="site_type" class="form-control"  v-model="campground.site_type">
													<option value="0">Bookable per site</option>
													<option value="1">Bookable per site type</option>
													<option value="2">Bookable per site type (hide site number)</option>
												</select>
											</div>
										</div>

                                                                                <div class="col-md-4">
                                                                                        <div class="form-group ">
                                                                                                <label class="control-label" >Mooring Group (Permissions)</label>
                                                                                                <select class="form-control" v-model="campground.mooring_group" id='mooring_groups' name='mooring_groups' multiple>
                                                                                                      <option v-for="m in mooring_groups" :value="m.id" >{{m.name}}</option>
                                                                                                </select>
                                                                                        </div>
                                                                                </div>

									</div>
				                                        <imagePicker :images="campground.images"></imagePicker>

									<div class="row" style="margin-top: 40px;">
										<div class="col-lg-12">
											<div class="panel panel-primary">
												<div class="panel-heading">
													<h3 class="panel-title">Contact</h3>
												</div>
												<div class="panel-body">
													<div class="row">
														<div class="form-group">
															<label class="col-md-4 control-label">Customer Contact</label>
															<div class="col-md-8">
															  	<select class="form-control" name="contact" v-model="campground.contact">
																	<option value="undefined">Select Contact</option>
																	<option v-for="c in contacts" :value="c.id">{{ c.name }}</option>
															  	</select>
															</div>
														</div>
													</div>
                                                    <div class="row">
                                                        <div class="form-group">
                                                            <div class="col-md-6">
                                                                <label class="control-label">Phone Number</label>
												                <input type="text" disabled name="contact_number" id="contact_number" class="form-control" v-model="selected_contact_number" required/>
                                                            </div>
                                                            <div class="col-md-6">
                                                                <label class="control-label">Email</label>
												                <input type="text" disabled name="contact_email" id="contact_email" class="form-control" v-model="selected_contact_email" required/>
                                                            </div>
                                                        </div>
                                                    </div>
												</div>
											</div>
										</div>
									</div>
									<div class="row" style="margin-top: 40px;">
										<div class="col-sm-3 features">
											<div class="panel panel-primary">
												<div class="panel-heading">
													<h3 class="panel-title">Features</h3>
												</div>
												<div class="panel-body" v-bind:class="{ 'empty-features': allFeaturesSelected }">
													<p v-show="allFeaturesSelected" style='text-align: center'>
				                             All features selected
				                         </p>
													<ul class="list-group">
														<a href="" v-for="feature,key in features"  @click.prevent="addSelectedFeature(feature,key)" class="list-group-item list-group-item-primary">{{feature.name}}</a>
													</ul>
												</div>
											</div>
										</div>
										<div class="col-sm-3 features">
											<div class="panel panel-primary">
												<div class="panel-heading">
													<h3 class="panel-title">Selected Feautures</h3>
												</div>
												<div class="panel-body"  v-bind:class="{ 'empty-features': !hasSelectedFeatures }">
													<p v-show="!hasSelectedFeatures" style='text-align: center'>
				                						             No features selected
										                        </p>
													<ul class="list-group">
														<a href="" v-for="feature,key in selected_features"  @click.prevent="removeSelectedFeature(feature, key)" class="list-group-item ">{{feature.name}}</a>
													</ul>
												</div>
											</div>
										</div>
                                                                                <div class="col-sm-6 features">
                                                                                        <div class="panel panel-primary">
                                                                                                <div class="panel-heading">
                                                                                                        <h3 class="panel-title">Location</h3>
                                                                                                </div>
                                                                                                <div class="panel-body" >
<!--- START MAP SELECTION -->

 <div id="map" class="map"></div>
 <input type='hidden' value='' iname='location_coordinates' id='location_coordinates'>
 <input type='hidden' value='Point' name='type' id='type'>

<!--- END MAP SELECTION -->





												</div>
											</div>
										</div>
									</div>
									<div class="row" style="margin-top: 40px;">
										<div class="col-md-12">
											<div class="form-group">
												<label class="control-label" >Description</label>
												<div id="editor" class="form-control"></div>
											</div>
										</div>
									</div>
				                                        <div class="row" style="margin-top: 40px;">
										<div class="col-md-12">
											<div class="form-group">
												<label class="control-label" >Additional confirmation information</label>
												<textarea id="additional_info" class="form-control" v-model="campground.additional_info"/>
											</div>
										</div>
									</div>
									<div class="row" style="margin-top: 40px;">
										<div class="col-sm-8">
											<div class="form-group">
												<div class="col-sm-4 col-md-3 col-lg-2">
													<label style="line-height: 2.5;">Price set at: </label>
												</div>
												<div class="col-sm-8 col-md-9 col-lg-10">
													<select id="price_level" name="price_level" class="form-control" v-model="campground.price_level">
														<option v-for="level in priceSet" :value="level.val">{{ level.name }}</option>
													</select>
												</div>
											</div>
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
                </div>
			</div>

			</form>
		</div>
		<loader :isLoading.sync="isLoading">Loading...</loader>
	</div>
</template>
<style>

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
    bus
}
from '../utils/eventBus.js';
import OpenLayers from 'openlayers';
import ol from 'openlayers';
import imagePicker from '../utils/images/imagePicker.vue'
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
        imagePicker
    },
    data: function() {
        let vm = this;
        return {
            selected_price_set: this.priceSet[0],
            editor: null,
            editor_updated: false,
            features: [],
            selected_features_loaded: false,
            selected_features: Array(),
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            contacts:[],
            mooring_groups: [],
            MooringGroups: [{ id: 1, name: 'Principal' }, { id: 2, name: 'Dessert' }, { id: 3, name: 'Drink' }],
        }
    },
    props: {
        createCampground: {
            default: function() {
                return true;
            }
        },
        priceSet: {
            default: function() {
                return [{
                    'val': 0,
                    name: 'Mooring level'
                }, {
                    'val': 1,
                    name: 'Mooring site Type level'
                }, {
                    'val': 2,
                    name: 'Mooring site level'
                }];
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
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        hasSelectedFeatures: function() {
            return this.selected_features.length > 0;
        },
        allFeaturesSelected: function() {
            return this.features.length < 1;
        },
        selected_contact_number: function() {
            let id = this.campground.contact;
            if(id != null) {
                let contact = this.contacts.find(contact => contact.id === id);
                return contact ? contact.phone_number: '';
            }
            else {
                return '';
            }
        },
        selected_contact_email: function(){
            let id = this.campground.contact;
            if(id != null){
                let contact = this.contacts.find(contact => contact.id === id);
                return contact ? contact.email: '';
            }
            else{
                return '';
            }
        },
		...mapGetters([
          'parks',
          'mooring_groups'
        ]),
 
    },
    watch: {
        campground: {
            handler: function() {
                this.loadSelectedFeatures();
            },
            deep: true

        }
    },
    methods: {
		goBack: function() {
            helpers.goBack(this);
        },
		validateForm:function () {
			let vm = this;
			var isValid = vm.validateEditor($('#editor'));
            return  vm.form.valid() && isValid;
		},
        create: function() {
			if(this.validateForm()){
				this.sendData(api_endpoints.campgrounds, 'POST');
			}
        },
        update: function() {
			if(this.validateForm()){
				this.sendData(api_endpoints.campground(this.campground.id), 'PUT');
			}
        },
        validateEditor: function(el){
            let vm = this;
			if (el.parents('.form-group').hasClass('has-error')) {
				el.tooltip("destroy");
				el.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
			}
            if (vm.editor.getText().trim().length == 0){
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
        sendData: function(url, method) {
            let vm = this;
            vm.isLoading =true;
            var featuresURL = new Array();
            var temp_features = vm.selected_features;
            if (vm.createCampground) {
                vm.campground.features = vm.selected_features;
            }
            vm.campground.features.forEach(function(f) {
                featuresURL.push(f.id);
            });
            vm.campground.features = featuresURL;
            if ( vm.campground.contact == "undefined") {
                vm.campground.contact = '';
            }
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                url: url,
                method: method,
                xhrFields: {
                    withCredentials: true
                },
                data: JSON.stringify(vm.campground),
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                contentType: "application/x-www-form-urlencoded",
                dataType: 'json',
                success: function(data, stat, xhr) {
                    if (method == 'POST') {
                        vm.$router.push({
                            name: 'cg_detail',
                            params: {
                                id: data.id
                            }
                        });
                        vm.isLoading = false;
                    }
                    else if (method == 'PUT') {
                        vm.campground.features = temp_features;
                        vm.showUpdate = true;
                        vm.isLoading = false
                    }
					vm.$store.dispatch("updateAlert",{
						visible:false,
						type:"danger",
						message: ""
					});
                },
                error: function(resp) {
					vm.$store.dispatch("updateAlert",{
						visible:true,
						type:"danger",
						message: helpers.apiError(resp)
					});
                    vm.isLoading = false
                }
            });
        },
        showAlert: function() {
            bus.$emit('showAlert', 'alert1');
        },
        loadParks: function() {
            var vm = this;
   	    if (vm.parks.length == 0) {
                vm.$store.dispatch("fetchParks");
            }
        },
        loadMooringGroups: function() {
            let vm =this;
            $.ajax({
                url: api_endpoints.mooring_groups,
                dataType: 'json',
                async: false,
                success: function(data, stat, xhr) {
                    vm.mooring_groups = data;
                }
            });

        },
        loadFeatures: function() {
            var vm = this;
            var url = api_endpoints.features;
            console.log(url);
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.features = data;
                }
            });
        },
        addSelectedFeature: function(feature, key) {
            let vm = this;
            vm.selected_features.push(feature);
            vm.features.splice(key, 1);
            vm.selected_features.sort(function(a, b) {
                return parseInt(a.id) - parseInt(b.id)
            });
        },
        removeSelectedFeature: function(feature, key) {
            let vm = this;
            vm.features.push(feature);
            vm.selected_features.splice(key, 1);
            vm.features.sort(function(a, b) {
                return parseInt(a.id) - parseInt(b.id)
            });
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
                }
            });
        },
        addFormValidations: function() {
            this.form.validate({
				ignore:'div.ql-editor',
                rules: {
                    name: "required",
                    park: "required",
                    campground_type: "required",
                    site_type: "required",
                    street: "required",
                    email: {
                        required: true,
                        email: true
                    },
                    telephone: "required",
                    postcode: "required",
                    price_level: "required"
                },
                messages: {
                    name: "Enter a campground name",
                    park: "Select a park from the options",
                    campground_type: "Select a campground type from the options",
                    site_type: "Select a site type from the options",
                    price_level: "Select a price level from the options"
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);

                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
        },
        loadSelectedFeatures: function() {
            let vm = this;
            if (vm.campground.features) {
                if (!vm.createCampground) {
                    vm.selected_features = vm.campground.features;
                }
                $.each(vm.campground.features, function(i, cgfeature) {
                    $.each(vm.features, function(j, feat) {
                        if (feat != null) {
                            if (cgfeature.id == feat.id) {
                                vm.features.splice(j, 1);
                            }
                        }
                    })
                });
            }

        }
    },
    mounted: function() {
        let vm = this;
        vm.loadParks();
        vm.loadFeatures();
        vm.fetchCampground();
        vm.loadMooringGroups();

        console.log('LOG');
        console.log(vm.mooring_groups);
        console.log(vm);
        vm.editor = new Editor('#editor', {
            modules: {
                toolbar: true
            },
            theme: 'snow'
        });
        vm.editor.clipboard.dangerouslyPasteHTML(0, vm.campground.description, 'api');
        vm.editor.on('text-change', function(delta, oldDelta, source) {
            var text = $('#editor >.ql-editor').html();
            vm.campground.description = text;
			vm.validateEditor($('#editor'));
        });
        
        vm.form = $('#attForm');
        vm.addFormValidations();
		vm.$http.get(api_endpoints.contacts).then((response) => {
			vm.contacts = response.body
		}, (error) => {
			console.log(error);
		});

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
    if (vm.campground.wkb_geometry.coordinates) {
	lat = vm.campground.wkb_geometry.coordinates[0];
	lon = vm.campground.wkb_geometry.coordinates[1];
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
            zoom: 4
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
          console.log(latLon);
          $('#location_coordinates').val("POINT ("+latLon[0]+" "+latLon[1]+")");
          // console.log("vm.campground.wkb_geometry.coordinates -START");
          var coord = new Object();
          coord.coordinates = latLon;
          coord.type = "Point";
          vm.campground.wkb_geometry = coord;
         

         // Add Point
         addInteraction();

        });


        // End Map Point Selection

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
    #editor{
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
