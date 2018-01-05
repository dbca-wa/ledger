<template lang="html">
<div  id="cg_attr" >
	<div v-show="!isLoading">
		<form id="attForm">
		<div class="col-sm-12">
			<alert :show.sync="showUpdate" type="success" :duration="7000">
				<p>Campground successfully updated</p>
			</alert>
			<alert :show.sync="showError" type="danger">
				<p>{{errorString}}<p/>
			</alert>
					<div class="row">
						<div class="col-lg-12">
							<div class="panel panel-primary">
								<div class="panel-heading">
									<h3 class="panel-title">Campground Details</h3>
								</div>
								<div class="panel-body">
									<div class="row">
										<div class="col-md-4">
											<div class="form-group">
												<label class="control-label" >Campground Name</label>
												<input type="text" name="name" id="name" class="form-control" v-model="campground.name" required/>
											</div>
										</div>
										<div class="col-md-4">
											<div class="form-group">
												<label class="control-label" >Campground Oracle Code</label>
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
										<div class="col-md-6">
											<div class="form-group ">
												<label class="control-label" >Campground Type</label>
												<select id="campground_type" name="campground_type" class="form-control"  v-model="campground.campground_type">
													<option value="0">Bookable Online</option>
													<option value="1">Not Bookable Online</option>
													<option value="2">Other accomodation</option>
													<option value="3">Unpublished</option>
												</select>
											</div>
										</div>
										<div class="col-md-6">
											<div class="form-group ">
												<label class="control-label" >Booking Configuration</label>
												<select id="site_type" name="site_type" class="form-control"  v-model="campground.site_type">
													<option value="0">Bookable per site</option>
													<option value="1">Bookable per site type</option>
													<option value="2">Bookable per site type (hide site number)</option>
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
										<div class="col-sm-6 features">
											<div class="panel panel-primary">
												<div class="panel-heading">
													<h3 class="panel-title">Features</h3>
												</div>
												<div class="panel-body" v-bind:class="{ 'empty-features': allFeaturesSelected }">
													<p v-show="allFeaturesSelected">
				                             All features selected
				                         </p>
													<ul class="list-group">
														<a href="" v-for="feature,key in features"  @click.prevent="addSelectedFeature(feature,key)" class="list-group-item list-group-item-primary">{{feature.name}}</a>
													</ul>
												</div>
											</div>
										</div>
										<div class="col-sm-6 features">
											<div class="panel panel-primary">
												<div class="panel-heading">
													<h3 class="panel-title">Selected Feautures</h3>
												</div>
												<div class="panel-body"  v-bind:class="{ 'empty-features': !hasSelectedFeatures }">
													<p v-show="!hasSelectedFeatures">
				                             No features selected
				                         </p>
													<ul class="list-group">
														<a href="" v-for="feature,key in selected_features"  @click.prevent="removeSelectedFeature(feature, key)" class="list-group-item ">{{feature.name}}</a>
													</ul>
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
                    name: 'Campground level'
                }, {
                    'val': 1,
                    name: 'Campsite Type level'
                }, {
                    'val': 2,
                    name: 'Campsite level'
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
        selected_contact_number: function(){
            let id = this.campground.contact;
            if(id != null){
                let contact = this.contacts.find(contact => contact.id === id);
                return contact ? contact.phone_number: '';
            }
            else{
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
          'parks'
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
        loadFeatures: function() {
            var vm = this;
            var url = api_endpoints.features;
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
		})
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
