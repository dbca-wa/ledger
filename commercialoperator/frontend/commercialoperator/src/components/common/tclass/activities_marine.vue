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
                                    <input @click="clickCategory($event, category)" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                                    {{ category.name }}
                                </div>
                                <div class="col-sm-12" v-for="activity in category.activities">
                                    <div class="form-check ">
                                        <input :onclick="isClickable"  :value="activity.id" class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_activities" data-parsley-required />
                                        {{ activity.name }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label"> Select the parks for which the activities are required</label>
                            <div class="" v-for="p in marine_parks">
                                <div class="form-check col-sm-12">
                                  <input :onclick="isClickable"  name="selected_parks" v-model="selected_parks" :value="p.id" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                                {{ p.name }}
                                  <span><a @click="edit_activities()" target="_blank" class="control-label pull-right">Edit access and activities</a></span>
                                </div>
                            </div>
                            <div>{{selected_parks}}</div>
                            <div>{{marine_parks_activities}}</div>
                        </div>
                        <div class="row"></div>
                        <div class="row"></div>
                        <div class="row"></div>
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label">You have selected vessel access for one or more parks. Provide details of each vessel you plan to use.</label>
                            <VesselTable :url="vessels_url" :proposal="proposal"></VesselTable>
                        </div>
                        <div class="form-horizontal col-sm-12">
                        
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Vue from 'vue' 
import VesselTable from '@/components/common/vessel_table.vue' 
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
            }
        },
        data:function () {
            let vm = this;
            return{
                values:null,
                vessels_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vessels'),
                marine_parks:[],
                marine_activities: [],
                selected_activities:[],
                selected_activities_before:[],
                selected_parks:[],
                selected_parks_before:[],
                marine_parks_activities:[],
            }
        },
        components: {
          VesselTable,
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
            //var current_access=vm.selected_access

            if(vm.marine_parks_activities.length==0){
              for (var i = 0; i < vm.selected_parks.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected_parks[i],
                  'activities': current_activities,
                  //'access': current_access
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
                    if(vm.marine_parks_activities[j].park==added_park[i]){ 
                      found = true;}
                  }
                  if(found==false)
                  {
                    data={
                    'park': added_park[i],
                    'activities': current_activities,
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
                    if(vm.marine_parks_activities[j].park==removed_park[i]){ 
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
                  if(vm.marine_parks_activities[i].activities.indexOf(added[j])<0){
                    vm.marine_parks_activities[i].activities.push(added[j]);
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  var index=vm.marine_parks_activities[i].activities.indexOf(removed[j]);
                  if(index!=-1){
                    vm.marine_parks_activities[i].activities.splice(index,1)
                  }
                }
              }
            }
            // for(var temp of vm.marine_parks_activities){
            //   if(added.length!=0){
            //     if(temp.activities.indexOf(added[0])<0){
            //       temp.activities.push(added[0]);
            //     }
            //    }
            // }

          }
        },
        marine_parks_activities: function(){
            let vm=this;
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
          for (var i = 0; i < parks.length; i++) {
              var current_park=parks[i].park.id
              var current_activities=[]
              for (var j = 0; j < parks[i].marine_activities.length; j++) {
                current_activities.push(parks[i].marine_activities[j].activity.id);
              }
               var data={
                'park': current_park,
                'activities': current_activities
               }
               vm.marine_parks_activities.push(data)
            }

            var activity_list=[]
            var park_list=[]
            for (var i=0; i<vm.marine_parks_activities.length; i++)
            { 
              park_list.push(vm.marine_parks_activities[i].park);
              activity_list.push({'key' : vm.marine_parks_activities[i].activities});
            }

            vm.selected_activities = vm.find_recurring(activity_list)
            vm.selected_parks=park_list
        }
        },
        mounted: function(){
            let vm = this;
            Vue.http.get('/api/marine_activities.json').then((res) => {
                      vm.marine_activities=res.body;                 
            },
            err => { 
                   console.log(err);
            });
            vm.fetchParks(); 
            vm.store_parks(vm.proposal.marine_parks);
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
</style>

