<template id="proposal_requirements">
    <div>
        <template v-if="isFinalised">
            <div class="col-md-12 alert alert-success" v-if="proposal.processing_status == 'Approved'">
                <p>The approval has been issued and has been emailed to {{proposal.applicant.name}}</p>
                <p>Expiry date: {{proposal.proposed_issuance_approval.expiry_date}}
                <p>Permit: <a target="_blank" :href="proposal.permit">permit.pdf</a></p>
            </div>
            <div v-else class="col-md-12 alert alert-warning">
                <p>The proposal was declined. The decision was emailed to {{proposal.applicant.name}}</p>
            </div>    
        </template>
        <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Level of Approval
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
                                <template v-if="!proposal.proposed_decline_status">
                                    <template v-if="isFinalised">
                                        <p><strong>Decision: Issue</strong></p>
                                        <p><strong>Start date: {{proposal.proposed_issuance_approval.start_date}}</strong></p>
                                        <p><strong>Expiry date: {{proposal.proposed_issuance_approval.expiry_date}}</strong></p>
                                        <p><strong>CC emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
                                    </template>
                                    <template v-else>
                                        <p><strong>Proposed decision: Issue</strong></p>
                                        <p><strong>Proposed start date: {{proposal.proposed_issuance_approval.start_date}}</strong></p>
                                        <p><strong>Proposed expiry date: {{proposal.proposed_issuance_approval.expiry_date}}</strong></p>
                                        <p><strong>Proposed cc emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
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
import RequirementDetail from './proposal_add_requirement.vue'
export default {
    name: 'InternalProposalRequirements',
    props: {
        proposal: Object
    },
    data: function() {
        let vm = this;
        return {
            proposedDecision: "proposal-decision-"+vm._uid,
            proposedLevel: "proposal-level-"+vm._uid,
        }
    },
    watch:{
    },
    components:{
    },
    computed:{
        hasAssessorMode(){
            return this.proposal.assessor_mode.has_assessor_mode;
        },
        isFinalised: function(){
            return this.proposal.processing_status == 'Approved' || this.proposal.processing_status == 'Declined';
        }
    },
    methods:{
        addRequirement(){
            this.$refs.requirement_detail.isModalOpen = true;
        },
        removeRequirement(_id){
            let vm = this;
            swal({
                title: "Remove Requirement",
                text: "Are you sure you want to remove this requirement?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Requirement',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.delete(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
                .then((response) => {
                    vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                });
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
