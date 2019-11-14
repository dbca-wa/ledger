<template lang="html">
    <div id="editVessel">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vesselForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Nominated Vessel</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="capacity" ref="capacity" v-model="vessel.nominated_vessel" type="text">
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">SPV No./ Reg. No.</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="spv_no" ref="spv_no" v-model="vessel.spv_no" type="text">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Hire and Drive reg.</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="hire_rego" ref="hire_rego" v-model="vessel.hire_rego" type="text">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">No. of craft</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="craft_no" ref="craft_no" v-model="vessel.craft_no" type="text">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Vessel Size</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input class="form-control" name="size" ref="size" v-model="vessel.size" type="text">
                                    </div>
                                </div>
                            </div>                      
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="issuingVessel" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
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
    name:'Edit-Vessel',
    components:{
        modal,
        alert
    },
    props:{
        vessel_id: {
            type: Number,
            required: true
        },
        vessel_action:{
            type: String,
            default: 'edit'
        }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            vessel: Object,
            vessel_id: Number,
            access_types: null,
            vessel_access_id: null,
            state: 'proposed_vessel',
            issuingVessel: false,
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
            return this.vessel_action == 'add' ? 'Add a new Vessel record' : 'Edit a vessel record';
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
            this.vessel = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
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
                },
              err => { 
                        console.log(err);
                  });
        },
        fetchVessel: function(vid){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.vessels,vid)).then((res) => {
                      vm.vessel=res.body; 
                      if(vm.vessel.access_type)
                      {
                        vm.vessel_access_id=vm.vessel.access_type.id
                      }
                      // if(vm.vessel.rego_expiry){
                      //   vm.vessel.rego_expiry=vm.vessel.rego_expiry.format('DD/MM/YYYY')
                      //   }
                },
              err => { 
                        console.log(err);
                  });
        },

        sendData:function(){
            let vm = this;
            vm.errors = false;
            // if(vm.vessel_access_id!=null){
            //     vm.vessel.access_type=vm.vessel_access_id
            // }
            // if(vm.vessel.rego_expiry){
            //     vm.vessel.rego_expiry=vm.vessel.rego_expiry.format('YYYY-MM-DD')
            // }
            let vessel = JSON.parse(JSON.stringify(vm.vessel));
            vm.issuingVessel = true;
            if(vm.vessel_action=="add" && vm.vessel_id==null)
            {
                vm.$http.post(api_endpoints.vessels,JSON.stringify(vessel),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingVessel = false;
                        vm.close();
                        swal(
                             'Created',
                             'New vessel record has been created.',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingVessel = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
            else{
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.vessels,vm.vessel_id+'/edit_vessel'),JSON.stringify(vessel),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingVessel = false;
                        vm.close();
                        swal(
                             'Saved',
                             'Vessel details has been saved.',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingVessel = false;
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
            // $(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.rego_expiry).on('dp.change', function(e){
            //     if ($(vm.$refs.rego_expiry).data('DateTimePicker').date()) {
            //         vm.vessel.rego_expiry =  e.date.format('DD/MM/YYYY');
            //         //vm.vessel.rego_expiry =  e.date.format('YYYY-MM-DD')
            //     }
            //     else if ($(vm.$refs.rego_expiry).data('date') === "") {
            //         vm.vessel.rego_expiry = null;
            //     }
            //  });

            // Intialise select2
            // $(vm.$refs.access_type).select2({
            //     "theme": "bootstrap",
            //     allowClear: true,
            //     placeholder:"Select access"
            // }).
            // on("select2:select",function (e) {
            //     var selected = $(e.currentTarget);
            //     //vm.vessel.access_type = selected.val();
            //     vm.vessel_access_id = selected.val();
            // }).
            // on("select2:unselect",function (e) {
            //     var selected = $(e.currentTarget);
            //     //vm.vessel.access_type = selected.val();
            //     vm.vessel_access_id = selected.val();
            // });


            //Initialise Date Picker TODO: Check why this is not working
            // console.log($(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions))
            // $(vm.$refs.rego_expiry).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.rego_expiry).on('dp.change', function(e){
            //     if ($(vm.$refs.rego_expiry).data('DateTimePicker').date()) {
            //         vm.vessel.rego_expiry =  e.date.format('DD/MM/YYYY');
            //     }
            //     else if ($(vm.$refs.rego_expiry).data('date') === "") {
            //         vm.vessel.rego_expiry = "";
            //     }
            //  });
       }
   },
   mounted:function () {
        let vm =this;
        //vm.fetchAccessTypes();
        
        vm.form = document.forms.vesselForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
