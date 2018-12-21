<template lang="html">
    <div id="editVehicle">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vehicleForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div>{{vehicle_id}}</div>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Vehicle Type</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <select class="form-control" name="access_type" ref="access_type">
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
                                        <input class="form-control" name="capacity" ref="capacity" type="text">
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Registration No.</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="rego" ref="rego" type="text">
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Registration Expiry</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="rego_expiry" style="width: 70%;">
                                            <input type="text" class="form-control" name="rego_expiry" placeholder="DD/MM/YYYY">
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
                                        <input class="form-control" name="licence_no" ref="licence_no" type="text">
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
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            vehicle: Object,
            vehicle_id: Number,
            access_types: null,
            state: 'proposed_vehicle',
            issuingVehicle: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
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
            return 'Cancel Vehicle';
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
        fetchAccessTypes: function(){
            let vm=this;
            Vue.http.get('/api/access_types.json').then((res) => {
                      vm.access_types=res.body; 
                      console.log(vm.access_types)                
                },
              err => { 
                        console.log(err);
                  });
        },
        fetchVehicle: function(){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.vehicles,vm.vehicle_id)).then((res) => {
                      vm.vehicle=res.body; 
                      console.log(vm.vehicle)                
                },
              err => { 
                        console.log(err);
                  });
        },

        sendData:function(){
            let vm = this;
            vm.errors = false;
            let vehicle = JSON.parse(JSON.stringify(vm.vehicle));
            vm.issuingVehicle = true;
            
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.vehicles,vm.vehicle_id+'/vehicle_cancellation'),JSON.stringify(vehicle),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingVehicle = false;
                        vm.close();
                        swal(
                             'Cancelled',
                             'An email has been sent to applicant about cancellation of this vehicle',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                       

                    },(error)=>{
                        vm.errors = true;
                        vm.issuingVehicle = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                        
            
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    cancellation_date:"required",                    
                    cancellation_details:"required",
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
            // Intialise select2
            $(vm.$refs.access_type).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select access"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.vehicle.access_type = selected.val();
                vm.vehicle.access_type_id = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.vehicle.access_type = selected.val();
                vm.vehicle.access_type_id = selected.val();
            });

            // Initialise Date Picker
            
            $(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.rego_expiry).on('dp.change', function(e){
                if ($(vm.$refs.rego_expiry).data('DateTimePicker').date()) {
                    vm.vehicle.rego_expiry =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.rego_expiry).data('date') === "") {
                    vm.vehicle.rego_expiry = "";
                }
             });
       }
   },
   mounted:function () {
        let vm =this;
        vm.fetchAccessTypes();
        //console.log(vm.approval_id)
        //vm.fetchVehicle();
        
        vm.form = document.forms.vehicleForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   },
   created: function(){
    let vm=this;
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.vehicles,vm.vehicle_id)).then((res) => {
                      vm.vehicle=res.body; 
                      console.log(vm.vehicle)                
                },
              err => { 
                        console.log(err);
        });
   }
}
</script>

<style lang="css">
</style>
