<template lang="html">
    <div  id="cg_limits" >
        <div>
            <form id="limitsForm">
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
                                            <div class="col-md-4">
                                                <label class="control-label" >Maximum Vessel Size (Meters)</label>
                                                <input type="number" name="vessel_size_limit" id="vessel_size_limit" style="margin-top:10px;" class="form-control form-control-input" v-model="campground.vessel_size_limit" @blur="validateSize()"required/>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="control-label" >Maximum Vessel Draft (Meters)</label>
                                                <input type="number" name="vessel_draft_limit" id="vessel_draft_limit" style="margin-top:10px;" class="form-control form-control-input" v-model="campground.vessel_draft_limit" @blur="validateDraft()" required/>
                                            </div>
                                            <div class="col-md-4" v-if="jettyPen">
                                                <label class="control-label" >Maximum Vessel Beam (Meters)</label>
                                                <input type="number" name="vessel_beam_limit" id="vessel_beam_limit" style="margin-top:10px;" class="form-control form-control-input" v-model="campground.vessel_beam_limit" @blur="validateBeamWeight()" required/>
                                            </div>
                                            <div class="col-md-4" v-else>
                                                <label class="control-label" >Maximum Vessel Weight (Tons)</label>
                                                <input type="number" name="vessel_weight_limit" id="vessel_weight_limit" style="margin-top:10px;" class="form-control form-control-input" v-model="campground.vessel_weight_limit" @blur="validateBeamWeight()" required/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="display:none;">
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
	</div>
</template>
<style>
.alert{
    display:none;
    margin-left:15px;
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
}
from '../utils/eventBus.js';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
export default {
    name: 'cg_limits',
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
            reload : false
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
        loadingLimits: {
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
        jettyPen: function(){
            return this.campground.mooring_physical_type == 1;
        },
    },
    watch: {
        loadingLimits: {
            immediate: true,
            deep: true,
            handler: function(n, o){
                this.isLoading = n;
            }
        },
        campground: {
            handler: function() {
            },
            deep: true

        }
    },
    methods: {
		goBack: function() {
            helpers.goBack(this);
        },
        validateSize: function(){
            let vm = this;
            var isValid = true;
            if(!parseInt(vm.campground.vessel_size_limit) > 0){
                isValid = false;
                var error = {
                    title : "Invalid Size",
                    text : "Please select a size greater than 0",
                    type : "warning",
                }
                vm.$emit('error', error);
            }
            return isValid;
        },
        validateDraft: function(){
            let vm = this;
            var isValid = true;
            if(!parseInt(vm.campground.vessel_draft_limit) > 0){
                isValid = false;
                var error = {
                    title : "Invalid Draft",
                    text : "Please select a draft greater than 0",
                    type : "warning",
                }
                vm.$emit('error', error);
            }
            return isValid;
        },
        validateBeamWeight: function(){
            let vm = this;
            var isValid = true;
            if(vm.campground.mooring_physical_type == 1) {
                if(!parseInt(vm.campground.vessel_beam_limit) > 0){
                    isValid = false;
                    var error = {
                        title : "Invalid Beam",
                        text : "Please select a beam greater than 0",
                        type : "warning",
                    }
                    vm.$emit('error', error);
                }
            } else {
                if(!parseInt(vm.campground.vessel_weight_limit) > 0){
                    isValid = false;
                    var error = {
                        title : "Invalid Weight",
                        text : "Please select a weight greater than 0",
                        type : "warning",
                    }
                    vm.$emit('error', error);
                }
            }
            return isValid;
        },
        validateLimits: function() {
            let vm = this;
            var isValid = true;
            isValid = vm.validateSize();
            if (isValid){
                isValid = vm.validateDraft();
            }
            if (isValid){
                isValid = vm.validateBeamWeight();
            }
            return isValid;
        },
		validateForm:function () {
			let vm = this;
            var isValid = vm.validateLimits();
            return  vm.form.valid() && isValid;
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
            if ( vm.campground.contact == "undefined") {
                vm.campground.contact = '';
            }
            if (vm.campground.mooring_physical_type == 1){
                vm.campground.vessel_weight_limit = 0;
            } else {
                vm.campground.vessel_beam_limit = 0;
            }
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "limits");
        },
        showAlert: function() {
            bus.$emit('showAlert', 'alert1');
        },
        // addFormValidations: function() {
        //     this.form.validate({
		// 		ignore:'div.ql-editor',
        //         rules: {
        //             vessel_size_limit: "required",
        //             vessel_draft_limit: "required",
        //         },
        //         messages: {
        //             vessel_size_limit: "Please set a size limit greater than 0",
        //             vessel_draft_limit: "Please set a draft limit greater than 0",
        //         },
        //         showErrors: function(errorMap, errorList) {
        //             $.each(this.validElements(), function(index, element) {
        //                 var $element = $(element);

        //                 $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
        //             });

        //             // destroy tooltips on valid elements
        //             $("." + this.settings.validClass).tooltip("destroy");

        //             // add or update tooltips
        //             for (var i = 0; i < errorList.length; i++) {
        //                 var error = errorList[i];
        //                 $('#'+ error.element.id).focus();
        //                 $(error.element).tooltip({
        //                         trigger: "focus"
        //                     })
        //                     .attr("data-original-title", error.message)
        //                     .parents('.form-group').addClass('has-error');
        //             }
        //         }
        //     });
        // },
    },
    mounted: function() {
        let vm = this;
        vm.form = $('#limitsForm');
        // vm.addFormValidations();
        $('.form-control').blur(function(){
            vm.$emit('updated', vm.campground);
        });
    },
}

</script>

