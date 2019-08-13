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
                            <div  class="row action-button">
                                <!-- <div v-if="!readonlyForm" class="col-sm-12"> -->
                                <div class="col-sm-12">
                                    <a ref="close" @click="endorseClicked" class="btn btn-primary btn-block">
                                        Endorse
                                    </a>
                                </div>
                            </div>

                            <div  class="row action-button">
                                <div class="col-sm-12">
                                    <a ref="close" @click="declineClicked" class="btn btn-primary btn-block">
                                        Decline
                                    </a>
                                </div>
                            </div>

                            <div  class="row action-button">
                                <div class="col-sm-12">
                                    <a ref="close" @click="returnToOfficerClicked" class="btn btn-primary btn-block">
                                        Return to Officer
                                    </a>
                                </div>
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
                                            <input :readonly="readonlyForm" class="form-control" v-model="displayOffence"/>
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
                                            <label>Offender</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input :readonly="readonlyForm" class="form-control" v-model="displayOffender"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Issued on paper?</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <input class="col-sm-1" id="issued_on_paper_yes" type="radio" v-model="sanction_outcome.issued_on_paper" :value="true" />
                                            <label class="col-sm-1 radio-button-label" for="issued_on_paper_yes">Yes</label>
                                            <input class="col-sm-1" id="issued_on_paper_no" type="radio" v-model="sanction_outcome.issued_on_paper" :value="false" />
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
                                            <textarea class="form-control" placeholder="add description" id="sanction-outcome-description" v-model="sanction_outcome.description"/>
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Date of Issue</label>
                                        </div>
                                        <div class="col-sm-6">
                                        </div>
                                    </div></div>

                                    <div class="form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label>Time of Issue</label>
                                        </div>
                                        <div class="col-sm-6">
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
    </div>
</template>

<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";
import datatable from '@vue-utils/datatable.vue'
import utils from "@/components/external/utils";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import SanctionOutcome from '../sanction_outcome/sanction_outcome_modal';
import CommsLogs from "@common-components/comms_logs.vue";
import filefield from '@/components/common/compliance_file.vue';
import 'bootstrap/dist/css/bootstrap.css';

export default {
    name: 'ViewSanctionOutcome',
    data() {
        let vm = this;
        return {
            soTab: 'soTab'+this._uid,
            deTab: 'deTab'+this._uid,
            reTab: 'reTab'+this._uid,
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
        CommsLogs,
    },
    beforeRouteEnter: function(to, from, next) {
        console.log('beforeRouteEnter');

        console.log('to');
        console.log(to);
        console.log('from');
        console.log(from);
        console.log('next');
        console.log(next);

        next(async (vm) => {
            console.log(vm);
            console.log('aho2');
            await vm.loadSanctionOutcome({ sanction_outcome_id: to.params.sanction_outcome_id });
        });
    },
    created: function() {
        console.log('created');
    },
    mounted: function() {
        console.log('mounted');
    },
    computed: {
        ...mapGetters('sanctionOutcomeStore', {
            sanction_outcome: "sanction_outcome",
        }),
        readonlyForm: function() {
            return true;
        },
        statusDisplay: function() {
            return 'TODO: Implement';
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
                    this.sanction_outcome.offence.lodgement_number;
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
        }
    },
    methods: {
        ...mapActions('sanctionOutcomeStore', {
            loadSanctionOutcome: 'loadSanctionOutcome',
            // saveSanctionOutcome: 'saveSanctionOutcome',
            // setSanctionOutcome: 'setSanctionOutcome', 
            // setPlannedForTime: 'setPlannedForTime',
            // modifyInspectionTeam: 'modifyInspectionTeam',
            // setPartyInspected: 'setPartyInspected',
        }),
        endorseClicked: function(e) {
            console.log('endorse clicked');
            console.log(e);
        },
        declineClicked: function(e) {
            console.log('decline clicked');
            console.log(e);
        },
        returnToOfficerClicked: function(e) {
            console.log('returnToOfficer clicked');
            console.log(e);
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
            await this.setInspection(res.body); 
        },
    }
}
</script>

<style>

</style>