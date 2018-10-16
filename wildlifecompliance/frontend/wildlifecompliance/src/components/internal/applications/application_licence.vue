<template id="application_conditions">
    <div>
        
        <template v-if="isFinalised">
            <div v-for="item in application.licence_type_data">
                <ul class="nav nav-tabs" id="conditiontabs">
                    <li v-for="(item1,index) in item">
                        <a v-if="item1.processing_status=='Accepted'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-ok"></span>
                        </a>
                        <a v-if="item1.processing_status=='Declined'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>


                    </li>
                </ul>
    
            </div>   
            <div  class="tab-content">
                <div v-for="item in application.licence_type_data">
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='Accepted'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been issued and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} {{isFinalised}}
                        <div v-for="licence in application.licences" v-if="licence.licence_activity_type_id == item1.id">
                            Expiry Date: {{licence.expiry_date}}
                        </div>
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='Declined'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been declined and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                </div>
            </div>
        </template>
        <template v-if="isPartiallyFinalised">
            <div v-for="item in application.licence_type_data">
                <ul class="nav nav-tabs" >
                    <li v-for="(item1,index) in item">
                        <a v-if="item1.processing_status=='Accepted'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-ok"></span>
                        </a>

                        <a v-if="item1.processing_status=='Declined'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="item1.processing_status=='With Assessor'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="item1.processing_status=='With Officer-Conditions'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>


                    </li>
                </ul>
    
            </div>   
            <div  class="tab-content">
                <div v-for="item in application.licence_type_data">
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='Accepted'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been issued and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='Declined'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been declined and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='With Assessor'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licensed activity cannot be issued as this licensed activity is still with assessord for assessment. 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status=='With Officer-Conditions'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licensed activity cannot be issued as the conditions have not been finalised yet. 
                    </div>
                </div>
            </div>
        </template>
        <!-- <template v-if="isFinalised">
            <div v-for="item in application.licence_type_data.activity_type">
                <ul class="nav nav-tabs">
                    <li>
                        <a v-if="item.processing_status=='Accepted'" data-toggle="tab" :href="`#${item.id}`">{{item.name}}
                        </a>
                        
                    </li>
                </ul>
    
            </div>   
            <div  class="tab-content">
                <div v-for="item in application.licence_type_data.activity_type">
                    <div v-if="item.processing_status=='Accepted'" :id="`${item.id}`" class="tab-pane fade active in"> 
                         <p>The licence has been issued and has been emailed to </p>
                         <p>Expiry date: 
                    </div>
                    
                </div>
            </div>
        </template> -->
        <!-- <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Level of Licence
                            <a class="panelClicker" :href="'#'+proposedLevel" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedLevel">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body panel-collapse collapse in" :id="proposedLevel">
                    </div>
                </div>
            </div>
        </div> -->
<!--         <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 v-if="!isFinalised" class="panel-title">Proposed Decision
                            <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                        <h3 v-else class="panel-title">Decision
                            <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body panel-collapse collapse in" :id="proposedDecision">
                        <div class="row">
                            <div class="col-sm-12">
                                <template v-if="!application.proposed_decline_status">
                                    <template v-if="isFinalised">
                                        <p><strong>Decision: Issue</strong></p>
                                        <p><strong>Start date: {{application.proposed_issuance_licence.start_date}}</strong></p>
                                        <p><strong>Expiry date: {{application.proposed_issuance_licence.expiry_date}}</strong></p>
                                        <p><strong>CC emails: {{application.proposed_issuance_licence.cc_email}}</strong></p>
                                    </template>
                                    <template v-else>
                                        <p><strong>Proposed decision: Issue</strong></p>
                                        <p><strong>Proposed start date: {{application.proposed_issuance_licence.start_date}}</strong></p>
                                        <p><strong>Proposed expiry date: {{application.proposed_issuance_licence.expiry_date}}</strong></p>
                                        <p><strong>Proposed cc emails: {{application.proposed_issuance_licence.cc_email}}</strong></p>
                                    </template>
                                </template>
                                <template v-else>
                                    <strong v-if="!isFinalised">Proposed decision: Decline</strong>
                                    <strong v-else>Decision: Decline</strong>
                                </template>
                            </div>
                        </div> 
                    </div>
                </div>
            </div>
        </div> -->
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
        application: Object
    },
    data: function() {
        let vm = this;
        return {
            proposedDecision: "application-decision-"+vm._uid,
            proposedLevel: "application-level-"+vm._uid,
        }
    },
    watch:{
    },
    components:{
    },
    computed:{
        hasAssessorMode(){
            return this.application.assessor_mode.has_assessor_mode;
        },
        isFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity_type.length; i<len; i++){
                if(vm.application.licence_type_data.activity_type[i].processing_status == 'Declined' || vm.application.licence_type_data.activity_type[i].processing_status == 'Accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag==len){
                return true;
            }
            else{
                return false;
            }
            
        },
        isPartiallyFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity_type.length; i<len; i++){
                if(vm.application.licence_type_data.activity_type[i].processing_status == 'Declined' || vm.application.licence_type_data.activity_type[i].processing_status == 'Accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag!=len){
                return true;
            }
            else{
                return false;
            }
            
        },
    },
    methods:{
        addCondition(){
            this.$refs.condition_detail.isModalOpen = true;
        },
        removeCondition(_id){
            let vm = this;
            swal({
                title: "Remove Condition",
                text: "Are you sure you want to remove this condition?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Condition',
                confirmButtonColor:'#d9534f'
            }).then((result) => {
                if (result.value) {
                    vm.$http.delete(helpers.add_endpoint_json(api_endpoints.application_conditions,_id))
                    .then((response) => {
                        vm.$refs.conditions_datatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
    },
    mounted: function(){
        let vm = this;
    }
}
</script>
<style scoped>
</style>
