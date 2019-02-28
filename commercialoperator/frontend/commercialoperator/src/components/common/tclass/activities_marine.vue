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
                    <div class="">
                        
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <label class="control-label">Select required activities</label>
                            <div class="" v-for="category in marine_activities">
                                <div class="form-check">
                                    <input :onclick="isClickable" :inderminante="true" class="form-check-input" ref="Checkbox" type="checkbox" data-parsley-required />
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
        methods:{
        },
        mounted: function(){
            let vm = this;
            Vue.http.get('/api/marine_activities.json').then((res) => {
                      vm.marine_activities=res.body;                 
            },
            err => { 
                   console.log(err);
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

