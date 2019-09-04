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
                <form>
                    <div class="col-sm-12" >
                        <div>
                            <!--<pre>{{ selected_access }}</pre>-->
                            <label class="control-label">Select the required access</label>
                                <!--
                                The below 3 are equivalent - require an event emitted fro child component -'this.$emit("update:value", vm.value)', (or 'this.$emit("value", vm.value)' )
                                <TreeSelect ref="selected_access" :proposal="proposal" @value="selected_access" :value="selected_access" :options="land_access_options" :default_expand_level="1"></TreeSelect>
                                <TreeSelect ref="selected_access" :proposal="proposal" @value="selected_access=$event" :value="selected_access" :options="land_access_options" :default_expand_level="1"></TreeSelect>
                                <TreeSelect ref="selected_access" :proposal="proposal" :value.sync="selected_access" :options="land_access_options" :default_expand_level="1"></TreeSelect>
                                -->
                                <TreeSelect ref="selected_access" :proposal="proposal" :value.sync="selected_access" :options="land_access_options" :default_expand_level="1" :disabled="!canEditActivities"></TreeSelect>
                        </div>
                    </div>
                </form>
            </div>

            <div class="borderDecoration col-sm-12">
                <form>
                    <div class="col-sm-12" >
                        <div>
                            <!--<pre>{{ selected_activities }}</pre>-->
                            <label class="control-label">Select the required activities</label>
                            <TreeSelect :proposal="proposal" :value.sync="selected_activities" :options="land_activity_options" :default_expand_level="1" :disabled="!canEditActivities"></TreeSelect>
                        </div>
                    </div>
                </form>
            </div>

            <div class="borderDecoration col-sm-12">
                <form>
                    <div class="col-sm-12" >
                        <div>
                            <!--<pre>{{ selected_parks }}</pre>-->
                            <label class="control-label">Select Parks</label>
                            <TreeSelect :proposal="proposal" :value.sync="selected_parks" :options="park_options" :default_expand_level="1" allow_edit="true" :disabled="!canEditActivities"></TreeSelect>
                        </div>
                    </div>
                </form>
            </div> 

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
                  <VehicleTable :url="vehicles_url" :proposal="proposal" :access_types="land_access_types" ref="vehicles_table"></VehicleTable>
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
                <form>
                    <div class="col-sm-12" >
                        <div>
                            <!--<pre>{{ trail_activities }}</pre>-->
                            <!--<pre>{{ selected_trails_activities }}</pre>-->
                            <label class="control-label">Select the required activities for trails</label>
                            <TreeSelect :proposal="proposal" :value.sync="trail_activities" :options="trail_activity_options" :default_expand_level="1" :disabled="!canEditActivities"></TreeSelect>
                        </div>
                    </div>
                </form>
            </div>

            <div class="borderDecoration col-sm-12">
                <form>
                    <div class="col-sm-12" >
                        <div>
                            <!--<pre>{{ selected_trail_ids }}</pre>-->
                            <!-- <label class="control-label">Select the required activities</label> -->
                            <label class="control-label">Select the long distance trails</label>
                            <TreeSelect :proposal="proposal" :value.sync="selected_trail_ids" :options="trail_options" :default_expand_level="1" open_direction="top" allow_edit="true" :disabled="!canEditActivities"></TreeSelect>
                        </div>
                    </div>
                </form>
            </div>

            <!--
            <div>Selected_Parks: {{selected_parks}}</div><br>
            <div>Selected_Parks_Activities: {{selected_parks_activities}}</div>
            <div>Trail: {{selected_trails}}</div>
            <div>Activities: {{selected_trails_activities}}</div>
            -->
            <!--
            <div>Trail_actvities: {{trail_activities}}</div><br>
            <div>Selected_Trail: {{selected_trails}}</div><br>
            <div>Selected_Trailss_Activities: {{selected_trails_activities}}</div>
            -->


          </div>
        </div>
      </div>


      <div>
              <editParkActivities ref="edit_activities" :proposal="proposal" :canEditActivities="canEditActivities" @refreshSelectionFromResponse="refreshSelectionFromResponse"></editParkActivities>
      </div>
      <div>
              <editTrailActivities ref="edit_sections" :proposal="proposal" :canEditActivities="canEditActivities" @refreshTrailFromResponse="refreshTrailFromResponse"></editTrailActivities>
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
import TreeSelect from '@/components/forms/treeview.vue'
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
                park_options: [],
                land_access_options: [],
                land_activity_options: [],
                trail_options: [],
                trail_activity_options: [],
                land_access_types: [],
                added_trail_id: [],
                removed_trail_id: [],
                
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
                selected_trail_ids:[],
                selected_trail_ids_before:[],
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
          TreeSelect,
        },
        computed:{

        },
        watch:{
          selected_trail_ids: function(){
            let vm=this;
            //if (vm.proposal){
            //  vm.proposal.trails=vm.selected_trails;
            //}

            vm.selected_trails = []
            for (var i = 0; i < vm.selected_trail_ids.length; i++) {
                var data = vm.get_selected_trail_data(vm.selected_trail_ids[i] )
                if (data !== null) {
                    vm.selected_trails.push( data )
                }
            }

            try {
                var removed_trail_id=$(vm.selected_trail_ids_before).not(vm.selected_trail_ids).get();
            } catch (error) {
                console.log('removed_trail: ' + error)
            }

            try {
                var added_trail_id=$(vm.selected_trail_ids).not(vm.selected_trail_ids_before).get();
            } catch (error) {
                console.log('added_trail: ' + error)
            }
            vm.selected_trail_ids_before=vm.selected_trail_ids;

            var current_activities=vm.trail_activities

            if(vm.selected_trails_activities.length==0){
              for (var i = 0; i < vm.selected_trails.length; i++) {
                 var data=null;
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
              if(added_trail_id.length!=0){
                for(var i=0; i<added_trail_id.length; i++) {
                  var found=false
                  for (var j=0; j<vm.selected_trails_activities.length; j++){
                        //console.log(added_trail[i])
                        if(vm.selected_trails_activities[j].trail==added_trail_id[i]){
                          found = true;
                        }
                  }
                  if(found==false) {
                    //original data object
                    var section_activities=[];
                    var trail_data = vm.get_selected_trail_data(added_trail_id[i] )
                    if (trail_data !== null) {
                        for(var k=0; k<trail_data.sections.length; k++){
                          var section_data={
                          'section': trail_data.sections[k],
                          'activities': current_activities
                          }
                          section_activities.push(section_data)
                        }
                        data={
                          'trail': added_trail_id[i],
                          'activities': section_activities
                        }
                    }
                    vm.selected_trails_activities.push(data);
                  }
                }
              }
              if(removed_trail_id.length!=0){
                for(var i=0; i<removed_trail_id.length; i++)
                { 
                  for (var j=0; j<vm.selected_trails_activities.length; j++){
                    if(vm.selected_trails_activities[j].trail==removed_trail_id[i]){
                      vm.selected_trails_activities.splice(j,1)}
                  }
                }
              }
            }
            if (vm.proposal){
              vm.proposal.trails=vm.selected_trails;
              vm.proposal.selected_trails_activities=vm.selected_trails_activities;
            }
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
              vm.proposal.selected_land_access=vm.selected_access;
              vm.proposal.selected_land_activities=vm.selected_activities;
            }
        },
        selected_trails_activities: function(){
            let vm=this;

            if (vm.proposal){
              vm.proposal.selected_trails_activities=vm.selected_trails_activities;
            }
        },
        trail_activities: function(){
          let vm=this;
          var removed=$(vm.trail_activities_before).not(vm.trail_activities).get();
          var added=$(vm.trail_activities).not(vm.trail_activities_before).get();
          vm.trail_activities_before=vm.trail_activities;
          if(vm.selected_trails_activities.length==0){
            for (var i = 0; i < vm.selected_trail_ids.length; i++) {
                 var data=null;
                 data={
                  'trail': vm.selected_trail_ids[i],
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
          get_selected_trail_data:function(trail_id){
            let vm = this;
            for (var i=0; i<vm.trails.length; i++) {
              if (vm.trails[i].id == trail_id) {
                //console.log(vm.trails[i].section_ids)
                return {'trail': trail_id, 'sections': vm.trails[i].section_ids}
              }
            }
            return null;
          },
          get_selected_trail_ids:function(node){
            let vm = this;

            var ids = []
            for (var i=0; i<vm.selected_trails.length; i++) {
                ids.push( vm.selected_trails[i].trail )
            }
            return ids.filter(function(item, pos) { return ids.indexOf(item) == pos;  }) // returns unique array ids
          },

          fetchParkTreeview: function(){
            let vm = this;

            //console.log('treeview_url: ' + api_endpoints.tclass_container_land)
            vm.$http.get(api_endpoints.tclass_container_land)
            .then((response) => {
                vm.park_options = [
                    {
                        'id': 'All',
                        'name':'Select all parks from all regions',
                        'children': response.body['land_parks'] // land_parks --> regions/districts/parks nested json
                    }
                ]
                vm.api_regions = response.body['land_parks']

                vm.land_access_options = [
                    {
                        'id': 'All',
                        'name':'Select all',
                        'children': response.body['access_types']
                    }
                ]
                vm.land_access_types = response.body['access_types'] // needed to pass to Vehicle component
                vm.access = response.body['access_types'] // needed to pass to Vehicle component

                vm.land_activity_options = [
                    {
                        'id': 'All',
                        'name':'Select all',
                        'children': response.body['land_activity_types']
                    }
                ]
                vm.trail_activity_options = vm.land_activity_options
                vm.activities = response.body['land_activity_types'] // needed to pass to Vehicle component

                vm.trail_options = [
                    {
                        'id': 'All',
                        'name':'Select all',
                        'children': response.body['trails']
                    }
                ]
                vm.trails = response.body['trails']
                vm.required_documents_list = response.body['land_required_documents']
                vm.fetchRequiredDocumentList();

            },(error) => {
                console.log(error);
            })
          },
          fetchRequiredDocumentList: function(){
            let vm = this;
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
              vm.checkRequiredDocuements(vm.selected_parks_activities)
            }
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

                      // if(vm.required_documents_list[j].activity== selected_parks_activities[i].activities[k]){
                      // vm.required_documents_list[j].can_view=true;
                      // }
                      if(vm.required_documents_list[j].park== selected_parks_activities[i].park){
                        if(vm.required_documents_list[j].activity== selected_parks_activities[i].activities[k]){
                            vm.required_documents_list[j].can_view=true;
                          }
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
          edit_activities_child_test:function(node){
              alert("IN PARENT:  park_id: " + node.raw.id + ", park_name: " + node.raw.label );
          },
          edit_activities: function(node){
            let vm=this;
            var p_id = node.raw.id;
            var p_name = node.raw.name;

            for (var j=0; j<vm.selected_parks_activities.length; j++){
              if(vm.selected_parks_activities[j].park==p_id){
                this.$refs.edit_activities.park_activities = vm.selected_parks_activities[j].activities;
                this.$refs.edit_activities.park_access = vm.selected_parks_activities[j].access
              }
            }
            this.$refs.edit_activities.park_id=p_id;
            this.$refs.edit_activities.park_name=p_name;
            this.$refs.edit_activities.fetchAllowedActivities(p_id)
            this.$refs.edit_activities.fetchAllowedAccessTypes(p_id)
            this.$refs.edit_activities.isModalOpen = true;
          },
          edit_sections: function(node){
            let vm=this;
            var trail = node.raw;
            //trail['id']=node.id

            console.log('Trail 0: ' + JSON.stringify(trail))
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
            console.log('Trail: ' + JSON.stringify(trail))
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
          var all_activities=[] //to store all activities for all sections so can find recurring ones to display selected_activities
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
        eventListeners: function(){
        },
    },

        mounted: function() {

            let vm = this;
            vm.fetchParkTreeview()


            vm.proposal.selected_trails_activities=[];
            vm.proposal.selected_parks_activities=[];
            //vm.proposal.marine_parks_activities=[];
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

            //vm.selected_activities = vm.proposal.land_activities
            //vm.selected_access=vm.proposal.land_access
            vm.selected_activities = vm.find_recurring(activity_list)
            vm.selected_access=vm.find_recurring(access_list)
            vm.selected_parks=park_list

            this.$nextTick(() => {
              let vm=this;
              //vm.eventListeners();
            });

            vm.store_trails(vm.proposal.trails);
            //vm.trail_activities = vm.proposal.trail_activities
            //vm.selected_trail_ids = vm.proposal.trail_section_activities
            //vm.clear_selected_trails_activities()
            vm.selected_trail_ids = vm.get_selected_trail_ids()
            vm.selected_trail_ids_before = vm.selected_trail_ids

            $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
              //console.log(this);
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
            }); 
        },
        updated: function(){
        },
        created: function(){
          //let vm=this;
          //vm.fetchRegions(); 
          //vm.fetchTrails();
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

/*
.myselect {
    position: relative;
    margin-bottom: 0;
    padding: 0;
}

.dropdown-pane {
  position: relative;
    margin-bottom: 0;
    padding: 0;
}
*/

</style>

