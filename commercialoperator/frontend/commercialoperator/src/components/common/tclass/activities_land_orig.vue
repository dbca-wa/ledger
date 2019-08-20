<template lang="html">
  <div class="row">
    <div class="col-sm-12">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Activities and Location <small> (Parks)</small>
            <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
              <span class="glyphicon glyphicon-chevron-up pull-right "></span>
            </a>
          </h3>
        </div>
        <div class="panel-body collapse in" :id="pBody">
          <div class="borderDecoration col-sm-12">
          <form class="form-horizontal col-sm-12" name="personal_form" method="post">
            <label class="control-label"> Select the required access and activities</label>
          </form>
          <form>
            <div class="form-horizontal col-sm-6">
              <label class="control-label">Access</label>
              <div class="" v-for="a in accessTypes">
                <div class="form-check">
                  <input  class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_access" :value="a.id" data-parsley-required  :disabled="!canEditActivities" />
                  {{ a.name }}
                </div>
              </div>
            </div>
          </form>
          <form>
            <div class="form-horizontal col-sm-6">
              <label class="control-label">Activities</label>
              <div class="" v-for="a in activities">
                <div class="form-check">
                  <input  class="form-check-input" v-model="selected_activities" :value="a.id" ref="Checkbox" type="checkbox" :disabled="!canEditActivities"data-parsley-required  />
                  {{ a.name }}
                </div>
              </div>
            </div>
          </form>
          <!-- <form> -->

            <!-- testing start <div class="form-horizontal col-sm-12">
              <label class="control-label">Select Parks</label>
              <div class="form-check">
                  <input  class="form-check-input" @click="clickSelectAll" ref="Checkbox" type="checkbox" data-parsley-required  />
                  Select all parks from all regions
              </div>
              <div class="" v-for="r in api_regions">
                <div class="form-check">
                  <input @click="clickRegion($event, r)" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" :value="r.id" v-model="selected_regions" :id="'region'+r.id" data-parsley-required />
                  {{ r.name }} -->
                  <!-- <a data-toggle="collapse" :href="'#'+r.id" role="button" aria-expanded="true" aria controls="r.id" ><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                <!-- </div>
                <div class="col-sm-12" v-for="d in r.districts" :id="r.id">
                  <div class="form-check ">
                    <input @click="clickDistrict($event, d)" :value="d.id" class="form-check-input" ref="Checkbox" :id="'district'+d.id" v-model="selected_districts" type="checkbox" data-parsley-required />
                    {{ d.name }} -->
                   <!--  <a data-toggle="collapse" :href="'#'+d.id+r.id" role="button" aria-expanded="true" aria controls="d.id+r.id"><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                  <!-- </div>
                  <div class="" v-for="p in d.land_parks">
                    <div class="form-check col-sm-12">
                      <input name="selected_parks" v-model="selected_parks" :value="p.id" class="form-check-input" ref="Checkbox" type="checkbox" :id="'park'+p.id" data-parsley-required />
                    {{ p.name }}
                      <span><a @click="edit_activities(p.id, p.name)" target="_blank" class="control-label pull-right">Edit access and activities</a></span>
                    </div>
                  </div>
                </div>
              </div>
            </div> testing end--> 

            <div class="form-horizontal col-sm-12" >
              <label class="control-label">Select Parks</label>
              <div class="form-check">
                  <input  class="form-check-input" @click="clickSelectAll" ref="Checkbox" type="checkbox" :disabled="!canEditActivities" data-parsley-required  />
                  Select all parks from all regions
              </div>
              <div class="list-group list-group-root well">
              <div class="" v-for="r in api_regions">
                <div class="form-check col-sm-12 list-group-item" style="">
                  <input @click="clickRegion($event, r)" class="form-check-input" ref="Checkbox" type="checkbox" :value="r.id" v-model="selected_regions" :id="'region'+r.id" :disabled="!canEditActivities" data-parsley-required />
                  {{ r.name }}
                  <a data-toggle="collapse" :href="'#'+'r'+r.id" role="button" aria-expanded="true" aria controls="r.id" ><span class="glyphicon glyphicon-chevron-up pull-right "></span></a>
                </div>
                <div class="col-sm-12 list-group collapse" :id="'r'+r.id">
                  <div v-for="d in r.districts">
                  <div  style="padding-left: 30px;" class="form-check list-group-item col-sm-12">
                    <input @click="clickDistrict($event, d, r)" :value="d.id" class="form-check-input" ref="Checkbox" :id="'district'+d.id" v-model="selected_districts" type="checkbox" :disabled="!canEditActivities" data-parsley-required />
                    {{ d.name }}
                   <a data-toggle="collapse" :href="'#'+'d'+d.id" role="button" aria-expanded="true" aria controls="d.id"><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> 
                  </div>
                  <div class="list-group collapse"  :id="'d'+d.id">
                    <div class="form-check col-sm-12 list-group-item" style="padding-left: 45px;" v-for="p in d.land_parks">
                      <input name="selected_parks" v-model="selected_parks" :value="p.id" class="form-check-input" :ref="'park'+p.id" type="checkbox" :id="'park'+p.id" :disabled="!canEditActivities" data-parsley-required @click="clickPark($event, p, d)"/>
                    {{ p.name }}
                      <span><a @click="edit_activities(p.id, p.name)" target="_blank" class="control-label pull-right" v-if="canEditActivities">Edit access and activities</a></span>
                    </div>
                  </div>
                <!--</div>  -->
                </div>
                </div>
              </div>
            </div>
            </div>

            <div>{{selected_parks}}</div>
            <div>{{selected_parks_activities}}</div>
<!--           </form>

 -->      </div> 
          <div class="borderDecoration col-sm-12">
              <div  v-for="rd in required_documents_list">
                <div v-if="rd.can_view">
                  <label>{{rd.question}}</label>
                  <FileField :proposal_id="proposal.id" isRepeatable="true" :name="'req_doc'+rd.id" :required_doc_id="rd.id" label="Add Document" :id="'proposal'+proposal.id+'req_doc'+rd.id" :readonly="proposal.readonly"></FileField>
                </div>
              </div>
          </div>
          <div class="borderDecoration col-sm-12">
            <label class="control-label">Provide details of every vehicle you plan to use when accessing the parks</label>
              <VehicleTable :url="vehicles_url" :proposal="proposal" ref="vehicles_table"></VehicleTable>
          </div>
        </div>
      </div>
      
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Activities and Location <small> (Trails)</small>
            <a class="panelClicker" :href="'#'+tBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="tBody">
              <span class="glyphicon glyphicon-chevron-up pull-right "></span>
            </a>
          </h3>
        </div>

        <div class="panel-body collapse in" :id="tBody">
          <div>
            <div class="borderDecoration col-sm-12">
            <form class="form-horizontal col-sm-12" name="trails_form" method="post">
              <label class="control-label"> Select the required activities for trails</label>
            </form>
            <form>
              <div class="form-horizontal col-sm-6">
                <label class="control-label">Activities</label>
                <div class="" v-for="a in activities">
                  <div class="form-check">
                    <input  class="form-check-input" ref="Checkbox" type="checkbox" v-model="trail_activities" :value="a.id" data-parsley-required :disabled="!canEditActivities"/>
                      {{ a.name }}
                  </div>
                </div>
              </div>
            </form> 
            <div>
              <form>
                <div class="form-horizontal col-sm-12">
                  <label class="control-label">Select the long distance trails</label>
                  <div class="list-group list-group-root well">
                    <div class="" v-for="t in trails">
                      <div class="form-check col-sm-12 list-group-item">
                        <input   name="selected_trails" v-model="selected_trails" :value="{'trail': t.id,'sections': t.section_ids}" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities" />
                        {{ t.name }} <span><a @click="edit_sections(t)" target="_blank" class="control-label pull-right" v-if="canEditActivities">Edit section and activities</a></span>
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
          </div>
        </div>
      </div>
      <!-- <div>{{selected_trails}}</div>
      <div>{{selected_trails_activities}}</div> -->
      <div>
              <editParkActivities ref="edit_activities" :proposal="proposal" @refreshSelectionFromResponse="refreshSelectionFromResponse"></editParkActivities>
      </div>
      <div>
              <editTrailActivities ref="edit_sections" :proposal="proposal" @refreshTrailFromResponse="refreshTrailFromResponse"></editTrailActivities>
      </div>


    </div>
  </div>
</template>


<script>
import Vue from 'vue' 
import VehicleTable from '@/components/common/vehicle_table.vue'
import editParkActivities from './edit_park_activities.vue'
import editTrailActivities from './edit_trail_activities.vue'
import FileField from './required_docs.vue'
//import 'custom-event-polyfill'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            }
        },
        data:function () {
          let vm = this;
            return{
                pBody: 'pBody'+vm._uid,
                tBody: 'lBody'+vm._uid,
                values:null,
                accessTypes:null,
                api_regions:null,
                trails:null,
                required_documents_list: null,
                selected_parks:[],
                selected_parks_before:[],
                selected_access:[],
                selected_access_before:[],
                selected_activities:[],
                selected_activities_before:[],
                selected_trails:[],
                trail_activities:[],
                trail_activities_before:[],
                activities:[],
                access:[],
                selected_regions:[],
                selected_regions_before:[],
                selected_districts:[],
                select_all: false,
                //vehicles_url: api_endpoints.vehicles,
                vehicles_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vehicles'),
                selected_parks_activities:[],
                selected_trails_activities:[],
            }
        },
        components: {
          VehicleTable,
          editParkActivities,
          editTrailActivities,
          FileField,
        },
        computed:{

        },
        watch:{
          selected_regions: function(val){
            //WIP
            let vm=this;
            var added_region=$(vm.selected_regions).not(vm.selected_regions_before).get();
            //console.log(added_region)
          },
          selected_parks: function(){
            let vm = this;
            var removed_park=$(vm.selected_parks_before).not(vm.selected_parks).get();
            var added_park=$(vm.selected_parks).not(vm.selected_parks_before).get();
            vm.selected_parks_before=vm.selected_parks;

            var current_activities=vm.selected_activities
            var current_access=vm.selected_access

            if(vm.selected_parks_activities.length==0){
              for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_parks[i],
                  'activities': current_activities,
                  'access': current_access
                 }
                 vm.selected_parks_activities.push(data);
               }
            }
            else{
              if(added_park.length!=0){
                for(var i=0; i<added_park.length; i++)
                { 
                  var found=false
                  for (var j=0; j<vm.selected_parks_activities.length; j++){
                    if(vm.selected_parks_activities[j].park==added_park[i]){ 
                      found = true;}
                  }
                  if(found==false)
                  {
                    data={
                    'park': added_park[i],
                    'activities': current_activities,
                    'access': current_access
                   }
                   vm.selected_parks_activities.push(data);
                  }
                }
              }
              if(removed_park.length!=0){
                for(var i=0; i<removed_park.length; i++)
                { 
                  for (var j=0; j<vm.selected_parks_activities.length; j++){
                    if(vm.selected_parks_activities[j].park==removed_park[i]){ 
                      vm.selected_parks_activities.splice(j,1)}
                  }
                }
              }
            }
        },
        selected_activities: function(){
          let vm=this;
          var removed=$(vm.selected_activities_before).not(vm.selected_activities).get();
          var added=$(vm.selected_activities).not(vm.selected_activities_before).get();
          vm.selected_activities_before=vm.selected_activities;
          if(vm.selected_parks_activities.length==0){
            for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_parks[i],
                  'activities': vm.selected_activities,
                  'access': vm.selected_access
                 }
                 vm.selected_parks_activities.push(data);
               }
          }
          else{
            
            for (var i=0; i<vm.selected_parks_activities.length; i++)
            { 
              if(added.length!=0){
                for(var j=0; j<added.length; j++)
                {
                  if(vm.selected_parks_activities[i].activities.indexOf(added[j])<0){
                    vm.selected_parks_activities[i].activities.push(added[j]);
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  var index=vm.selected_parks_activities[i].activities.indexOf(removed[j]);
                  if(index!=-1){
                    vm.selected_parks_activities[i].activities.splice(index,1)
                  }
                }
              }
            }
          }
          vm.checkRequiredDocuements(vm.selected_parks_activities)
        },
        selected_access: function(){
          let vm=this;
          var removed=$(vm.selected_access_before).not(vm.selected_access).get();
          var added=$(vm.selected_access).not(vm.selected_access_before).get();
          vm.selected_access_before=vm.selected_access;
          if(vm.selected_parks_activities.length==0){
            for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_parks[i],
                  'activities': vm.selected_activities,
                  'access': vm.selected_access
                 }
                 vm.selected_parks_activities.push(data);
               }
          }
          else{
            for (var i=0; i<vm.selected_parks_activities.length; i++)
            { 
              if(added.length!=0){
               
                for(var j=0; j<added.length; j++)
                {
                  if(vm.selected_parks_activities[i].access.indexOf(added[j])<0){
                    vm.selected_parks_activities[i].access.push(added[j]);
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  var index=vm.selected_parks_activities[i].access.indexOf(removed[j]);
                  if(index!=-1){
                    vm.selected_parks_activities[i].access.splice(index,1)
                  }
                }
              }
            }
          }
        },
        selected_parks_activities: function(){
            let vm=this;
            vm.checkRequiredDocuements(vm.selected_parks_activities)
            if (vm.proposal){
              vm.proposal.selected_parks_activities=vm.selected_parks_activities;
            }
        },
        selected_trails_activities: function(){
            let vm=this;
            if (vm.proposal){
              vm.proposal.selected_trails_activities=vm.selected_trails_activities;
            }
        },
        selected_trails: function(){
            let vm=this;
            if (vm.proposal){
              vm.proposal.trails=vm.selected_trails;
            }

            var removed_trail=$(vm.selected_trails_before).not(vm.selected_trails).get();
            var added_trail=$(vm.selected_trails).not(vm.selected_trails_before).get();
            vm.selected_trails_before=vm.selected_trails;

            var current_activities=vm.trail_activities

            if(vm.selected_trails_activities.length==0){
              for (var i = 0; i < vm.selected_trails.length; i++) {
                 var data=null;
                 // data={
                 //  'trail': vm.selected_trails[i],
                 //  'activities': current_activities
                 // }
                 var section_activities=[];

                 for (var j=0; j<vm.selected_trails[i].sections.length; j++){
                  var section_data={
                    'section': vm.selected_trails[i].sections[j],
                    'activities': current_activities
                  }
                  section_activities.push(section_data)
                 }
                 data={
                  'trail': vm.selected_trails[i].trail,
                  'activities': section_activities 
                 }
                 vm.selected_trails_activities.push(data);
               }
            }
            else{
              if(added_trail.length!=0){
                for(var i=0; i<added_trail.length; i++)
                { 
                  var found=false
                  for (var j=0; j<vm.selected_trails_activities.length; j++){
                    //console.log(added_trail[i])
                    if(vm.selected_trails_activities[j].trail==added_trail[i].trail){ 
                      found = true;}
                  }
                  if(found==false)
                  {//original data object
                    var section_activities=[];
                    for(var k=0; k<added_trail[i].sections.length; k++){
                      var section_data={
                      'section': added_trail[i].sections[k],
                      'activities': current_activities
                      }
                      section_activities.push(section_data)
                    }
                    data={
                    'trail': added_trail[i].trail,
                    'activities': section_activities,                   }
                    // data={
                    // 'trail': added_trail[i].trail,
                    // 'activities':{
                    //   'zone': added_trail[i].zones,
                    //   'activities': current_activities,
                    // }
                    //}
                   vm.selected_trails_activities.push(data);
                  }
                }
              }
              if(removed_trail.length!=0){
                for(var i=0; i<removed_trail.length; i++)
                { 
                  for (var j=0; j<vm.selected_trails_activities.length; j++){
                    if(vm.selected_trails_activities[j].trail==removed_trail[i].trail){
                      vm.selected_trails_activities.splice(j,1)}
                  }
                }
              }
            }
          },
        trail_activities: function(){
          let vm=this;
          var removed=$(vm.trail_activities_before).not(vm.trail_activities).get();
          var added=$(vm.trail_activities).not(vm.trail_activities_before).get();
          vm.trail_activities_before=vm.trail_activities;
          if(vm.selected_trails_activities.length==0){
            for (var i = 0; i < vm.selected_trails.length; i++) {
                 var data=null;
                 data={
                  'trail': vm.selected_trails[i],
                  'activities': vm.trail_activities
                 }
                 vm.selected_trails_activities.push(data);
               }
          }
          else{
            for (var i=0; i<vm.selected_trails_activities.length; i++)
            { 
              if(added.length!=0){
               
                for(var j=0; j<added.length; j++)
                {
                  // if(vm.selected_trails_activities[i].activities.indexOf(added[j])<0){
                  //   vm.selected_trails_activities[i].activities.push(added[j]);
                  // }
                  for(var k=0; k<vm.selected_trails_activities[i].activities.length; k++){
                    if(vm.selected_trails_activities[i].activities[k].activities.indexOf(added[j])<0){
                    vm.selected_trails_activities[i].activities[k].activities.push(added[j]);
                    }
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  // var index=vm.selected_trails_activities[i].activities.indexOf(removed[j]);
                  // if(index!=-1){
                  //   vm.selected_trails_activities[i].activities.splice(index,1)
                  // }
                  for(var k=0; k<vm.selected_trails_activities[i].activities.length; k++){
                    var index=vm.selected_trails_activities[i].activities[k].activities.indexOf(removed[j]);
                    if(index!=-1){
                      vm.selected_trails_activities[i].activities[k].activities.splice(index,1)
                    }
                  }

                }
              }
            }
          }
        },
        },
        methods:{
          fetchRegions: function(){
            let vm = this;

            vm.$http.get(api_endpoints.regions).then((response) => { 
            vm.api_regions = response.body;
            },(error) => {
            console.log(error);
            })
          },
          fetchTrails: function(){
            let vm = this;
            vm.$http.get('/api/trails.json').then((response) => {
            vm.trails = response.body;
            
            },(error) => {
            console.log(error);
            })
          },
          fetchRequiredDocumentList: function(){
            let vm = this;
            vm.$http.get('/api/required_documents.json').then((response) => {
            vm.required_documents_list = response.body;
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
              vm.checkRequiredDocuements(vm.selected_parks_activities)
              //console.log('park',vm.selected_parks_activities)
            }
            },(error) => {
            console.log(error);
            })

          },
          checkRequiredDocuements: function(selected_parks_activities){
            let vm=this;
            //Check if the combination of selected park and activities require a document to be attahced
            if(vm.required_documents_list){
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
            }

            for(var i=0; i<selected_parks_activities.length; i++){
              for(var j=0; j<vm.required_documents_list.length; j++){
                if(vm.required_documents_list[j].park!=null){
                  if(vm.required_documents_list[j].activity==null){
                    if(vm.required_documents_list[j].park== selected_parks_activities[i].park){
                      vm.required_documents_list[j].can_view=true;
                    }
                  }
                  else{
                    for(var k=0; k<selected_parks_activities[i].activities.length; k++){
                      if(vm.required_documents_list[j].activity== selected_parks_activities[i].activities[k]){
                      vm.required_documents_list[j].can_view=true;
                      }
                    }
                  }
                }
                else if(vm.required_documents_list[j].activity!=null){
                  for(var k=0; k<selected_parks_activities[i].activities.length; k++){
                      if(vm.required_documents_list[j].activity== selected_parks_activities[i].activities[k]){
                        vm.required_documents_list[j].can_view=true;
                      }
                  }
                }
              }
            }
          }
          },
          edit_activities: function(p_id, p_name){
            let vm=this;
            for (var j=0; j<vm.selected_parks_activities.length; j++){
              if(vm.selected_parks_activities[j].park==p_id){ 
                this.$refs.edit_activities.park_activities= vm.selected_parks_activities[j].activities;
                this.$refs.edit_activities.park_access= vm.selected_parks_activities[j].access
              }
            }
            this.$refs.edit_activities.park_id=p_id;
            this.$refs.edit_activities.park_name=p_name;
            this.$refs.edit_activities.fetchAllowedActivities(p_id)
            this.$refs.edit_activities.fetchAllowedAccessTypes(p_id)
            this. $refs.edit_activities.isModalOpen = true;
          },
          edit_sections: function(trail){
            let vm=this;
            //inserting a temporary variables checked and new_activities to store and display selected activities for each section.
            for(var l=0; l<trail.sections.length; l++){
              trail.sections[l].checked=false;
              trail.sections[l].activities=[];
            }

            for (var i=0; i<vm.selected_trails_activities.length; i++){
              if(vm.selected_trails_activities[i].trail==trail.id){
                for(var j=0; j<vm.selected_trails_activities[i].activities.length; j++){
                  for(var k=0; k<trail.sections.length; k++){
                    if (trail.sections[k].id==vm.selected_trails_activities[i].activities[j].section){
                      trail.sections[k].checked=true;
                      trail.sections[k].new_activities=vm.selected_trails_activities[i].activities[j].activities
                    }
                  }
                } 
              }
            }
            //console.log(trail);
            this.$refs.edit_sections.trail=trail;
            this. $refs.edit_sections.isModalOpen = true;
          },
          refreshSelectionFromResponse: function(park_id, park_activities, park_access){
              let vm=this;
              for (var j=0; j<vm.selected_parks_activities.length; j++){
              if(vm.selected_parks_activities[j].park==park_id){ 
                vm.selected_parks_activities[j].activities= park_activities;
                vm.selected_parks_activities[j].access= park_access;
              }
            }
            vm.checkRequiredDocuements(vm.selected_parks_activities)
          },
          refreshTrailFromResponse: function(trail_id, new_activities){
              let vm=this;
              for (var j=0; j<vm.selected_trails_activities.length; j++){
              if(vm.selected_trails_activities[j].trail==trail_id){ 
                vm.selected_trails_activities[j].activities= new_activities;
              }
            }
          },
          clickSelectAll: function(e){
            let vm=this;
            var checked=e.target.checked;
            var new_regions=[];
            var new_district=[];
            var new_parks = [];
            if(checked){
              for(var i=0; i<vm.api_regions.length; i++){
                new_regions.push(vm.api_regions[i].id);
                //change the inderminate and checked states of region checkboxes
                var region = $("#region"+vm.api_regions[i].id)[0]
                region.checked=true;
                region.indeterminate=false;

                for (var j=0; j<vm.api_regions[i].districts.length; j++){
                  new_district.push(vm.api_regions[i].districts[j].id);
                  //change the inderminate and checked states of district checkboxes
                  var district = $("#district"+vm.api_regions[i].districts[j].id)[0]
                    district.checked=true;
                    district.indeterminate=false;
                  for (var k=0; k<vm.api_regions[i].districts[j].land_parks.length; k++){
                    new_parks.push(vm.api_regions[i].districts[j].land_parks[k].id);
                  }
                }
              }
              vm.selected_regions=new_regions;
              vm.selected_districts=new_district;
              vm.selected_parks=new_parks;
            }
          if(!checked){
            for(var i=0; i<vm.api_regions.length; i++){
              var region = $("#region"+vm.api_regions[i].id)[0]
                region.checked=false;
                region.indeterminate=false;
                for (var j=0; j<vm.api_regions[i].districts.length; j++){
                    var district = $("#district"+vm.api_regions[i].districts[j].id)[0]
                    district.checked=false;
                    district.indeterminate=false;
                }
            }
            vm.selected_regions=[];
            vm.selected_districts=[];
            vm.selected_parks=[];
          }
          },
          clickRegion: function(e, r){
            var checked=e.target.checked;
            if(checked){
              for(var i=0; i<r.districts.length; i++){
                var index=this.selected_districts.indexOf(r.districts[i].id);
                if(index==-1)
                {
                  this.selected_districts.push(r.districts[i].id)
                  var district = $("#district"+r.districts[i].id)[0]
                  district.checked=true;
                  district.indeterminate=false;
                  for(var j=0; j<r.districts[i].land_parks.length; j++){
                    var index_park=this.selected_parks.indexOf(r.districts[i].land_parks[j].id);
                    if(index_park==-1)
                    {
                      var s = helpers.copyObject(this.selected_parks);
                      s.push(r.districts[i].land_parks[j].id);
                      this.selected_parks=s
                    }
                  }   
                }
              }
            }
            else{
              for(var i=0; i<r.districts.length; i++){
                var index=this.selected_districts.indexOf(r.districts[i].id);
                if(index!=-1){
                  this.selected_districts.splice(index,1)
                  var district = $("#district"+r.districts[i].id)[0]
                  district.checked=false;
                  district.indeterminate=false;
                  for(var j=0; j<r.districts[i].land_parks.length; j++){
                    var index_park=this.selected_parks.indexOf(r.districts[i].land_parks[j].id);
                    if(index_park!=-1)
                    {
                      var s = helpers.copyObject(this.selected_parks);
                      s.splice(index_park,1);
                      this.selected_parks=s
                    }
                  }

                }
              }
            }
          },
          clickDistrict: function(e, d, r){
            let vm=this;
            var original_region=r;
            var checked=e.target.checked;
            if(checked){
              for(var i=0; i<d.land_parks.length; i++){
                var index=this.selected_parks.indexOf(d.land_parks[i].id);
                if(index==-1)
                {
                  var r = helpers.copyObject(this.selected_parks);
                  r.push(d.land_parks[i].id);
                  this.selected_parks=r
                  
                }
              }
            }
            else{
              if(e.target.indeterminate==false){
              for(var i=0; i<d.land_parks.length; i++){
                var index=this.selected_parks.indexOf(d.land_parks[i].id);
                if(index!=-1){
                  var r = helpers.copyObject(this.selected_parks);
                  r.splice(index,1);
                  this.selected_parks=r
                  //this.selected_parks.splice(index,1)
                }
              }
            }
            }
            this.handleDistrictChange(e,d,original_region);
          },

          handleDistrictChange: function(e,d, r){
            //console.log('here')
            var inder_state=false;
            var checked_state=false;
            var checked_all=true;
            var unchecked_all=true;
            var elem=$("#region"+r.id)[0]
            inder_state=elem.indeterminate
            checked_state=elem.checked
            if(e.target.checked){
              if(!checked_state){
                for(var i=0; i<r.districts.length; i++){
                  var district = $("#district"+r.districts[i].id)[0]
                  if(district.checked==false){
                    checked_all=false;
                  }
                }
                if(checked_all){
                  elem.indeterminate=false;
                  elem.checked=true;
                  var index=this.selected_regions.indexOf(r.id);
                  if(index==-1){
                    this.selected_regions.push(r.id)
                  }
                }
                else{
                  elem.indeterminate=true;
                  elem.checked=false;
                }
              }              
            }
            else{//if unselected
              if(e.target.indeterminate==false){
              for(var i=0; i<r.districts.length; i++){
                  var district = $("#district"+r.districts[i].id)[0]
                  if(district.checked==true){
                    unchecked_all=false;
                  }
                }
                if(unchecked_all){
                  elem.indeterminate=false;
                  elem.checked=false;
                  var index=this.selected_regions.indexOf(r.id);
                  if(index>-1){
                    this.selected_regions.splice(index,1)
                  }
                }
                else{
                  var index=this.selected_regions.indexOf(r.id);
                  if(index>-1){
                    this.selected_regions.splice(index,1)
                  }
                  elem.indeterminate=true;
                  elem.checked=false;
                }
              }
              else{
                elem.indeterminate=true;
                  elem.checked=false;
              }
            }
          },
          

          clickPark: function(e,p,d){
            var inder_state=false;
            var checked_state=false;
            var checked_all=true;
            var unchecked_all=true;
            var elem=$("#district"+d.id)[0]
            inder_state=elem.indeterminate
            checked_state=elem.checked
            if(e.target.checked){
              if(!checked_state){
                for(var i=0; i<d.land_parks.length; i++){
                  var park = $("#park"+d.land_parks[i].id)[0]
                  if(park.checked==false){
                    checked_all=false;
                  }
                }
                if(checked_all){
                  elem.indeterminate=false;
                  elem.checked=true;
                  var index=this.selected_districts.indexOf(d.id);
                  if(index==-1){
                    this.selected_districts.push(d.id)
                  }
                }
                else{
                  elem.indeterminate=true;
                  elem.checked=false;
                }
              }              
            }
            else{//if unselected
              for(var i=0; i<d.land_parks.length; i++){
                  var park = $("#park"+d.land_parks[i].id)[0]
                  if(park.checked==true){
                    unchecked_all=false;
                  }
                }
                if(unchecked_all){
                  elem.indeterminate=false;
                  elem.checked=false;
                  var index=this.selected_districts.indexOf(d.id);
                  if(index>-1){
                    this.selected_districts.splice(index,1)
                  }
                }
                else{
                  var index=this.selected_districts.indexOf(d.id);
                  if(index>-1){
                    this.selected_districts.splice(index,1)
                  }
                  elem.indeterminate=true;
                  elem.checked=false;
                }
            }
            var event = document.createEvent('HTMLEvents');
            event.initEvent('click', true, true);
            elem.dispatchEvent(event);
          },
          
          find_recurring: function(array){
            var common=new Map();
            array.forEach(function(obj){
             var values=Object.values(obj)[0];
             values.forEach(function(val){
                 common.set(val,(common.get(val)||0)+1);
             });
            });
            var result=[];
            common.forEach(function(appearance,el){
              if(appearance===array.length){
               result.push(el);
              }
            });
            return result;
        },

        store_trails: function(trails){
          let vm=this;
          var all_activities=[] //to store all activities for all sections so can find recurring onees to display selected_activities
          var trail_list=[]
          for (var i = 0; i < trails.length; i++) {
              var current_trail=trails[i].trail.id
              var current_activities=[]
              var current_sections=[]
              
              for (var j = 0; j < trails[i].sections.length; j++) {
                var trail_activities=[];
                for (var k = 0; k < trails[i].sections[j].trail_activities.length; k++) {
                  trail_activities.push(trails[i].sections[j].trail_activities[k].activity);
                }
                var data_section={
                  'section': trails[i].sections[j].section,
                  'activities': trail_activities
                }
                current_activities.push(data_section)
                all_activities.push({'key': trail_activities})
                //current_sections.push(trails[i].sections[j].section)
              }
               
               var data={
                'trail': current_trail,
                'activities': current_activities 
               }
               vm.selected_trails_activities.push(data)
               
            }
            
          for (var i=0; i<trails.length; i++)
            { 
              
              trail_list.push({'trail':trails[i].trail.id, 'sections':trails[i].trail.section_ids})
            }
          vm.selected_trails=trail_list
          //console.log(trail_list)
          vm.trail_activities = vm.find_recurring(all_activities)
        },
        createParkEvent: function(selected_parks){
          let vm= this;
          for(var i=0;i<selected_parks.length; i++){
            var elem=$("#park"+selected_parks[i])[0];
            var event = document.createEvent('HTMLEvents');
            event.initEvent('click', true, true);
            elem.dispatchEvent(event);
          }
        },
        _createParkEvent: function(selected_parks){
          let vm= this;
          for(var i=0;i<selected_parks.length; i++){
            //$("#park"+selected_parks[i]).prop( "checked", true );
            document.getElementById("park"+selected_parks[i]).checked = true
          }
        },

        eventListeners: function(){
            
        },
    },

        mounted: function() {

            let vm = this;
            vm.proposal.selected_trails_activities=[];
            vm.proposal.selected_parks_activities=[];
            //vm.proposal.marine_parks_activities=[];
            vm.fetchRequiredDocumentList();
            Vue.http.get('/api/access_types.json').then((res) => {
                      vm.accessTypes=res.body;                 
                },
              err => { 
                        console.log(err);
                  }); 
            Vue.http.get('/api/land_activities.json').then((res) => {
                      vm.activities=res.body;                 
                },
              err => { 
                        console.log(err);
                  }); 
            //vm.fetchRegions(); 
            //vm.fetchTrails();
            //vm.fetchRequiredDocumentList();

            for (var i = 0; i < vm.proposal.land_parks.length; i++) {
              var current_park=vm.proposal.land_parks[i].park.id
              var current_activities=[]
              var current_access=[]
              for (var j = 0; j < vm.proposal.land_parks[i].land_activities.length; j++) {
                current_activities.push(vm.proposal.land_parks[i].land_activities[j].activity.id);
              }
               for (var k = 0; k < vm.proposal.land_parks[i].access_types.length; k++){
                current_access.push(vm.proposal.land_parks[i].access_types[k].access_type.id);
               }
               var data={
                'park': current_park,
                'activities': current_activities,
                'access':current_access  
               }
               vm.selected_parks_activities.push(data)
            }

            var activity_list=[]
            var access_list=[]
            var park_list=[]
            for (var i=0; i<vm.selected_parks_activities.length; i++)
            { 
              park_list.push(vm.selected_parks_activities[i].park);
              activity_list.push({'key' : vm.selected_parks_activities[i].activities});
              access_list.push({'key' : vm.selected_parks_activities[i].access});
            }

            vm.selected_activities = vm.find_recurring(activity_list)
            vm.selected_access=vm.find_recurring(access_list)
            vm.selected_parks=park_list
            
            this.$nextTick(() => {
              let vm=this;
              //vm.eventListeners();
            });
            //vm.eventListeners();

            vm.store_trails(vm.proposal.trails);


            // for (var i = 0; i < vm.proposal.trails.length; i++) {
            //   this.selected_trails.push(vm.proposal.trails[i].trail.id);
            // } 

            
            
            $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
              //console.log(this);
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
            }); 

            //check why this is not working for list items
            // var list_item=$('.list-group-item')
            // var a_item=list_item.children[ 1 ]
            // $(a_item).on( 'click', function () {
            //   console.log(this);
            //   var chev2 = $( this ).children()[ 0 ];
            //   window.setTimeout( function () {
            //       $( chev2 ).toggleClass( "glyphicon-chevron-up glyphicon-chevron-down" );
            // }, 100 );
            // }); 
            // $('.list-group-item').on('click', function(){
            //   console.log(this);
            //   $('.glyphicon', this).toggleClass('glyphicon-chevron-up').toggleClass('glyphicon-chevron-down');
            // })
        },
        updated: function(){
          let vm=this;
          if(vm.api_regions){ //check if Regions, Parks and districts are loaded in DOM
                vm.createParkEvent(vm.selected_parks);           
          }
          /*
          */
        },
        created: function(){
          let vm=this;
          vm.fetchRegions(); 
          vm.fetchTrails();
        },

    }
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 5px;
    margin-top: 5px;
}
.just-padding {
    padding: 15px;
}

.list-group {
  padding: 0;
}

.list-group.list-group-root {
    padding: 0;
    overflow: hidden;
}

.list-group.list-group-root .list-group {
    margin-bottom: 0;
}

.list-group.list-group-root .list-group-item {
    border-radius: 0;
    border-width: 1px 0 0 0;
}

.list-group.list-group-root > .list-group-item:first-child {
    border-top-width: 0;
}

.list-group.list-group-root > .list-group > .list-group-item {
    padding-left: 30px;
}

.list-group.list-group-root > .list-group > .list-group > .list-group-item {
    padding-left: 45px;
}

.list-group-item .glyphicon {
    margin-right: 5px;
}
</style>

