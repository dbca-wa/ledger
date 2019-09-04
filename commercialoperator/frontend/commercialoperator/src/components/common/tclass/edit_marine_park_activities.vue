<template lang="html">
    <div id="editMarinePark">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title(zone_label)" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="marineActivitiesForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <!--
                            <div class="form-group">
                                <label for="">Zone</label>
                                <select class="form-control" v-model="selected_zone">
                                    <option v-for="z in park.zones" :value="z">{{z.name}}</option>
                                </select>
                            </div>
                            -->
                            <form>
                                <div class="form-horizontal col-sm-6">
                                  <label class="control-label">Activities</label>
                                  <div class="" v-for="a in allowed_activities">
                                    <div class="form-check">
                                      <input :onclick="isClickable" class="form-check-input" v-model="new_activities" :value="a.id" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities" />
                                      {{ a.name }}
                                    </div>
                                  </div>
                                </div>
                                <div class="form-group">
                                  <div class="row">
                                    <div class="form-horizontal col-sm-9">
                                        
                                        <label class="control-label pull-left"  for="Name">Point of access</label>
                                    </div>
                                    <div class="form-horizontal col-sm-9">
                                        <input class="form-control" name="access_point" ref="access_point" v-model="access_point" type="text" :disabled="!canEditActivities">
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
    name:'Edit-marine-park-activities',
    components:{
        modal,
        alert
    },
    props:{
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
            zone_id: null,
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
    },
    methods:{
        title: function (label) {
            return 'Edit Access and Activities for ' + label;
        },
        ok:function () {
            let vm =this;
            var new_activities=[]

            var data={
                'zone': vm.zone_id,
                'activities':vm.new_activities,
                'access_point': vm.access_point
            }
            new_activities.push(data)
            vm.$emit('refreshSelectionFromResponse', vm.park_id, vm.zone_id, data);
            vm.close(); 
        },

        /*
        _ok:function () {
            let vm =this;
                var allowed_activities_id=[]
                var new_activities=[]
                for(var j=0; j<vm.park.zones.length; j++) {
                        var data={
                            'zone':vm.park.zones[j].id,
                            'activities':vm.park.zones[j].new_activities,
                            'access_point': vm.park.zones[j].access_point
                        }
                        new_activities.push(data)
                }
                console.log(new_activities);
                vm.$emit('refreshSelectionFromResponse',vm.park.id, new_activities);
            vm.close(); 
        },
        */
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
        addFormValidations: function() {
        },
       eventListeners:function () {
       }
   },
   mounted:function () {
        let vm =this;
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
