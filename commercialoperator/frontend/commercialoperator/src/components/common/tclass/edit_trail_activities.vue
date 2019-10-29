<template lang="html">
    <div id="editTrailActivities">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vehicleForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <form>
                                <div class="form-horizontal col-sm-3">
                                   <label class="control-label">Sections</label> 
                                </div>
                            </form>
                            <form>
                                <div class="form-horizontal col-sm-9">
                                   <label class="control-label">Activities</label> 
                                </div>
                            </form>
                            <form>
                            <div class="row" v-for="s in trail.sections">
                                <div class="form-horizontal col-sm-3">
                                  <div class="" >
                                    <div class="form-check">
                                      <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" v-model="s.checked"  data-parsley-required :disabled="!canEditActivities"/><a v-if="s.doc_url" :href="s.doc_url" target="_blank" >
                                        {{ s.name }}</a><span v-else>
                                        {{ s.name }}</span>
                                    </div>
                                  </div>
                                </div>

                                <div class="form-horizontal col-sm-9">
                                  <div v-for="a in trail.allowed_activities" >
                                    <div class="form-check">
                                      <input :disabled="!s.checked" :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" :id="'section'+s.id+'activity'+a.id" v-model="s.new_activities" :value="a.id" data-parsley-required :disabled="!canEditActivities" />
                                      {{ a.name }}
                                    </div>
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
    name:'Edit-Trail-Activities',
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
            trail: Object,
            trail_id: null,
            trail_name: '',
            allowed_activities:[],
            trail_sections:[],
            trail_activities:[],
            issuingVehicle: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            act:[],
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return this.trail && this.trail.name ? 'Edit Sections and Activities for '+this.trail.name : 'Edit Sections and Activities';
        }
    },
    watch: {
        trail_sections: function(){
            var removed_section=$(vm.trail_sections_before).not(vm.trail_sections).get();
            var added_section=$(vm.trail_sections).not(vm.trail_sections_before).get();
            vm.trail_sections_before=vm.trail_sections

            if(added_trail.length!=0){
                for(var i=0; i<added_trail.length; i++)
                { 
                  var found=false
                  for (var j=0; j<vm.trail_sections_activities.length; j++){
                    if(vm.trail_sections_activities[j].trail==added_trail[i]){ 
                      found = true;}
                  }
                  if(found==false)
                  {
                    data={
                    'trail': added_trail[i],
                    'activities': [],
                   }
                   vm.trail_sections_activities.push(data);
                  }
                }
              }
              if(removed_trail.length!=0){
                for(var i=0; i<removed_trail.length; i++)
                { 
                  for (var j=0; j<vm.trail_sections_activities.length; j++){
                    if(vm.trail_sections_activities[j].trail==removed_trail[i]){ 
                      vm.trail_sections_activities.splice(j,1)}
                  }
                }
              }
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            //console.log('after ok',vm.trail);
            
                //vm.sendData();
                var allowed_activities_id=[]
                var new_activities=[]
                for(var i=0; i<vm.trail.allowed_activities.length; i++){
                    allowed_activities_id.push(vm.trail.allowed_activities[i].id)
                }
                for(var j=0; j<vm.trail.sections.length; j++) {
                    if(vm.trail.sections[j].checked==true){
                        for(var k=0; k<vm.trail.sections[j].new_activities.length; k++){
                            if(allowed_activities_id.indexOf(vm.trail.sections[j].new_activities[k])==-1){
                                vm.trail.sections[j].new_activities.splice(k,1)
                            }
                        }
                        var data={
                            'section':vm.trail.sections[j].id,
                            'activities':vm.trail.sections[j].new_activities
                        }
                        new_activities.push(data)
                    }
                }
                vm.$emit('refreshTrailFromResponse',vm.trail.id, new_activities);

            vm.close();
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.trail={};
            this.trail.sections={};
            this.trail_id = null;
            this.errors = false;
            $('.has-error').removeClass('has-error');
            //this.validation_form.resetForm();
        },
        addnewdata: function(){
            let vm=this;
            for(var i=0;i<vm.trail.sections.length; i++){
                vm.trail.sections[i].checked= true;
                vm.trail.sections[i].new_activities=[];  
            }
        },
        fetchTrail: function(trail_id){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.trails,trail_id)).then((res) => {
                      vm.trail=res.body;                 
                },
              err => { 
                        console.log(err);
                  });
        },

        addFormValidations: function() {
        },
       eventListeners:function () {
       }
   },
   mounted:function () {
        let vm =this;
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
