<template lang="html">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Activities and Location <small> (marine-based activities)</small>
                    <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                    </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="" >                        
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label">Select required activities</label>
                            <div  class="" v-for="category in marine_activities" >
                                <div class="form-check">
                                    <input @click="clickCategory($event, category)" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities" />
                                    {{ category.name }}
                                </div>
                                <div class="col-sm-12" v-for="activity in category.activities">
                                    <div class="form-check ">
                                        <input :onclick="isClickable"  :value="activity.id" class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_activities" data-parsley-required :disabled="!canEditActivities"/>
                                        {{ activity.name }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label"> Select the parks for which the activities are required</label>
                            <!-- <div class="" v-for="p in marine_parks">
                                <div class="form-check col-sm-12">
                                  <input :onclick="isClickable"  name="selected_parks" v-model="selected_parks" :value="{'park': p.id,'zones': p.zone_ids}" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities"/>
                                {{ p.name }}
                                  <span><a @click="edit_activities(p)" target="_blank" class="control-label pull-right" v-if="canEditActivities">Edit access and activities</a></span>
                                </div>
                            </div> -->
                            <div class="list-group list-group-root well">
                                <div class="" v-for="p in marine_parks">
                                  <div class="form-check col-sm-12 list-group-item">
                                    <input :onclick="isClickable"  name="selected_parks" v-model="selected_parks" :value="{'park': p.id,'zones': p.zone_ids}" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required :disabled="!canEditActivities"/>
                                  {{ p.name }}
                                    <span><a @click="edit_activities(p)" target="_blank" class="control-label pull-right" v-if="canEditActivities">Edit access and activities</a></span>
                                  </div>
                                </div>
                            </div>
                            <!-- <div>{{selected_parks}}</div>
                            <div>{{marine_parks_activities}}</div> -->
                        </div>
                        <div class="row"></div>
                        <div class="row"></div>
                        <div class="row"></div>
                        <div class="borderDecoration col-sm-12">
                          <div  v-for="rd in required_documents_list">
                            <div v-if="rd.can_view">
                              <label>{{rd.question}}</label>
                              <FileField :proposal_id="proposal.id" isRepeatable="true" :name="'req_doc'+rd.id" :required_doc_id="rd.id" label="Add Document" :id="'proposal'+proposal.id+'req_doc'+rd.id" :readonly="proposal.readonly"></FileField>
                            </div>
                          </div>
                        </div>
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label">You have selected vessel access for one or more parks. Provide details of each vessel you plan to use.</label>
                            <VesselTable :url="vessels_url" :proposal="proposal" ref="vessel_table"></VesselTable>
                        </div>
                        <div class="form-horizontal col-sm-12">
                        
                        </div>
                    </div>
                </div>
                <div>
                  <editMarineParkActivities ref="edit_activities" :proposal="proposal" @refreshSelectionFromResponse="refreshSelectionFromResponse"></editMarineParkActivities>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Vue from 'vue' 
import VesselTable from '@/components/common/vessel_table.vue' 
import editMarineParkActivities from './edit_marine_park_activities.vue'
import FileField from './required_docs.vue'
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
                values:null,
                vessels_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vessels'),
                marine_parks:[],
                marine_activities: [],
                selected_activities:[],
                selected_activities_before:[],
                selected_parks:[],
                selected_parks_before:[],
                marine_parks_activities:[],
                required_documents_list: null,
            }
        },
        components: {
          VesselTable,
          editMarineParkActivities,
          FileField,
        },
        watch: {
        selected_parks: function() {
            let vm = this;
            if (vm.proposal) {
                vm.proposal.parks = vm.selected_parks
            }
            var removed_park=$(vm.selected_parks_before).not(vm.selected_parks).get();
            var added_park=$(vm.selected_parks).not(vm.selected_parks_before).get();
            vm.selected_parks_before=vm.selected_parks;

            var current_activities=vm.selected_activities
            var zone_activities=[];
            //var current_access=vm.selected_access

            if(vm.marine_parks_activities.length==0){
              for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 // data={
                 //  'park': vm.selected_parks[i],
                 //  'activities': current_activities,
                 //  //'access': current_access
                 // }
                 for (var j=0; j<vm.selected_parks[i].zones.length; j++){
                  var zone_data={
                    'zone': vm.selected_parks[i].zones[j],
                    'activities': current_activities
                  }
                  zone_activities.push(zone_data)
                 }
                 data={
                  'park': vm.selected_parks[i].park,
                  'activities': zone_activities 
                 }
                 vm.marine_parks_activities.push(data);
               }
            }
            else{
              if(added_park.length!=0){
                for(var i=0; i<added_park.length; i++)
                { 
                  var found=false
                  for (var j=0; j<vm.marine_parks_activities.length; j++){
                    if(vm.marine_parks_activities[j].park==added_park[i].park){ 
                      found = true;}
                  }
                  if(found==false)
                  {
                    var zone_activities=[];
                    for(var k=0; k<added_park[i].zones.length; k++){
                      var zone_data={
                      'zone': added_park[i].zones[k],
                      'activities': current_activities
                      }
                      zone_activities.push(zone_data)
                    }
                    data={
                    'park': added_park[i].park,
                    'activities': zone_activities,
                    //'access': current_access
                   }
                   vm.marine_parks_activities.push(data);

                  }
                }
              }
              if(removed_park.length!=0){
                for(var i=0; i<removed_park.length; i++)
                { 
                  for (var j=0; j<vm.marine_parks_activities.length; j++){
                    if(vm.marine_parks_activities[j].park==removed_park[i].park){ 
                      vm.marine_parks_activities.splice(j,1)}
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
          if(vm.marine_parks_activities.length==0){
            for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_parks[i],
                  'activities': vm.selected_activities,
                  //'access': vm.selected_access
                 }
                 vm.marine_parks_activities.push(data);
               }
          }
          else{
            
            for (var i=0; i<vm.marine_parks_activities.length; i++)
            { 
              if(added.length!=0){
                for(var j=0; j<added.length; j++)
                {
                  // if(vm.marine_parks_activities[i].activities.indexOf(added[j])<0){
                  //   vm.marine_parks_activities[i].activities.push(added[j]);
                  // }
                  for(var k=0; k<vm.marine_parks_activities[i].activities.length; k++){
                    if(vm.marine_parks_activities[i].activities[k].activities.indexOf(added[j])<0){
                    vm.marine_parks_activities[i].activities[k].activities.push(added[j]);
                    }
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  // var index=vm.marine_parks_activities[i].activities.indexOf(removed[j]);
                  // if(index!=-1){
                  //   vm.marine_parks_activities[i].activities.splice(index,1)
                  // }
                  for(var k=0; k<vm.marine_parks_activities[i].activities.length; k++){
                    var index=vm.marine_parks_activities[i].activities[k].activities.indexOf(removed[j]);
                    if(index!=-1){
                      vm.marine_parks_activities[i].activities[k].activities.splice(index,1)
                    }
                  }
                }
              }
            }
          }
          vm.checkRequiredDocuements(vm.marine_parks_activities)
        },
        marine_parks_activities: function(){
            let vm=this;
            vm.checkRequiredDocuements(vm.marine_parks_activities)
            if (vm.proposal){
              vm.proposal.marine_parks_activities=vm.marine_parks_activities;
            }
        },
        },
        methods:{
            fetchParks: function(){
            let vm = this;

            vm.$http.get('/api/parks/marine_parks.json').then((response) => { 
            vm.marine_parks = response.body;
            },(error) => {
            console.log(error);
            })
          },
          checkRequiredDocuements: function(marine_parks_activities){
            let vm=this;
            //Check if the combination of selected park and activities require a document to be attahced
            if(vm.required_documents_list){
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
            }

            for(var i=0; i<marine_parks_activities.length; i++){
              for(var j=0; j<vm.required_documents_list.length; j++){
                if(vm.required_documents_list[j].park!=null){
                  if(vm.required_documents_list[j].activity==null){
                    if(vm.required_documents_list[j].park== marine_parks_activities[i].park){
                      vm.required_documents_list[j].can_view=true;
                    }
                  }
                  else{
                    for(var k=0; k<marine_parks_activities[i].activities.length; k++){
                      for(var l=0; l<marine_parks_activities[i].activities[k].activities.length; l++){
                        if(vm.required_documents_list[j].activity== marine_parks_activities[i].activities[k].activities[l]){
                        vm.required_documents_list[j].can_view=true;
                        }
                      }                     
                    }
                  }
                }
                else if(vm.required_documents_list[j].activity!=null){
                  for(var k=0; k<marine_parks_activities[i].activities.length; k++){
                      for(var l=0; l<marine_parks_activities[i].activities[k].activities.length; l++){
                        if(vm.required_documents_list[j].activity== marine_parks_activities[i].activities[k].activities[l]){
                        vm.required_documents_list[j].can_view=true;
                        }
                    }
                  }
                }
              }
            }
          }
          },
          fetchRequiredDocumentList: function(){
            let vm = this;
            vm.$http.get('/api/required_documents.json').then((response) => {
            vm.required_documents_list = response.body;
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
              vm.checkRequiredDocuements(vm.marine_parks_activities)
              //console.log('park',vm.selected_parks_activities)
            }
            },(error) => {
            console.log(error);
            })

          },
          clickCategory: function(e, c){
            let vm=this;
            var checked=e.target.checked;
            if(checked){
              for(var i=0; i<c.activities.length; i++){
                var index=this.selected_activities.indexOf(c.activities[i].id);
                if(index==-1)
                {
                  var r = helpers.copyObject(this.selected_activities);
                  r.push(c.activities[i].id);
                  this.selected_activities=r
                  
                }
              }
            }
            else{
              for(var i=0; i<c.activities.length; i++){
                var index=this.selected_activities.indexOf(c.activities[i].id);
                if(index!=-1){
                  var r = helpers.copyObject(this.selected_activities);
                  r.splice(index,1);
                  this.selected_activities=r
                  //this.selected_parks.splice(index,1)
                }
              }
            }
          },
          edit_activities: function(park){
            let vm=this;
            //inserting a temporary variables checked and new_activities to store and display selected activities for each zone.
            for(var l=0; l<park.zones.length; l++){
              console.log(park)
              park.zones[l].new_activities=[];
            }

            for (var i=0; i<vm.marine_parks_activities.length; i++){
              if(vm.marine_parks_activities[i].park==park.id){
                for(var j=0; j<vm.marine_parks_activities[i].activities.length; j++){
                  for(var k=0; k<park.zones.length; k++){
                    if (park.zones[k].id==vm.marine_parks_activities[i].activities[j].zone){
                      //park.zones[k].checked=true;
                      park.zones[k].new_activities=vm.marine_parks_activities[i].activities[j].activities;
                      park.zones[k].access_point=vm.marine_parks_activities[i].activities[j].access_point
                    }
                  }
                } 
              }
            }
            //console.log(park);
            this.$refs.edit_activities.park=park;
            this. $refs.edit_activities.isModalOpen = true;
          },
          refreshSelectionFromResponse: function(park_id, new_activities){
              let vm=this;
              for (var j=0; j<vm.marine_parks_activities.length; j++){
              if(vm.marine_parks_activities[j].park==park_id){ 
                vm.marine_parks_activities[j].activities= new_activities;
              }
            }
            vm.checkRequiredDocuements(vm.marine_parks_activities)
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
        store_parks: function(parks){
          let vm=this;
          var all_activities=[] //to store all activities for all zones so can find recurring onees to display selected_activities
          var park_list=[]
          for (var i = 0; i < parks.length; i++) {
              var current_park=parks[i].park.id
              var current_activities=[]
              var current_zones=[]
              
              for (var j = 0; j < parks[i].zones.length; j++) {
                var park_activities=[];
                for (var k = 0; k < parks[i].zones[j].park_activities.length; k++) {
                  park_activities.push(parks[i].zones[j].park_activities[k].activity);
                }

                var data_zone={
                  'zone': parks[i].zones[j].zone,
                  'activities': park_activities,
                  'access_point': parks[i].zones[j].access_point
                }
                current_activities.push(data_zone)
                all_activities.push({'key': park_activities})
                //current_zones.push(parks[i].zones[j].zone)
              }
               
               var data={
                'park': current_park,
                'activities': current_activities 
               }
               vm.marine_parks_activities.push(data)
               
            }
            
          for (var i=0; i<parks.length; i++)
            { 
              
              park_list.push({'park':parks[i].park.id, 'zones':parks[i].park.zone_ids})
            }
          vm.selected_parks=park_list
          //console.log(park_list)
          vm.selected_activities = vm.find_recurring(all_activities)
        },
        eventListeners: function(){
            
        },
        },
        mounted: function(){
            let vm = this;
            vm.proposal.marine_parks_activities=[];
            Vue.http.get('/api/marine_activities.json').then((res) => {
                      vm.marine_activities=res.body;                 
            },
            err => { 
                   console.log(err);
            });
            vm.fetchParks();
            vm.fetchRequiredDocumentList();
            vm.store_parks(vm.proposal.marine_parks);
            //vm.eventListeners();
        }
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

