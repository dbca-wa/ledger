<template lang="html">
    <div  id="cg_contact" >
        <div v-show="!isLoading">
            <form id="contactForm">
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
                                <div class="col-lg-12">
                                    <div class="row">
                                        <div class="form-group">
                                            <div class="col-md-6">
                                                <label class="control-label">Customer Contact</label>
                                                <select class="form-control" ref="contact" name="contact" v-model="campground.contact">
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
                            <div class="row">
                                <div class="col-md-12" style="margin-top:20px;">
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
    validate
}
from '../../hooks.js'
import {
    bus,
    select2
}
from '../utils/eventBus.js';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
export default {
    name: 'cg_contact',
    components: {
        alert,
        loader,
    },
    data: function() {
        let vm = this;
        return {
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            reload : false,
            contacts:[],
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
                };
            },
            type: Object
        },
        loadingContact: {
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
 
    },
    watch: {
        loadingContact: {
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
		validateForm:function () {
			let vm = this;
            return  vm.form.valid()
		},
        create: function() {
            console.log("CREATE");
			if(this.validateForm()){
				this.sendData(api_endpoints.campgrounds, 'POST');
			}
        },
        update: function() {
			if(this.validateForm()){
				this.sendData(api_endpoints.campground(this.campground.id), 'PUT',true); 
			}	
        },
        sendData: function(url, method, reload=false) {
            let vm = this;
            vm.isLoading =true;
            vm.reload = reload;
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "contact");
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
        addFormValidations: function() {
            this.form.validate({
				ignore:'div.ql-editor',
                rules: {
                    email: {
                        required: true,
                        email: true
                    },
                    telephone: "required",

                },
                messages: {
                    email: "Please select a contact",
                    telephone: "Please select a contact",
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
  
        vm.form = $('#contactForm');
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
        }, 1000);
    },
}

</script>

