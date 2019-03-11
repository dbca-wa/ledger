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
          <div class="borderDecoration">
          <form class="form-horizontal col-sm-12" name="personal_form" method="post">
            <label class="control-label"> Select the required access and activities</label>
          </form>
          <form>
            <div class="form-horizontal col-sm-6">
              <label class="control-label">Access</label>
              <div class="" v-for="a in accessTypes">
                <div class="form-check">
                  <input  class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_access" :value="a.id" data-parsley-required   />
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
                  <input  class="form-check-input" v-model="selected_activities" :value="a.id" ref="Checkbox" type="checkbox" data-parsley-required  />
                  {{ a.name }}
                </div>
              </div>
            </div>
          </form>
          <!-- <form> -->
            <div class="form-horizontal col-sm-12">
              <label class="control-label">Select Parks</label>
              <div class="" v-for="r in api_regions">
                <div class="form-check">
                  <input @click="clickRegion($event, r)" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" :value="r.id" v-model="selected_regions" :id="'region'+r.id" data-parsley-required />
                  {{ r.name }}
                  <!-- <a data-toggle="collapse" :href="'#'+r.id" role="button" aria-expanded="true" aria controls="r.id" ><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                </div>
                <div class="col-sm-12" v-for="d in r.districts" :id="r.id">
                  <div class="form-check ">
                    <input @click="clickDistrict($event, d)" :value="d.id" class="form-check-input" ref="Checkbox" :id="'district'+d.id" v-model="selected_districts" type="checkbox" data-parsley-required />
                    {{ d.name }}
                   <!--  <a data-toggle="collapse" :href="'#'+d.id+r.id" role="button" aria-expanded="true" aria controls="d.id+r.id"><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                  </div>
                  <div class="" v-for="p in d.land_parks">
                    <div class="form-check col-sm-12">
                      <input name="selected_parks" v-model="selected_parks" :value="p.id" class="form-check-input" ref="Checkbox" type="checkbox" :id="'park'+p.id" data-parsley-required />
                    {{ p.name }}
                      <span><a @click="edit_activities(p.id, p.name)" target="_blank" class="control-label pull-right">Edit access and activities</a></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- The below test code works for multiselect but it doesn't work with v-model -->
            <!-- <div class="form-horizontal col-sm-12">
              <label class="control-label">Select Parks test</label>
              <ul class="" v-for="r in api_regions">
                <li class="form-check">
                  <input :onclick="isClickable()" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" :value="r.id" v-model="selected_regions" :id="'region'+r.id" data-parsley-required />
                  {{ r.name }} -->
                  <!-- <a data-toggle="collapse" :href="'#'+r.id" role="button" aria-expanded="true" aria controls="r.id" ><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                
                <!-- <ul class="col-sm-12" v-for="d in r.districts" :id="r.id">
                  <li class="form-check ">
                    <input :onclick="isClickable()"  :value="d.id" class="form-check-input" ref="Checkbox" :id="'district'+d.id" type="checkbox" data-parsley-required />
                    {{ d.name }} -->
                   <!--  <a data-toggle="collapse" :href="'#'+d.id+r.id" role="button" aria-expanded="true" aria controls="d.id+r.id"><span class="glyphicon glyphicon-chevron-up pull-right "></span></a> -->
                  
                  <!-- <ul class="" v-for="p in d.land_parks">
                    <li class="form-check col-sm-12">
                      <input :onclick="isClickable()"  name="selected_parks" :value="p.id" class="form-check-input" ref="Checkbox" type="checkbox" :id="'park'+p.id" data-parsley-required />
                    {{ p.name }}
                      <span><a @click="edit_activities(p.id, p.name)" target="_blank" class="control-label pull-right">Edit access and activities</a></span>
                    </li>
                  </ul>
                  </li>
                </ul>
                </li>
              </ul>
            </div> -->
            <!-- test finish -->

            <div>{{selected_parks}}</div>
            <div>{{selected_parks_activities}}</div>
            
            
<!--           </form>

 -->      </div> 
          <div class="borderDecoration">
              <VehicleTable :url="vehicles_url" :proposal="proposal"></VehicleTable>
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
          <div class="row">
            <form class="form-horizontal col-sm-12" name="trails_form" method="post">
              <label class="control-label"> Select the required activities for trails</label>
            </form>
            <form>
              <div class="form-horizontal col-sm-6">
                <label class="control-label">Activities</label>
                <div class="" v-for="a in accessTypes">
                  <div class="form-check">
                    <input  class="form-check-input" ref="Checkbox" type="checkbox" v-model="trail_activities" :value="a.id" data-parsley-required/>
                      {{ a.name }}
                  </div>
                </div>
              </div>
            </form> 
            <div>
              <form>
                <div class="form-horizontal col-sm-12">
                  <label class="control-label">Select the long distance trails</label>
                  <div class="" v-for="t in trails">
                    <div class="form-check">
                      <input   name="selected_trails" v-model="selected_trails" :value="t.id" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                      {{ t.name }}
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <div>{{selected_trails}}</div>
      <div>{{selected_trails_activities}}</div>
      <div>
              <editParkActivities ref="edit_activities" :proposal="proposal" @refreshSelectionFromResponse="refreshSelectionFromResponse"></editParkActivities>
      </div>

    </div>
  </div>
</template>


<script>
import Vue from 'vue' 
import VehicleTable from '@/components/common/vehicle_table.vue'
import editParkActivities from './edit_park_activities.vue'
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
                accessTypes:null,
                api_regions:null,
                trails:null,
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
                //vehicles_url: api_endpoints.vehicles,
                vehicles_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vehicles'),
                selected_parks_activities:[],
                selected_trails_activities:[],
            }
        },
        components: {
          VehicleTable,
          editParkActivities,
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
            if (vm.proposal) {
                vm.proposal.parks = vm.selected_parks
            }
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
            if (vm.proposal){
              vm.proposal.selected_parks_activities=vm.selected_parks_activities;
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
                 data={
                  'trail': vm.selected_trails[i],
                  'activities': current_activities
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
                    if(vm.selected_trails_activities[j].trail==added_trail[i]){ 
                      found = true;}
                  }
                  if(found==false)
                  {
                    data={
                    'trail': added_trail[i],
                    'activities': current_activities,                   }
                   vm.selected_trails_activities.push(data);
                  }
                }
              }
              if(removed_trail.length!=0){
                for(var i=0; i<removed_trail.length; i++)
                { 
                  for (var j=0; j<vm.selected_trails_activities.length; j++){
                    if(vm.selected_trails_activities[j].trail==removed_trail[i]){
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
                  if(vm.selected_trails_activities[i].activities.indexOf(added[j])<0){
                    vm.selected_trails_activities[i].activities.push(added[j]);
                  }
                }
              }
              if(removed.length!=0){
                for(var j=0; j<removed.length; j++)
                {
                  var index=vm.selected_trails_activities[i].activities.indexOf(removed[j]);
                  if(index!=-1){
                    vm.selected_trails_activities[i].activities.splice(index,1)
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
            this. $refs.edit_activities.isModalOpen = true;
          },
          refreshSelectionFromResponse: function(park_id, park_activities, park_access){
              let vm=this;
              for (var j=0; j<vm.selected_parks_activities.length; j++){
              if(vm.selected_parks_activities[j].park==park_id){ 
                vm.selected_parks_activities[j].activities= park_activities;
                vm.selected_parks_activities[j].access= park_access;
              }
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
                }
              }
            }
            else{
              for(var i=0; i<r.districts.length; i++){
                var index=this.selected_districts.indexOf(r.districts[i].id);
                if(index!=-1){
                  this.selected_districts.splice(index,1)
                }
              }
            }
          },
          clickDistrict: function(e, d){
            let vm=this;
            var checked=e.target.checked;
            if(checked){
              for(var i=0; i<d.land_parks.length; i++){
                var index=this.selected_parks.indexOf(d.land_parks[i].id);
                if(index==-1)
                {
                  //this.selected_parks.push(d.land_parks[i].id)
                  Vue.set(this.selected_parks, this.selected_parks.length, d.land_parks[i].id);
                }
              }
            }
            else{
              for(var i=0; i<d.land_parks.length; i++){
                var index=this.selected_parks.indexOf(d.land_parks[i].id);
                if(index!=-1){
                  this.selected_parks.splice(index,1)
                }
              }
            }
          },
          // isClickable: function() {
            
          //   $('input[type="checkbox"]').change(function(e) {

          //   var checked = $(this).prop("checked"),
          //       container = $(this).parent(),
          //       siblings = container.siblings();

          //   console.log(siblings)

          //   container.find('input[type="checkbox"]').prop({
          //     indeterminate: false,
          //     checked: checked
          //   });

          //   function checkSiblings(el) {

          //     var parent = el.parent().parent(),
          //         all = true;

          //     el.siblings().each(function() {
          //       return all = ($(this).children('input[type="checkbox"]').prop("checked") === checked);
          //     });

          //     if (all && checked) {

          //       parent.children('input[type="checkbox"]').prop({
          //         indeterminate: false,
          //         checked: checked
          //       });

          //       checkSiblings(parent);

          //     } else if (all && !checked) {

          //       parent.children('input[type="checkbox"]').prop("checked", checked);
          //       parent.children('input[type="checkbox"]').prop("indeterminate", (parent.find('input[type="checkbox"]:checked').length > 0));
          //       checkSiblings(parent);

          //     } else {

          //       el.parents("li").children('input[type="checkbox"]').prop({
          //         indeterminate: true,
          //         checked: false
          //       });

          //     }

          //   }

          //   checkSiblings(container);
          //   });


          // },
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
        },

        mounted: function() {
            let vm = this;
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
            vm.fetchRegions(); 
            vm.fetchTrails();

            for (var i = 0; i < vm.proposal.parks.length; i++) {
              var current_park=vm.proposal.parks[i].park.id
              var current_activities=[]
              var current_access=[]
              for (var j = 0; j < vm.proposal.parks[i].land_activities.length; j++) {
                current_activities.push(vm.proposal.parks[i].land_activities[j].activity.id);
              }
               for (var k = 0; k < vm.proposal.parks[i].access_types.length; k++){
                current_access.push(vm.proposal.parks[i].access_types[k].access_type.id);
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

            for (var i = 0; i < vm.proposal.trails.length; i++) {
              this.selected_trails.push(vm.proposal.trails[i].trail.id);
            } 

            // this.$nextTick(()=>{
            //   vm.eventListeners();
            // });
            //check why this is not working
            $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
            }); 
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

