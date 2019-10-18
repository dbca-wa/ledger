<template id="proposal_requirements">
    <div>
        <template v-if="isFinalised">
            <div class="col-md-12 alert alert-success" v-if="proposal.processing_status == 'Approved'">
                <p>The approval has been issued and has been emailed to {{proposal.applicant.name}}</p>
                <p>Expiry date: {{proposal.proposed_issuance_approval.expiry_date}}
                <p>Permit: <a target="_blank" :href="proposal.permit">approval.pdf</a></p>
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

                        <div class="row">
                            <div class="col-sm-12">
                                    <template v-if="!isFinalised">
                                        <p><strong>Level of approval: {{proposal.approval_level}}</strong></p>
                                        
                                    <div v-if="isApprovalLevel">    
                                        <p v-if="proposal.approval_level_document"><strong>Attach documents: <a :href="proposal.approval_level_document[1]" target="_blank">{{proposal.approval_level_document[0]}}</a>
                                        <span>
                                        <a @click="removeFile()" class="fa fa-trash-o" title="Remove file" style="cursor: pointer; color:red;"></a>
                                        </span></p>
                                        <div v-else>
                                            <p><strong>Attach documents:</strong></p>
                                            <div class="col-sm-12">                                           
                                            <span class="btn btn-info btn-file pull-left">
                                            Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                            </span>
                                            <!--<span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName()}}</span>-->
                                            
                                            </div>
                                            <div class="row"><p></p></div>
                                            <div class="row"><p></p></div>
                                            <div class="row"><p></p></div>

                                            <p>
                                            <strong>Comments (if no approval attached)</strong>
                                            </p>
                                            <p>
                                            <textarea name="approval_level_comments"  v-model="proposal.approval_level_comment" class="form-control" style="width:70%;"></textarea>
                                            </p>
                                        </div>

                                    </div>
                                    </template> 

                                    <template v-if="isFinalised">
                                        <p><strong>Level of approval: {{proposal.approval_level}}</strong></p>
                                        
                                        <div v-if="isApprovalLevel">    
                                            <p v-if="proposal.approval_level_document"><strong>Attach documents: <a :href="proposal.approval_level_document[1]" target="_blank">{{proposal.approval_level_document[0]}}</a>
                                            </p>
                                            <p v-if="proposal.approval_level_comment"><strong>Comments: {{proposal.approval_level_comment}}
                                            </p>
                                        </div>
                                    </template>                                    
                            </div>
                        </div> 
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
            uploadedFile: null,
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
        },
        isApprovalLevel:function(){
            return this.proposal.approval_level != null ? true : false;
        },
    },
    methods:{
        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
            vm.save()
        },
        removeFile: function(){
            let vm = this;
            vm.uploadedFile = null;
            vm.save()
        },
        save: function(){
            let vm = this;
                let data = new FormData(vm.form);
                data.append('approval_level_document', vm.uploadedFile)
                if (vm.proposal.approval_level_document) {
                    data.append('approval_level_document_name', vm.proposal.approval_level_document[0])
                }
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/approval_level_document'),data,{
                emulateJSON:true
            }).then(res=>{
                vm.proposal = res.body;
                vm.$emit('refreshFromResponse',res);

                },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });

            
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
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
