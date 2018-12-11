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
                                        <label class="control-label" >Mooring Park</label>
                                        <select name="park" v-show="!parks.length > 0" class="form-control" >
                                            <option >Loading...</option>
                                        </select>
                                        <select name="park" ref="park" id="park" v-if="parks.length > 0" class="form-control" v-model="campground.park">
                                            <option v-for="park in parks" :value="park.id">{{ park.name }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div style="margin-top: 40px;margin-left:10px;" class="alert alert-danger" id="selected_features_warning">Please select at least 1 feature.</div>
                            </div>
                            <div class="row">
                                <div class="col-md-0">
                                    <div class="form-group " style='display:none'>
                                        <label class="control-label" >Booking Configuration</label>
                                        <select id="site_type" name="site_type" class="form-control"  v-model="campground.site_type">
                                            <option value="0" selected >Bookable per site</option>
                                            <option value="1" >Bookable per site type</option>
                                            <option value="2">Bookable per site type (hide site number)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label class="control-label">Mooring Features</label>
                                        <select class="form-control" id="features" name="features" ref="features" v-model="features_selected" multiple>
                                            <option v-for="f in features" :value="f.id">{{ f.name }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group ">
                                        <label class="control-label" >Mooring Group (Permissions)</label>
                                        <select class="form-control" ref="group_permissions" v-model="campground.mooring_group" id='mooring_groups' name='mooring_groups' multiple >
                                            <option v-for="m in mooring_groups" :value="m.id" >{{m.name}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="form-group ">
                                        <label class="control-label" >Booking Type</label>
                                        <select id="campground_type" ref="campground_type" name="campground_type" class="form-control"  v-model="campground.mooring_type">
                                            <option value="0">Bookable Online</option>
                                            <option value="1">Not Bookable Online</option>
                                            <option value="2">Public</option>
                                            <option value="3">Unpublished</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-group ">
                                        <label class="control-label" >Mooring Physical Type</label>
                                        <select id="campground_type_physical" ref="type_physical" name="campground_type_physical" class="form-control"  v-model="campground.mooring_physical_type">
                                            <option value="0">Mooring</option>
                                            <option value="1">Jetty Pen</option>
                                            <option value="2">Beach Pen</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-group ">
                                        <label class="control-label" >Mooring Class</label>
                                        <select id="campground_class" ref="class" name="campground_class" class="form-control"  v-model="campground.mooring_class">
                                            <option value="small">Small</option>
                                            <option value="medium">Medium</option>
                                            <option value="large">Large</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                                                                                                   
                            <div class="row" >
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
    height:30px;
    line-height:30px;
    padding:7px 9px;
}

</style>

<script>
import {
    $,
    api_endpoints,
    helpers,
    validate,
    select2
}
from '../../hooks.js'
import {
    bus,
}
from '../utils/eventBus.js';
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
            features: [],
            selected_features_loaded: false,
            selected_features: Array(),
            features_selected:[],
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            reload : false,
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
        campground: {
            default: function() {
                return {
                    address: {},
                    images: []
                };
            },
            type: Object
        },
        loadingDetails: {
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
        hasSelectedFeatures: function() {
            return this.selected_features.length > 0;
        },
        allFeaturesSelected: function() {
            return this.features.length < 1;
        },
        selected_contact_number: function() {
            let id = this.campground.contact;
            if(id != null) {
                let contact = this.contacts.find(contact => contact.id == id);
                return contact ? contact.phone_number: '';
            }
            else {
                return '';
            }
        },
        selected_contact_email: function(){
            let id = this.campground.contact;
            if(id != null){
                let contact = this.contacts.find(contact => contact.id == id);
                return contact ? contact.email: '';
            }
            else{
                return '';
            }
        },
        jettyPen: function(){
            return this.campground.mooring_physical_type == 1;
        },
		...mapGetters([
          'parks',
          'mooring_groups'
        ]),
 
    },
    watch: {
        loadingDetails: {
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
            deep: true,

        }
    },
    methods: {
		goBack: function() {
            helpers.goBack(this);
        },
		validateForm:function () {
			let vm = this;
            var isValid = true;
            if(!vm.campground.features || vm.campground.features == ''){
                $('#selected_features_warning').css("display","inline");
                isValid = false;
            } else {
                $('#selected_features_warning').css("display","none");
            }
            
            return  vm.form.valid() && isValid;
		},
        create: function() {
            console.log("CREATE");
		this.setFeatures();
			if(this.validateForm()){
				this.sendData(api_endpoints.campgrounds, 'POST');
			}
        },
        update: function() {
			this.setFeatures();
			if(this.validateForm()){
				this.sendData(api_endpoints.campground(this.campground.id), 'PUT',true); 
			}	
        },
        sendData: function(url, method, reload=false) {
            let vm = this;
            vm.isLoading =true;
            vm.reload = reload;
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "details");
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
        setFeatures: function(){
            let vm = this;
            vm.campground.features = vm.features_selected;
            console.log("Features updated");
            vm.$emit('updated', vm.campground);
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
                    setTimeout("vm.setFeatures();", 1500);
                    
                    console.log("Finished fetching campground");
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
//                    site_type: "required",
//                    street: "required",
                    email: {
                        required: true,
                        email: true
                    },
                    telephone: "required",
            //        postcode: "required",
 //                   price_level: "required"

                },
                messages: {
                    name: "Enter a mooring name",
                    park: "Select a park from the options",
                    campground_type: "Select a mooring type from the options",
                    site_type: "Select a site type from the options",
//                    price_level: "Select a price level from the options"
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
    },
    mounted: function() {
        let vm = this;
        vm.fetchCampground();
        vm.loadParks();
        vm.loadFeatures();
        vm.loadMooringGroups();

        vm.form = $('#attForm');
        vm.addFormValidations();
		vm.$http.get(api_endpoints.contacts).then((response) => {
			vm.contacts = response.body
		}, (error) => {
			console.log(error);
		});

        $('.form-control').blur(function(){
            vm.$emit('updated', vm.campground);
        });

        setTimeout( function(){
            //Park selector
            $(vm.$refs.park).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.campground.park = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.campground.park = selected.val();
            });
            //Mooring type selector
            $(vm.$refs.campground_type).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_type = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_type = selected.val();
            });
            //Group permissions
            $(vm.$refs.group_permissions).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                var mooringgroups = [];
                console.log(selected.val());
                var select_array = selected.val();
                console.log(select_array);
                for (var i = 0; i < select_array.length; i++){
                    var val = select_array[i];
                    console.log(val);
                    var intval = parseInt(select_array[i]);
                    console.log(intval);
                    mooringgroups.push(intval);
                }
                console.log(mooringgroups);
                vm.campground.mooring_group = mooringgroups;
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                var mooringgroups = [];
                var select_array = selected.val();
                for (var i = 0; i < select_array.length; i++){
                    var val = select_array[i];
                    var intval = parseInt(select_array[i]);
                    mooringgroups.push(intval);
                }
                vm.campground.mooring_group = mooringgroups;
            });
            //Physical Type
            $(vm.$refs.type_physical).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_physical_type = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_physical_type = selected.val();
            });
            //Class
            $(vm.$refs.class).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_class = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.campground.mooring_class = selected.val();
            });
            //Contact
            $(vm.$refs.contact).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.campground.contact = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.campground.contact = selected.val();
            });
            //Features
            $(vm.$refs.features).select2({
                "theme": "bootstrap",
            }).
            on("select2:select", function (e){
                var selected = $(e.currentTarget);
                vm.features_selected = selected.val();
            }).
            on("select2:unselect", function (e){
                var selected = $(e.currentTarget);
                vm.features_selected = selected.val();
            });
            // if (vm.campground.features.length > 0){
                // vm.setFeatures();
            $(vm.$refs.features).val(vm.features_selected).trigger('change');
            vm.$emit('updated', vm.campground);
            // } 
            // else {
            //     vm.fetchCampground();
            //     // vm.setFeatures();
            //     $(vm.$refs.features).val(vm.campground.features).trigger('change');
            // }

        }, 1000);

       
    },
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
