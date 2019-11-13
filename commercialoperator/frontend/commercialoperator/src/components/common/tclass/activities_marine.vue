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

                        <div class="borderDecoration col-sm-12">
                            <form>
                                <div class="col-sm-12" >
                                    <div>
                                        <!--<pre>{{ selected_activities }}</pre>-->
                                        <label class="control-label">Select the required activities</label>
                                        <TreeSelect :proposal="proposal" :value.sync="selected_activities" :options="marine_activity_options" :default_expand_level="1" :disabled="!canEditActivities"></TreeSelect>
                                    </div>
                                </div>
                            </form>
                        </div>

                        <div class="borderDecoration col-sm-12">
                            <form>
                                <div class="col-sm-12" >
                                    <div>
                                        <!--<pre>{{ selected_activities }}</pre>-->
                                        <label class="control-label">Select the parks for which the activities are required</label>
                                        <TreeSelect :proposal="proposal" :value.sync="selected_zone_ids" :options="marine_park_options" :default_expand_level="1" allow_edit="true" :disabled="!canEditActivities"></TreeSelect>
                                    </div>
                                </div>
                            </form>
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
                  <editMarineParkActivities ref="edit_activities" :proposal="proposal" :canEditActivities="canEditActivities" @refreshSelectionFromResponse="refreshSelectionFromResponse"></editMarineParkActivities>
                </div>
            </div>
        </div>

        <!--
        <div>Selected_Activities: {{selected_activities}}</div><br>
        <div>selected_zone_ids: {{selected_zone_ids}}</div><br>
        <div>selected_zones: {{selected_zones}}</div><br>
        <div>Marine_Park_Activities: {{marine_parks_activities}}</div><br>
        -->

    </div>
</template>

<script>
import Vue from 'vue' 
import VesselTable from '@/components/common/vessel_table.vue' 
import editMarineParkActivities from './edit_marine_park_activities.vue'
import FileField from './required_docs.vue'
import TreeSelect from '@/components/forms/treeview.vue'
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
                selected_zone_ids: [],
                selected_zone_ids_before: [],
                park_map: {},
                zone_map: {},
                park_activities: [],
                pBody: 'pBody'+vm._uid,
                values:null,
                vessels_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vessels'),
                marine_parks:[],
                marine_activities: [],
                selected_activities:[],
                selected_activities_before:[],
                selected_zones:[],
                selected_zones_before:[],
                marine_parks_activities:[],
                required_documents_list: null,
            }
        },
        components: {
          VesselTable,
          editMarineParkActivities,
          FileField,
          TreeSelect,
        },
        watch: {
          selected_zone_ids: function() {
            let vm = this;

            vm.selected_zones = []
            for (var i = 0; i < vm.selected_zone_ids.length; i++) {
                //var data = vm.get_selected_park_data(vm.get_park_ids[i] )
                var zone_id = vm.selected_zone_ids[i]
                var data = vm.get_selected_zone_data( zone_id )
                if (data !== null) {
                    vm.selected_zones.push( data )
                }
            }

            if (vm.proposal) {
                vm.proposal.parks = vm.selected_zones
            }

            try {
                var removed_zone_ids=$(vm.selected_zone_ids_before).not(vm.selected_zone_ids).get();
            } catch (error) {
                console.log('removed_zone: ' + error)
            }

            try {
                var added_zone_ids=$(vm.selected_zone_ids).not(vm.selected_zone_ids_before).get();
            } catch (error) {
                console.log('added_zone: ' + error)
            }
            vm.selected_zone_ids_before=vm.selected_zone_ids;

            var current_activities=vm.selected_activities
            var zone_activities=[];
            //var current_access=vm.selected_access

            if(vm.marine_parks_activities.length==0){
              for (var i = 0; i < vm.selected_zones.length; i++) {
                var park_id = vm.get_park_id(vm.selected_zones[i].zone)
                var data=null;

                if (park_id !== null) {
                  var zone_data={
                    'zone': vm.selected_zones[i].zone,
                    'activities': current_activities
                  }
                  zone_activities.push(zone_data)

                  data={
                    'park': parseInt(park_id),
                    'activities': zone_activities 
                  }
                  vm.marine_parks_activities.push(data);
                }
              }
            } else{
              if(added_zone_ids.length!=0){
                for(var i=0; i<added_zone_ids.length; i++) {
                  var park_id = vm.get_park_id(added_zone_ids[i])
                  var park_idx = vm.contains_park(park_id)

                  if (park_id !== null) {
                    var zone_data={
                      'zone': added_zone_ids[i],
                      'activities': current_activities
                      //'access': current_access
                    }

                    if( park_idx > -1) { // check if vm.marine_parks_activities dict already contains park entry
                      vm.marine_parks_activities[park_idx].activities.push( zone_data )
                    } else {
                      var zone_activities=[];
                      zone_activities.push(zone_data)

                      data={
                        'park': parseInt(park_id),
                        'activities': zone_activities,
                      }
                      vm.marine_parks_activities.push(data);
                    }
                  }
                }
              }
              if(removed_zone_ids.length!=0){
                for(var i=0; i<removed_zone_ids.length; i++) {
                  var park_id = vm.get_park_id(removed_zone_ids[i]);
                  var park_idx = vm.contains_park(park_id);
                  var park_activities = vm.marine_parks_activities[park_idx].activities;
                  var zone_idx = vm.contains_zone(park_activities, removed_zone_ids[i]);

                  vm.marine_parks_activities[park_idx].activities.splice(zone_idx,1)
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
            for (var i = 0; i < vm.selected_zones.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_zones[i],
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
          get_selected_zone_data:function(zone_id){
            let vm = this;
            for (var i=0; i<vm.marine_parks.length; i++) {
              var park = vm.marine_parks[i];
              for (var j=0; j<park.children.length; j++) {
                var zone = park.children[j];
                if (zone.id == zone_id) {
                  return {'zone': zone_id, 'park': park.id, 'activities': vm.selected_activities} // { "park": 4, "zones": [ 5, 4, 1  ]  }
                }
              }
            }
            return null;
          },

          get_park_id:function(zone_id){
            /* given zone id returns the associated proposal_park id */
            let vm = this;

            var ids = []
            var park_ids = Object.keys(vm.park_map);
            for (var i=0; i<park_ids.length; i++){ 
              var park_id = park_ids[i]
              var zone_ids = vm.park_map[park_id]
              if (zone_ids.indexOf(zone_id) > -1) {
                return park_id;
              }
            }
            return null;
          },

          get_park_map:function(){
            /* dictionary key:park id,  value:list zone ids
               eg. {park_id: zone_list} ==> { "4":[5,4,1], "170":[10,7,6,8,9], "171":[11] } */
            let vm = this;

            var park_map = {};
            for (var i=0; i<vm.marine_parks.length; i++){ 
              var park = vm.marine_parks[i]

              var ids = [];
              for (var j=0; j<park.children.length; j++) {
                var zone_id = park.children[j].id
                ids.push( zone_id )
              }
              park_map[park.id] = ids;
            }
            return park_map;
          },

          get_park_activities:function(){
            /* dictionary key:park id,  value:list zone ids
               eg. {park_id: zone_list} ==> { "4":[5,4,1], "170":[10,7,6,8,9], "171":[11] } */
            let vm = this;

            var park_map = {};
            var park_activities = [];
            var activities_by_zone = [];
            for (var i=0; i<vm.selected_zone_ids.length; i++){ 
              var zone_id = vm.selected_zone_ids[i]
              var park_id = vm.get_park_id(zone_id)
              if (park_id !== null) {
                activities_by_zone.push( {'park': park_id, 'activities': vm.selected_activities, 'access_point': '' } )
                park_activities.push({'zone': zone_id, 'activities': activities_by_zone})
              } else {
                console.log('ERROR: Park ID not found for zone_id ' + zone_id)
              }
            }
            return park_activities;
          },

          contains_park:function(park_id){
            /* return the index position of the park if exists, else -1 */
            let vm = this;

            for (var i=0; i<vm.marine_parks_activities.length; i++) {
              if(vm.marine_parks_activities[i].park==park_id) {
                return i;
              }
            }
            return -1;
          },
          contains_zone:function(activities, zone_id){
            /* return the index position of the zone if exists, else -1 */
            let vm = this;

            for (var i=0; i<activities.length; i++) {
              if(activities[i].zone==zone_id) {
                return i;
              }
            }
            return -1;
          },

          fetchMarineTreeview: function(){
            let vm = this;

            //console.log('treeview_url: ' + api_endpoints.tclass_container_marine)
            vm.$http.get(api_endpoints.tclass_container_marine)
            .then((response) => {

                vm.marine_activity_options = [
                    {
                        'id': 'All',
                        'name':'Select all marine activities',
                        'children': response.body['marine_activities']
                    }
                ]
                vm.marine_activities = response.body['marine_activities']

                vm.marine_park_options = [
                    {
                        'id': 'All',
                        'name':'Select all marine parks',
                        'children': response.body['marine_parks']
                    }
                ]
                vm.marine_parks = response.body['marine_parks']
                vm.park_map = vm.get_park_map();
                vm.park_activities = vm.get_park_activities();

                vm.required_documents_list = response.body['required_documents']
                vm.fetchRequiredDocumentList();

            },(error) => {
                console.log(error);
            })
          },
          fetchRequiredDocumentList: function(){
            let vm = this;
            for(var l=0; l<vm.required_documents_list.length; l++){
              vm.required_documents_list[l].can_view=false;
              vm.checkRequiredDocuements(vm.marine_parks_activities)
            }
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

                      // for(var l=0; l<marine_parks_activities[i].activities[k].activities.length; l++){
                      //   if(vm.required_documents_list[j].activity== marine_parks_activities[i].activities[k].activities[l]){
                      //   vm.required_documents_list[j].can_view=true;
                      //   }
                      // }
                      if(vm.required_documents_list[j].park== marine_parks_activities[i].park){
                        for(var l=0; l<marine_parks_activities[i].activities[k].activities.length; l++){
                          if(vm.required_documents_list[j].activity== marine_parks_activities[i].activities[k].activities[l]){
                            vm.required_documents_list[j].can_view=true;
                          }
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
          edit_activities: function(node){
            let vm=this;
            var park_id = node.raw.park_id
            var zone_id = node.raw.id
            var allowed_activities = node.raw.allowed_zone_activities 
            var label  = node.label

            var park_idx = vm.contains_park(park_id);
            var zone_idx = vm.contains_zone(vm.marine_parks_activities[park_idx].activities, zone_id)
            var activities = vm.marine_parks_activities[park_idx].activities[zone_idx].activities
            var access_point = vm.marine_parks_activities[park_idx].activities[zone_idx].access_point

            this.$refs.edit_activities.park_id = park_id;
            this.$refs.edit_activities.zone_id = zone_id;
            this.$refs.edit_activities.new_activities = activities.length > 0 ? activities : vm.selected_activities;
            this.$refs.edit_activities.access_point = access_point
            this.$refs.edit_activities.allowed_activities = allowed_activities;
            this.$refs.edit_activities.zone_label = label;
            this.$refs.edit_activities.isModalOpen = true;
          },
          /*
          _edit_activities: function(park){
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
                      park.zones[k].new_activities=vm.marine_parks_activities[i].activities[j].activities;
                      park.zones[k].access_point=vm.marine_parks_activities[i].activities[j].access_point
                    }
                  }
                } 
              }
            }
            this.$refs.edit_activities.park=park;
            this. $refs.edit_activities.isModalOpen = true;
          },
          */


          refreshSelectionFromResponse: function(park_id, zone_id, new_activities){
              let vm=this;

              var park_idx = vm.contains_park(park_id);
              var zone_idx = vm.contains_zone(vm.marine_parks_activities[park_idx].activities, zone_id)
              vm.marine_parks_activities[park_idx].activities.splice(zone_idx,1)
              vm.marine_parks_activities[park_idx].activities.push( new_activities );

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
          var zone_ids=[]
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
                zone_ids.push(parks[i].zones[j].zone)
              }

               var data={
                'park': current_park,
                'activities': current_activities 
               }
               vm.marine_parks_activities.push(data)
            }

          vm.selected_zone_ids=zone_ids
          vm.selected_activities = vm.find_recurring(all_activities)
        },

        eventListeners: function(){
        },
        },
        mounted: function(){
            let vm = this;
            vm.proposal.marine_parks_activities=[];
            vm.fetchMarineTreeview();

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

