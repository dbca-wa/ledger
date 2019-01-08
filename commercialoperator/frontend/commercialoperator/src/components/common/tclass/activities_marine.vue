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
                    <div class="borderDecoration">
                        <form class="form-horizontal col-sm-12" name="marine_form" method="post">
                        <label class="control-label">You have selected vessel access for one or more parks. Provide details of each vessel you plan to use.</label>
                        </form>
                    <div class="borderDecoration">
                        <VesselTable :url="vessels_url" :proposal="proposal"></VesselTable>
                    </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
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
            }
        },
        components: {
          VesselTable,
        },
        methods:{
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

