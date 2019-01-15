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
                  <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_access" :value="a.name" data-parsley-required   />
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
                  <input :onclick="isClickable" class="form-check-input" v-model="selected_activities" :value="a.id" ref="Checkbox" type="checkbox" data-parsley-required  />
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
                  <input :onclick="isClickable" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                  {{ r.name }}
                </div>
                <div class="col-sm-12" v-for="d in r.districts">
                  <div class="form-check ">
                    <input :onclick="isClickable"  :value="d.id" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                    {{ d.name }}
                  </div>
                  <div class="" v-for="p in d.parks">
                    <div class="form-check col-sm-12">
                      <input :onclick="isClickable"  name="selected" v-model="selected" :value="p.id" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
                    {{ p.name }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>{{selected}}</div>
            <div>{{selected_activities}}</div>
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
                <label class="control-label">Access</label>
                <div class="" v-for="a in accessTypes">
                  <div class="form-check">
                    <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" v-model="selected_access" :value="a.name" data-parsley-required/>
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
                      <input :onclick="isClickable"  name="selected_trails" v-model="selected_trails" :value="t.id" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
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

    </div>
  </div>
</template>


<script>
import Vue from 'vue' 
import VehicleTable from '@/components/common/vehicle_table.vue'
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
                selected:[],
                selected_access:[],
                selected_activities:[],
                selected_trails:[],
                activities:[],
                access:[],
                //vehicles_url: api_endpoints.vehicles,
                vehicles_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/vehicles'),
                selected_parks_activities:[]
            }
        },
        components: {
          VehicleTable,
        },
        watch:{
          selected: function() {
            let vm = this;
            if (vm.proposal) {
                vm.proposal.parks = vm.selected
                //vm.proposal.trails=vm.selected_trails;
               // for (var i = 0; i < vm.proposal.parks.length; i++) {
               //  vm.proposal.parks[i].land_activities=vm.selected_activities;
               // }
               //Storing and sending activities to API is still incomplete
               vm.selected_parks_activities=[]
               for (var i = 0; i < vm.selected.length; i++) {
                 var data=null;
                 data={
                  'park': vm.selected[i],
                  'activities': vm.selected_activities
                 }
                 vm.selected_parks_activities.push(data);
               }
            }
        },
        selected_trails: function(){
            let vm=this;
            if (vm.proposal){
              vm.proposal.trails=vm.selected_trails;
              //console.log(vm.proposal.trails);
            }
          }
        },
        methods:{
          fetchRegions: function(){
            let vm = this;

            vm.$http.get(api_endpoints.regions).then((response) => {
            vm.api_regions = response.body;
            //console.log(vm.api_regions);

            // for (var i = 0; i < vm.api_regions.length; i++) {
            //         this.regions.push( {text: vm.api_regions[i].name, value: vm.api_regions[i].id, districts: vm.api_regions[i].districts} );
            //     }
            },(error) => {
            console.log(error);
            })
          },
          fetchTrails: function(){
            let vm = this;

            vm.$http.get('/api/trails.json').then((response) => {
            vm.trails = response.body;
            console.log(vm.trails);

            // for (var i = 0; i < vm.api_regions.length; i++) {
            //         this.regions.push( {text: vm.api_regions[i].name, value: vm.api_regions[i].id, districts: vm.api_regions[i].districts} );
            //     }
            },(error) => {
            console.log(error);
            })
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
              this.selected.push(vm.proposal.parks[i].park.id);
              for (var j = 0; j < vm.proposal.parks[i].land_activities.length; j++) {
                this.selected_activities.push(vm.proposal.parks[i].land_activities[j].activity.id);
               }

            }

            // vm.$http.get(api_endpoints.regions).then((response) => {
            // vm.api_regions = response.body;
            // console.log(vm.api_regions);
            // },(error) => {
            // console.log(error);
            // })  
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

