<template lang="html">
    <div id="editVehicle">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vehicleForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Vehicle Type</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <select class="form-control" name="access_type" ref="access_type" v-model="vehicle_access_id">
                                            <option v-for="a in access_types" :value="a.id">{{a.name}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Seating Capcity</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="capacity" ref="capacity" v-model="vehicle.capacity" type="text">
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Registration No.</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="rego" ref="rego" v-model="vehicle.rego" type="text">
                                    </div>
                                </div>
                            </div>

                            <!-- <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Registration Expiry</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="rego_expiry" style="width: 70%;">
                                            <input type="text" class="form-control" placeholder="DD/MM/YYYY" >
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

 -->
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Registration Expiry</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="rego_expiry" style="width: 70%;">
                                            <input type="text" class="form-control" name="rego_expiry" placeholder="DD/MM/YYYY" v-model="vehicle.rego_expiry">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Transport licence no.</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="license" ref="license" v-model="vehicle.license" type="text">
                                    </div>
                                </div>
                            </div>                           
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="issuingVehicle" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import Vue from 'vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'Edit-Vehicle',
    components:{
        modal,
        alert
    },
    props:{
        vehicle_id: {
            type: Number,
            required: true
        },
        vehicle_action:{
            type: String,
            default: 'edit'
        },
        access_types:{
            type: Array,
            required: true
        }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            vehicle: Object,
            vehicle_id: Number,
            //access_types: null,
            vehicle_access_id: null,
            state: 'proposed_vehicle',
            issuingVehicle: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            dateFormat:'YYYY-MM-DD',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return this.vehicle_action == 'add' ? 'Add a new Vehicle record' : 'Edit a vehicle record';
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
               
            }
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.vehicle = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.rego_expiry).data('DateTimePicker').clear();
            this.$refs.capacity='';
            this.$refs.license='';
            this.$refs.rego='';
            this.validation_form.resetForm();
        },
        fetchContact: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            },(error) => {
                console.log(error);
            } );
        },
        /*
        fetchAccessTypes: function(){
            let vm=this;
            Vue.http.get('/api/access_types.json').then((res) => {
                      vm.access_types=res.body; 
                },
              err => { 
                        console.log(err);
                  });
        },
        */
        fetchVehicle: function(vid){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.vehicles,vid)).then((res) => {
                      vm.vehicle=res.body; 
                      if(vm.vehicle.access_type)
                      {
                        vm.vehicle_access_id=vm.vehicle.access_type.id
                      }
                      // if(vm.vehicle.rego_expiry){
                      //   vm.vehicle.rego_expiry=vm.vehicle.rego_expiry.format('DD/MM/YYYY')
                      //   }
                },
              err => { 
                        console.log(err);
                  });
        },

        sendData:function(){
            let vm = this;
            vm.errors = false;
            if(vm.vehicle_access_id!=null){
                vm.vehicle.access_type=vm.vehicle_access_id
            }
            // if(vm.vehicle.rego_expiry){
            //     vm.vehicle.rego_expiry=vm.vehicle.rego_expiry.format('YYYY-MM-DD')
            // }
            let vehicle = JSON.parse(JSON.stringify(vm.vehicle));
            vm.issuingVehicle = true;
            if(vm.vehicle_action=="add" && vm.vehicle_id==null)
            {
                vm.$http.post(api_endpoints.vehicles,JSON.stringify(vehicle),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingVehicle = false;
                        vm.vehicle={};
                        vm.close();
                        swal(
                             'Created',
                             'New vehicle record has been created.',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingVehicle = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
            else{
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.vehicles,vm.vehicle_id+'/edit_vehicle'),JSON.stringify(vehicle),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingVehicle = false;
                        vm.vehicle={};
                        vm.close();
                        swal(
                             'Saved',
                             'Vehicle details has been saved.',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingVehicle = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                }
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    access_type:"required",                    
                },
                messages: {
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
       eventListeners:function () {
            let vm = this;
            $(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.rego_expiry).on('dp.change', function(e){
                if ($(vm.$refs.rego_expiry).data('DateTimePicker').date()) {
                    vm.vehicle.rego_expiry =  e.date.format('DD/MM/YYYY');
                    //vm.vehicle.rego_expiry =  e.date.format('YYYY-MM-DD')
                }
                else if ($(vm.$refs.rego_expiry).data('date') === "") {
                    vm.vehicle.rego_expiry = null;
                }
             });

            // Intialise select2
            // $(vm.$refs.access_type).select2({
            //     "theme": "bootstrap",
            //     allowClear: true,
            //     placeholder:"Select access"
            // }).
            // on("select2:select",function (e) {
            //     var selected = $(e.currentTarget);
            //     //vm.vehicle.access_type = selected.val();
            //     vm.vehicle_access_id = selected.val();
            // }).
            // on("select2:unselect",function (e) {
            //     var selected = $(e.currentTarget);
            //     //vm.vehicle.access_type = selected.val();
            //     vm.vehicle_access_id = selected.val();
            // });


            //Initialise Date Picker TODO: Check why this is not working
            // console.log($(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions))
            // $(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.rego_expiry).on('dp.change', function(e){
            //     if ($(vm.$refs.rego_expiry).data('DateTimePicker').date()) {
            //         vm.vehicle.rego_expiry =  e.date.format('DD/MM/YYYY');
            //     }
            //     else if ($(vm.$refs.rego_expiry).data('date') === "") {
            //         vm.vehicle.rego_expiry = "";
            //     }
            //  });
       }
   },
   mounted:function () {
        let vm =this;
        //vm.fetchAccessTypes();
        
        vm.form = document.forms.vehicleForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
