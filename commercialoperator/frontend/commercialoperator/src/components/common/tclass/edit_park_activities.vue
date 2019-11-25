<template lang="html">
    <div id="editParkActivities">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vehicleForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <form>
                                <div class="form-horizontal col-sm-6">
                                  <label class="control-label">Access</label>
                                  <div class="" v-for="a in allowed_access_types">
                                    <div class="form-check">
                                      <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" v-model="park_access" :value="a.id" data-parsley-required :disabled="!canEditActivities" />
                                      {{ a.name }}
                                    </div>
                                  </div>
                                </div>
                            </form>

                            <form>
                                <div class="form-horizontal col-sm-6">
                                  <label class="control-label">Activities</label>
                                  <div class="" v-for="a in allowed_activities">
                                    <div class="form-check">
                                      <input :onclick="isClickable" class="form-check-input" v-model="park_activities" :value="a.id" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities" />
                                      {{ a.name }}
                                    </div>
                                  </div>
                                </div>
                            </form>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="issuingVehicle" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else class="btn btn-default" @click="ok" :disabled="!canEditActivities">Ok</button>
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
    name:'Edit-Park-Activities',
    components:{
        modal,
        alert
    },
    props:{
        vehicle_id: {
            type: Number,
            required: false
        },
        vehicle_action:{
            type: String,
            default: 'edit'
        },
        canEditActivities:{
          type: Boolean,
          default: true
        }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            park: Object,
            park_id: null,
            park_name: '',
            access_types: null,
            allowed_activities:[],
            allowed_access_types:[],
            park_access:[],
            park_activities:[],
            vehicle_access_id: null,
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
            return this.park_name ? 'Edit Access and Activities for '+this.park_name : 'Edit Access and Activities';
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                //vm.sendData();
                var allowed_activities_id=[]
                for(var i=0; i<vm.allowed_activities.length; i++){
                    allowed_activities_id.push(vm.allowed_activities[i].id)
                }
                for(var j=0; j<vm.park_activities.length; j++) {
                    if(allowed_activities_id.indexOf(vm.park_activities[j])==-1){
                        vm.park_activities.splice(j,1)
                    }
                }
                vm.$emit('refreshSelectionFromResponse',vm.park_id, vm.park_activities, vm.park_access);
            }
            vm.close();
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.park_id = null;
            this.park_access=[];
            this.park_activities=[];
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
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
        fetchAllowedActivities: function(park_id){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.parks,park_id+'/allowed_activities')).then((res) => {
                      vm.allowed_activities=res.body;                 
                },
              err => { 
                        console.log(err);
                  });
        },
        fetchAllowedAccessTypes: function(park_id){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.parks,park_id+'/allowed_access')).then((res) => {
                      vm.allowed_access_types=res.body;                 
                },
              err => { 
                        console.log(err);
                  });
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
            
       }
   },
   mounted:function () {
        let vm =this;
        vm.fetchAccessTypes();        
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
