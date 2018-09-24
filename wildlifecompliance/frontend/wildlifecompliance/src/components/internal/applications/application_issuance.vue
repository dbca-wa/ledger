<template id="application_issuance">

                    <div class="col-md-12">
                    <div class="row" v-for="item in application.licence_type_data">
                        <div class="panel panel-default">
                            <div class="panel-heading" v-for="(item1,index) in item">
                                <h3 class="panel-title" v-if="item1.name && item1.processing_status=='With Officer-Finalisation'">Issue {{item1.name}}
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="col-sm-12">
                                        <div class="form-group">
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Inspection Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" style="width: 70%;">
                                                       <input class="pull-left" placeholder="DD/MM/YYYY"/> 
                                                       <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Inspection Report</label>
                                                </div>
                                                <div class="col-sm-9">
                                                       <a href="">Attach File</a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Proposed Conditions
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="col-sm-12">
                                        <button v-if="hasAssessorMode" @click.prevent="addCondition()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Condition</button>
                                    </div>
                                    <datatable ref="conditions_datatable" :id="'conditions-datatable-'+_uid" :dtOptions="condition_options" :dtHeaders="condition_headers"/>
                                </form>
                            </div>
                        </div>
                    </div>
                    <ConditionDetail ref="condition_detail" :application_id="application.id" :conditions="conditions" :licence_activity_type_tab="licence_activity_type_tab"/>
                </div>

            
</template>
<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import ConditionDetail from './application_add_condition.vue'
export default {
    name: 'InternalApplicationConditions',
    props: {
        application: Object,
        licence_activity_type_tab:Number
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "application-conditions-"+vm._uid,
            proposed_licence:{},
        }
    },
    watch:{
        hasAssessorMode(){
            // reload the table
            this.updatedConditions();
        }
    },
    components:{
        datatable,
        ConditionDetail
    },
    computed:{
        hasAssessorMode(){
            return this.application.assessor_mode.has_assessor_mode;
        }
    },
    methods:{
        
        fetchProposeIssue(){
            let vm = this;
            
           vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/get_proposed_licence')))
            .then((response) => {
                vm.proposed_licence = response.body;
                
            }, (error) => {
               
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
       
        eventListeners(){
            let vm = this;
            vm.$refs.conditions_datatable.vmDataTable.on('click', '.deleteCondition', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.removeCondition(id);
            });
            vm.$refs.conditions_datatable.vmDataTable.on('click', '.editCondition', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.editCondition(id);
            });
        },
    },
    mounted: function(){
        let vm = this;
        this.fetchConditions();
        vm.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>
<style scoped>
</style>