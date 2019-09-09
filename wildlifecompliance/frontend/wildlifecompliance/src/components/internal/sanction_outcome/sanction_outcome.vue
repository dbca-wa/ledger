<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <h3>Sanction Outcome: {{ displayLodgementNumber }}</h3>
            </div>
        </div>
        <div>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Workflow 
                        </div>
                        <div class="panel-body panel-collapse">
                            <div class="row">
                                <div class="col-sm-12">
                                    <strong>Status</strong><br/>
                                    {{ statusDisplay }}<br/>
                                </div>
                            </div>

                            <div v-if="sanction_outcome.allocated_group" class="form-group">
                            <div class="row">
                                <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <select :disabled="!sanction_outcome.user_in_group" class="form-control" v-model="sanction_outcome.assigned_to_id" @change="updateAssignedToId()">
                                        <option  v-for="option in sanction_outcome.allocated_group" :value="option.id" v-bind:key="option.id">
                                        {{ option.full_name }} 
                                        </option>
                                    </select>
                                </div>
                            </div>
                            </div>
                            <div v-if="sanction_outcome.user_in_group">
                                <a @click="updateAssignedToId('current_user')" class="btn pull-right">
                                    Assign to me
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Action 
                        </div>
                        <div class="panel-body panel-collapse">
                            <div v-if="visibilityWithdrawButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('withdraw')" class="btn btn-primary btn-block">
                                        Withdraw
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Withdraw
                            </div>

                            <div v-if="visibilitySendToManagerButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('send_to_manager')" class="btn btn-primary btn-block">
                                        Send To Manager
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Send To Manager
                            </div>

                            <div v-if="visibilityEndorseButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('endorse')" class="btn btn-primary btn-block">
                                        Endorse
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Endorse
                            </div>

                            <div v-if="visibilityDeclineButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('decline')" class="btn btn-primary btn-block">
                                        Decline
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Declilne
                            </div>

                            <div v-if="visibilityReturnToOfficerButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('return_to_officer')" class="btn btn-primary btn-block">
                                        Return to Officer
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Return to Officer
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-9" id="main-column">  
                <div class="row">
                    <div class="container-fluid">
                        <ul class="nav nav-pills aho2">
                            <li class="nav-item active"><a data-toggle="tab" :href="'#'+soTab">{{ typeDisplay }}</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+deTab">Details</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+reTab">Related Items</a></li>
                        </ul>
                        <div class="tab-content">
                            <div :id="soTab" class="tab-pane fade in active">
                                <FormSection :formCollapse="false" :label="typeDisplay">
                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Identifier</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input :readonly="readonlyForm" class="form-control" v-model="sanction_outcome.identifier"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Offence</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input readonly="true" class="form-control" v-model="displayOffence"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Offender</label>
                                        </div>
                                        <div class="col-sm-6">

                                            <div v-if="sanction_outcome && sanction_outcome.offence && sanction_outcome.offence.offenders">
                                                <select :disabled="readonlyForm" class="form-control" v-model="sanction_outcome.offender">
                                                    <option value=""></option>
                                                    <option v-for="offender in sanction_outcome.offence.offenders" v-bind:value="offender" v-bind:key="offender.id">
                                                        <span v-if="offender.person">
                                                            {{ offender.person.first_name + ' ' + offender.person.last_name + ', DOB:' + offender.person.dob }} 
                                                        </span>
                                                        <span v-else-if="offender.organisation">
                                                            {{ offender.organisation.name + ', ABN: ' + offender.organisation.abn }} 
                                                        </span>
                                                    </option>
                                                </select>
                                            </div>

                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-5">
                                            <label>Alleged committed offence</label>
                                        </div>
                                            <!--
                                        <div class="col-sm-6" v-for="item in sanction_outcome.alleged_offences">
                                            <input :readonly="readonlyForm" class="form-control" v-model="item.act + ', ' + item.name + ', ' + item.offence_text"/>
                                        </div>
                                            -->
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <div class="col-sm-12">
                                                <datatable ref="alleged_committed_offence_table" id="alleged-committed-offence-table" :dtOptions="dtOptionsAllegedOffence" :dtHeaders="dtHeadersAllegedOffence" />
                                            </div>
                                        </div></div>

                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Issued on paper?</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input :disabled="readonlyForm" class="col-sm-1" id="issued_on_paper_yes" type="radio" v-model="sanction_outcome.issued_on_paper" :value="true" />
                                            <label class="col-sm-1 radio-button-label" for="issued_on_paper_yes">Yes</label>
                                            <input :disabled="readonlyForm" class="col-sm-1" id="issued_on_paper_no" type="radio" v-model="sanction_outcome.issued_on_paper" :value="false" />
                                            <label class="col-sm-1 radio-button-label" for="issued_on_paper_no">No</label>
                                        </div>
                                    </div></div>

                                </FormSection>
                            </div>

                            <div :id="deTab" class="tab-pane fade in">
                                <FormSection :formCollapse="false" label="Details">
                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Description</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <textarea :disabled="readonlyForm" class="form-control" placeholder="add description" id="sanction-outcome-description" v-model="sanction_outcome.description"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Date of Issue</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input :readonly="readonlyForm" class="form-control" v-model="sanction_outcome.date_of_issue"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Time of Issue</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input :readonly="readonlyForm" class="form-control" v-model="sanction_outcome.time_of_issue"/>
                                        </div>
                                    </div></div>
                                </FormSection>
                            </div>

                            <div :id="reTab" class="tab-pane fade in active">
                                
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="workflow_type">
            <SanctionOutcomeWorkflow ref="add_workflow" :workflow_type="workflow_type" v-bind:key="workflowBindId" />
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";
import datatable from '@vue-utils/datatable.vue'
import utils from "@/components/external/utils";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import CommsLogs from "@common-components/comms_logs.vue";
import filefield from '@/components/common/compliance_file.vue';
import SanctionOutcomeWorkflow from './sanction_outcome_workflow';
import 'bootstrap/dist/css/bootstrap.css';

export default {
    name: 'ViewSanctionOutcome',
    data() {
        let vm = this;
        vm.STATUS_DRAFT = 'draft';
        vm.STATUS_AWAITING_ENDORSEMENT = 'awaiting_endorsement';
        vm.STATUS_AWAITING_REVIEW = 'awaiting_review';
        vm.STATUS_AWAITING_AMENDMENT = 'awaiting_amendment';
        vm.STATUS_AWAITING_PAYMENT = 'awaiting_payment';
        vm.STATUS_DECLINED = 'declined';

        return {
            workflow_type :'',
            workflowBindId :'',
            soTab: 'soTab' + this._uid,
            deTab: 'deTab' + this._uid,
            reTab: 'reTab' + this._uid,
            comms_url: helpers.add_endpoint_json(
                api_endpoints.sanction_outcome,
                this.$route.params.sanction_outcome_id + "/comms_log"
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.sanction_outcome,
                this.$route.params.sanction_outcome_id + "/add_comms_log"
            ),
            logs_url: helpers.add_endpoint_json(
                api_endpoints.sanction_outcome,
                this.$route.params.sanction_outcome_id + "/action_log"
            ),
            dtHeadersAllegedOffence: [
                "id",
                "Act",
                "Section/Regulation",
                "Alleged Offence",
                "Action"
            ],
            dtOptionsAllegedOffence: {
                columns: [
                    {
                        data: "id",
                        visible: false
                    },
                    {
                        data: "Act",
                        mRender: function(data, type, row) {
                            if (row.Action.removed){
                                data = '<strike>' + data + '</strike>';
                            }
                            return data;
                        }
                    },
                    {
                        data: "Section/Regulation",
                        mRender: function(data, type, row) {
                            if (row.Action.removed){
                                data = '<strike>' + data + '</strike>';
                            }
                            return data;
                        }
                    },
                    {
                        data: "Alleged Offence",
                        mRender: function(data, type, row) {
                            if (row.Action.removed){
                                data = '<strike>' + data + '</strike>';
                            }
                            return data;
                        }
                    },
                    {
                        data: "Action",
                        mRender: function(alleged_committed_offence, type, row) {
                            let ret = '';
                            if (alleged_committed_offence.removed){
                                ret = '<a href="#" class="restore_button" data-alleged-committed-offence-id="' + alleged_committed_offence.id + '">Restore</a>';
                            } else {
                                ret = '<a href="#" class="remove_button" data-alleged-committed-offence-id="' + alleged_committed_offence.id + '">Remove</a>';
                            }
                            return ret;
                        }
                    }
                ]
            }
        }
    },
    components: {
        FormSection,
        SanctionOutcomeWorkflow,
        CommsLogs,
        datatable,
    },
    created: async function() {
        console.log('created');
        if (this.$route.params.sanction_outcome_id) {
            await this.loadSanctionOutcome({ sanction_outcome_id: this.$route.params.sanction_outcome_id });
            this.reflectAllegedOffencesToTable();
        }
    },
    mounted: function() {
        this.$nextTick(() => {
            this.addEventListeners();
        });
    },
    computed: {
        ...mapGetters('sanctionOutcomeStore', {
            sanction_outcome: "sanction_outcome",
        }),
        readonlyForm: function() {
            return !this.canUserEditForm;
        },
        canUserEditForm: function() {
            let canUserEdit = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status === this.STATUS_AWAITING_AMENDMENT || this.sanction_outcome.status === this.STATUS_DRAFT){
                    canUserEdit = true;
                }
            }
            return canUserEdit;
        },
        statusDisplay: function() {
            let ret = '';
            if (this.sanction_outcome){
                if (this.sanction_outcome.status){
                    ret = this.sanction_outcome.status.name;
                }
            }
            return ret;
        },
        typeDisplay: function() {
            let ret = '';
            if (this.sanction_outcome){
                if (this.sanction_outcome.type){
                    ret = this.sanction_outcome.type.name;
                }
            }
            return ret;
        },
        displayOffence: function() {
            let ret = '';
            if (this.sanction_outcome){
                if (this.sanction_outcome.offence){
                    console.log('displayOffence');
                    ret = this.sanction_outcome.offence.lodgement_number;
                }
            }
            return ret;
        },
        displayOffender: function() {
            let ret = '';
            if (this.sanction_outcome){
                if (this.sanction_outcome.offender){
                    if (this.sanction_outcome.offender.person){
                        ret = [this.sanction_outcome.offender.person.first_name, this.sanction_outcome.offender.person.last_name].filter(Boolean).join(" ");
                    } else if (this.sanction_outcome.offender.organisation){
                        ret = [this.sanction_outcome.offender.organisation.name, this.sanction_outcome.offender.organisation.abn].filter(Boolean).join(" ");
                    }
                }
            }
            return ret;
        },
        displayLodgementNumber: function() {
            let ret = '';
            if (this.sanction_outcome){
                ret = this.sanction_outcome.lodgement_number;
            }
            return ret;
        },
        visibilityWithdrawButton: function() {
            let visibility = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_PAYMENT){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilitySendToManagerButton: function() {
            let visibility = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status.id === this.STATUS_DRAFT || this.sanction_outcome.status.id === this.STATUS_AWAITING_AMENDMENT){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityEndorseButton: function() {
            let visibility = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_ENDORSEMENT || this.sanction_outcome.status.id === this.STATUS_AWAITING_REVIEW){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityDeclineButton: function() {
            let visibility = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_ENDORSEMENT || this.sanction_outcome.status.id === this.STATUS_AWAITING_REVIEW){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityReturnToOfficerButton: function() {
            let visibility = false;
            if (this.sanction_outcome.can_user_action){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_REVIEW){
                    visibility = true;
                }
            }
            return visibility;
        }
    },
    methods: {
        ...mapActions('sanctionOutcomeStore', {
            loadSanctionOutcome: 'loadSanctionOutcome',
            setSanctionOutcome: 'setSanctionOutcome', 
            setAssignedToId: 'setAssignedToId',
            setCanUserAction: 'setCanUserAction',
        }),
        addEventListeners: function() {
            $("#alleged-committed-offence-table").on("click", ".remove_button", this.removeAllegedOffenceClicked);
            $("#alleged-committed-offence-table").on("click", ".restore_button", this.restoreAllegedOffenceClicked);
        },
        removeAllegedOffenceClicked: function(e) {
            this.toggleAllegedCommittedOffence(e, true);
        },
        restoreAllegedOffenceClicked: function(e){
            this.toggleAllegedCommittedOffence(e, false);
        },
        toggleAllegedCommittedOffence: function(e, removed){
            let vm = this;
            let acoId = parseInt(e.target.getAttribute("data-alleged-committed-offence-id"));
            vm.$refs.alleged_committed_offence_table.vmDataTable.rows(function(idx, data, node) {
                if (data.id === acoId) {
                    vm.$refs.alleged_committed_offence_table.vmDataTable.rows(idx).data()[0].Action.removed = removed;
                        vm.$refs.alleged_committed_offence_table.vmDataTable.rows(idx).invalidate();
                }
            });
        },
        reflectAllegedOffencesToTable: function(){
            if (this.sanction_outcome && this.sanction_outcome.alleged_committed_offences){
                for(let i=0; i<this.sanction_outcome.alleged_committed_offences.length; i++){
                    this.addAllegedOffenceToTable(this.sanction_outcome.alleged_committed_offences[i]);
                }
            }
        },
        addAllegedOffenceToTable: function(allegedCommittedOffence){
              this.$refs.alleged_committed_offence_table.vmDataTable.row.add({
                  id: allegedCommittedOffence.id,
                  Act: allegedCommittedOffence.alleged_offence.section_regulation.act,
                  "Section/Regulation": allegedCommittedOffence.alleged_offence.section_regulation.name,
                  "Alleged Offence": allegedCommittedOffence.alleged_offence.section_regulation.offence_text,
                  Action: allegedCommittedOffence,
              }).draw();
        },
        addWorkflow(workflow_type) {
            this.workflow_type = workflow_type;
            this.updateWorkflowBindId();
            this.$nextTick(() => {
                this.$refs.add_workflow.isModalOpen = true;
            });
        },
        updateWorkflowBindId: function() {
            let timeNow = Date.now()
            if (this.workflow_type) {
                this.workflowBindId = this.workflow_type + '_' + timeNow.toString();
            } else {
                this.workflowBindId = timeNow.toString();
            }
        },
        updateAssignedToId: async function (user) {
            let url = helpers.add_endpoint_join(
                api_endpoints.sanction_outcome, 
                this.sanction_outcome.id + '/update_assigned_to_id/'
                );
            let payload = null;
            if (user === 'current_user' && this.sanction_outcome.user_in_group) {
                payload = {'current_user': true};
            } else if (user === 'blank') {
                payload = {'blank': true};
            } else {
                payload = { 'assigned_to_id': this.sanction_outcome.assigned_to_id };
            }
            let res = await Vue.http.post(
                url,
                payload
            );
            console.log('updateAssignedToId');
            console.log(res.body);
            //await this.setSanctionOutcome(res.body); 
            this.setAssignedToId(res.body.assigned_to_id);
            this.setCanUserAction(res.body.can_user_action);
        },
    }
}
</script>

<style>

</style>
