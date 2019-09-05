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
                                                <select class="form-control" v-on:change="offenderSelected($event)" v-bind:value="sanction_outcome.offender.id">
                                                    <option value=""></option>
                                                    <option v-for="offender in sanction_outcome.offence.offenders" v-bind:value="offender.id" v-bind:key="offender.id">
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
                                        <div class="col-sm-3">
                                            <label>Alleged committed offence</label>
                                        </div>
                                        <div class="col-sm-6" v-for="item in sanction_outcome.alleged_offences">
                                            <input :readonly="readonlyForm" class="form-control" v-model="item.act + ', ' + item.name + ', ' + item.offence_text"/>
                                        </div>
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
        }
    },
    components: {
        FormSection,
        SanctionOutcomeWorkflow,
        CommsLogs,
    },
    created: async function() {
        if (this.$route.params.sanction_outcome_id) {
            await this.loadSanctionOutcome({ sanction_outcome_id: this.$route.params.sanction_outcome_id });
        }
    },
    mounted: function() {
        console.log('mounted');
    },
    computed: {
        ...mapGetters('sanctionOutcomeStore', {
            sanction_outcome: "sanction_outcome",
        }),
        readonlyForm: function() {
            return false;
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
        canUserAction: function() {
            return this.sanction_outcome.can_user_action;
        },
        visibilityWithdrawButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_PAYMENT){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilitySendToManagerButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.sanction_outcome.status.id === this.STATUS_DRAFT || this.sanction_outcome.status.id === this.STATUS_AWAITING_AMENDMENT){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityEndorseButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_ENDORSEMENT || this.sanction_outcome.status.id === this.STATUS_AWAITING_REVIEW){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityDeclineButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.sanction_outcome.status.id === this.STATUS_AWAITING_ENDORSEMENT || this.sanction_outcome.status.id === this.STATUS_AWAITING_REVIEW){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityReturnToOfficerButton: function() {
            let visibility = false;
            if (this.canUserAction){
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
        }),
        offenderSelected: function(e) {
            let offender_id = parseInt(e.target.value);
            for (let i = 0; i < this.sanction_outcome.offence.offenders.length; i++) {
                if (this.sanction_outcome.offence.offenders[i].id == offender_id) {
                    this.sanction_outcome.offender = this.sanction_outcome.offence.offenders[i];
                    return;
                }
            }
            // User selected the empty line
            this.sanction_outcome.offender = {};
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
            await this.setSanctionOutcome(res.body); 
        },
    }
}
</script>

<style>

</style>
