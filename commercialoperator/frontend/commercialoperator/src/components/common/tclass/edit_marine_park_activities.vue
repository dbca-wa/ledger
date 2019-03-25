<template lang="html">
    <div id="editMarinePark">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="marineActivitiesForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <label for="">Zone</label>
                                <select class="form-control" v-model="selected_zone">
                                    <option v-for="z in park.zones" :value="z">{{z.name}}</option>
                                </select>
                            </div>                           
                            <form>
                                <div class="form-horizontal col-sm-6">
                                  <label class="control-label">Activities</label>
                                  <div class="" v-for="a in selected_zone.allowed_activities">
                                    <div class="form-check">
                                      <input :onclick="isClickable" class="form-check-input" v-model="selected_zone.new_activities" :value="a.id" ref="Checkbox" type="checkbox" data-parsley-required  />
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
    name:'Edit-marine-park-activities',
    components:{
        modal,
        alert
    },
    props:{
        
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
            park_access:[],
            park_activities:[],
            selected_zone: '',
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
            return this.park && this.park.name ? 'Edit Access and Activities for '+this.park.name : 'Edit Access and Activities';
        },
    },
    methods:{
        ok:function () {
            let vm =this;
                var allowed_activities_id=[]
                var new_activities=[]
                
                for(var j=0; j<vm.park.zones.length; j++) {
                        
                        var data={
                            'zone':vm.park.zones[j].id,
                            'activities':vm.park.zones[j].new_activities
                        }
                        new_activities.push(data)
                    
                }
                vm.$emit('refreshSelectionFromResponse',vm.park.id, new_activities);              
            vm.close(); 
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.park_id = null;
            this.selected_zone='';
            this.park_activities=[];
            this.errors = false;
            $('.has-error').removeClass('has-error');
            //this.validation_form.resetForm();
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

        addFormValidations: function() {
            // let vm = this;
            // vm.validation_form = $(vm.form).validate({
            //     rules: {
            //         access_type:"required",                    
            //     },
            //     messages: {
            //     },
            //     showErrors: function(errorMap, errorList) {
            //         $.each(this.validElements(), function(index, element) {
            //             var $element = $(element);
            //             $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
            //         });
            //         // destroy tooltips on valid elements
            //         $("." + this.settings.validClass).tooltip("destroy");
            //         // add or update tooltips
            //         for (var i = 0; i < errorList.length; i++) {
            //             var error = errorList[i];
            //             $(error.element)
            //                 .tooltip({
            //                     trigger: "focus"
            //                 })
            //                 .attr("data-original-title", error.message)
            //                 .parents('.form-group').addClass('has-error');
            //         }
            //     }
            // });
       },
       eventListeners:function () {
            
       }
   },
   mounted:function () {
        let vm =this;
        //vm.fetchAccessTypes();        
        vm.form = document.forms.marineActivitiesForm;
        //vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
