<template id="application_conditions">
    <div>
        <template v-if="isFinalised">
            <div class="col-md-12 alert alert-success" v-if="application.processing_status == 'Approved'">
                <p>The licence has been issued and has been emailed to {{application.applicant.name}}</p>
                <p>Expiry date: {{application.proposed_issuance_licence.expiry_date}}
                <p>Permit: <a target="_blank" :href="application.permit">permit.pdf</a></p>
            </div>
            <div v-else class="col-md-12 alert alert-warning">
                <p>The application was declined. The decision was emailed to {{application.applicant.name}}</p>
            </div>    
        </template>
        <div class="col-md-12">
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
        </div>
        <div class="col-md-12">
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
        </div>
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
            return this.application.processing_status == 'Approved' || this.application.processing_status == 'Declined';
        }
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
