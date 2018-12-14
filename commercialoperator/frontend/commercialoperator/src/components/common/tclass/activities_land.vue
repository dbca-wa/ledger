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
                  <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required   />
                  {{ a.name }}
                </div>
              </div>
            </div>
          </form>
          <form>
            <div class="form-horizontal col-sm-6">
              <label class="control-label">Activities</label>
              <div class="" v-for="a in accessTypes">
                <div class="form-check">
                  <input :onclick="isClickable" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required  />
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
            <div>{{proposal.parks}}</div>
            
<!--           </form>

 -->    </div> 
          <div class="borderDecoration">
              <VehicleTable :url="vehicles_url"></VehicleTable>
          </div>
        </div>
      </div>
    </div>
  </div>

    <div>
      
      <div v-if="proposal.processing_status=='Draft'">
        <!-- Activities Land: <input type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br> -->
      </div>
      <div v-else>
        <!-- Activities Land: <input readonly="readonly" type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br> -->
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
            return{
                values:null,
                accessTypes:null,
                api_regions:null,
                selected:[],
                activities:[],
                access:[],
                vehicles_url: api_endpoints.vehicles,
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
            } 
        },
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
        },
        mounted: function() {
            let vm = this;
            Vue.http.get('/api/access_types.json').then((res) => {
                      vm.accessTypes=res.body;
                      //console.log(vm.accessTypes);                  
                },
              err => { 
                        console.log(err);
                  }); 
            vm.fetchRegions(); 
            for (var i = 0; i < vm.proposal.parks.length; i++) {
            this.selected.push(vm.proposal.parks[i].park.id);
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

