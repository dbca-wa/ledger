<template lang="html">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <h3>Call/Email: {{ call_email.number }}</h3>
        </div>
        <div class="col-md-3 pull-right">
          <input  v-if="call_email.user_is_volunteer" type="button" @click.prevent="duplicate" class="pull-right btn btn-primary" value="Create Duplicate Call/Email"/>  
        </div>
      </div>
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

                        <div v-if="call_email.allocated_group && !(statusId === 'closed')" class="form-group">
                          <div class="row">
                            <div class="col-sm-12 top-buffer-s">
                              <strong>Currently assigned to</strong><br/>
                            </div>
                          </div>
                          <div class="row">
                            <div class="col-sm-12">
                              
                              <select :disabled="!call_email.user_in_group" class="form-control" v-model="call_email.assigned_to_id" @change="updateAssignedToId()">
                                <option  v-for="option in call_email.allocated_group" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div v-if="call_email.user_in_group">
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
                        <div v-if="statusId ==='draft' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="forwardToWildlifeProtectionBranch" @click="addWorkflow('forward_to_wildlife_protection_branch')" class="btn btn-primary btn-block">
                                  Forward to Wildlife Protection Branch
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='draft' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="forwardToRegions" @click="addWorkflow('forward_to_regions')" class="btn btn-primary btn-block">
                                  Forward to Regions
                                </a>
                          </div>
                        </div>

                        <div v-if="statusId ==='open' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="save" @click="save()" class="btn btn-primary btn-block">
                                  Save
                                </a>
                          </div>
                        </div>

                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open_followup' && this.call_email.can_user_action" class="row action-button">

                        <!-- <div v-if="statusId ==='open_followup'" class="row action-button"> -->
                        <!-- <div class="row action-button"> -->

                          <div class="col-sm-12">
                                <a @click="openOffence()" class="btn btn-primary btn-block">
                                  Offence
                                </a>
                          </div>
                        </div>

                        <div v-if="statusId ==='open_followup' && this.call_email.can_user_action && this.offenceExists" class="row action-button">
                          <div class="col-sm-12">
                                <a @click="openSanctionOutcome()" class="btn btn-primary btn-block">
                                  Sanction Outcome
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="allocateForFollowUp" @click="addWorkflow('allocate_for_follow_up')" class="btn btn-primary btn-block" >
                                  Allocate for Follow Up
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <!--a ref="allocateForInspection" @click="addWorkflow('allocate_for_inspection')" class="btn btn-primary btn-block"-->
                                <a ref="allocateForInspection" @click="allocateForInspection()" class="btn btn-primary btn-block" >
                                  Allocate for Inspection
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->

                        <div v-if="statusId ==='open' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="allocateForCase" @click="addWorkflow('allocate_for_case')" class="btn btn-primary btn-block" >
                                  Allocate for Case
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId !=='closed' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="close" @click="addWorkflow('close')" class="btn btn-primary btn-block">
                                  Close
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
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+cTab">Call/Email</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+rTab">Related Items</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="cTab" class="tab-pane fade in active">

                          <FormSection :formCollapse="false" label="Caller" Index="0">
                            
                            <div class="row"><div class="col-sm-8 form-group">
                              <label class="col-sm-12">Caller name</label>
                              <input :readonly="readonlyForm" class="form-control" v-model="call_email.caller"/>
                            </div></div>
                            <div class="col-sm-4 form-group"><div class="row">
                              <label class="col-sm-12">Caller contact number</label>
                            <input :readonly="readonlyForm" class="form-control" v-model="call_email.caller_phone_number"/>
                            </div></div>
                            
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4">Anonymous call?</label>
                                <input :disabled="readonlyForm" class="col-sm-1" id="yes" type="radio" v-model="call_email.anonymous_call" v-bind:value="true">
                                <label class="col-sm-1" for="yes">Yes</label>
                                <input :disabled="readonlyForm" class="col-sm-1" id="no" type="radio" v-model="call_email.anonymous_call" v-bind:value="false">
                                <label class="col-sm-1" for="no">No</label>
                            </div></div>
            
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4">Caller wishes to remain anonymous?</label>
                                <input :disabled="readonlyForm" class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="true">
                                <label class="col-sm-1">Yes</label>
                                <input :disabled="readonlyForm" class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="false">
                                <label class="col-sm-1">No</label>
                            </div></div>
            
                            <div v-show="statusId !=='draft'">
                                <SearchPerson />
                            </div>
                          </FormSection>
            
                          <FormSection :formCollapse="false" label="Location" Index="1">
                              <div v-if="call_email.location">
                                <MapLocation v-bind:key="call_email.location.id"/>
                              </div>
                          </FormSection>
            
                          <FormSection :formCollapse="true" label="Details" Index="2">
                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Date of call</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="dateOfCallPicker">
                                        <input :disabled="readonlyForm" type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="call_email.date_of_call"/>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <label class="col-sm-3">Time of call</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" id="timeOfCallPicker">
                                      <input :disabled="readonlyForm" type="text" class="form-control" placeholder="HH:MM" v-model="call_email.time_of_call"/>
                                      <span class="input-group-addon">
                                          <span class="glyphicon glyphicon-calendar"></span>
                                      </span>
                                    </div>
                                </div>
                            </div></div>
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-3">Volunteer</label>
                            <div class="col-sm-9">
                              <select :disabled="readonlyForm" class="form-control" v-model="call_email.volunteer_id">
                                <option  v-for="option in call_email.volunteer_list" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                            </div></div>
            
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4">Use occurrence from/to</label>
                                <input :disabled="readonlyForm" class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="true">
                                <label class="col-sm-1">Yes</label>
                                <input :disabled="readonlyForm" class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="false">
                                <label class="col-sm-1">No</label>
                            </div></div>
            
                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                                <div class="col-sm-4">
                                    <div class="input-group date" ref="occurrenceDateFromPicker">
                                        <input :disabled="readonlyForm" type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="call_email.occurrence_date_from" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <div v-show="call_email.occurrence_from_to">
                                    <div class="col-sm-4">
                                        <div class="input-group date" ref="occurrenceDateToPicker">
                                            <input :disabled="readonlyForm" type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="call_email.occurrence_date_to" />
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div></div>
            
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                              <div class="col-sm-3">
                                  <div class="input-group date" id="occurrenceTimeStartPicker">
                                    <input :disabled="readonlyForm" type="text" class="form-control" placeholder="HH:MM" v-model="call_email.occurrence_time_start"/>
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                  </div>
                              </div>
                              <div v-show="call_email.occurrence_from_to">
                                  <label class="col-sm-3">Occurrence time to</label>
                                  <div class="col-sm-3">
                                      <div class="input-group date" id="occurrenceTimeEndPicker">
                                        <input :disabled="readonlyForm" type="text" class="form-control" placeholder="HH:MM" v-model="call_email.occurrence_time_end"/>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                      </div>
                                  </div>
                              </div>
                            </div></div>
              
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4">Classification</label>
                              <select :disabled="readonlyForm" class="form-control" v-model="call_email.classification_id">
                                    <option v-for="option in classification_types" :value="option.id" v-bind:key="option.id">
                                      {{ option.name }} 
                                    </option>
                                </select>
                            </div></div>
            
                            <div class="row">
                                <div class="col-sm-9 form-group">
                                  <label class="col-sm-4">Report Type</label>
                                  <select :disabled="readonlyForm" @change.prevent="loadSchema" class="form-control" v-model="call_email.report_type_id">
                                          <option v-for="option in report_types" :value="option.id" v-bind:key="option.id">
                                            {{ option.report_type }} 
                                          </option>
                                  </select>
                                </div>
                                <div class="col-sm-3 form-group">
                                    <div class="row">
                                        <label class="col-sm-2 advice-url-label">None </label>
                                    </div>
                                    <div class="row">
                                        <a class="advice-url" :href="this.reportAdviceUrl" target="_blank" >Click for advice</a>
                                    </div>
                                </div>
                            </div>
                            
                            <div v-for="(item, index) in current_schema">
                              <compliance-renderer-block
                                 :component="item"
                                 v-bind:key="`compliance_renderer_block_${index}`"
                                />
                            </div>
                          </FormSection>
            
                          <FormSection v-if="(call_email.referrer && call_email.referrer.length > 0) || call_email.advice_details" :formCollapse="true" label="Outcome" Index="3">
                              <div v-if="call_email.referrer && call_email.referrer.length > 0" class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-4">Referred To</label>
                                <!--select multiple :readonly="true" class="form-control" v-model="call_email.selected_referrers" -->
                                <select style="width:100%" class="form-control input-sm" multiple ref="referrerList" >
                                  <option  v-for="option in referrers" :value="option.id" v-bind:key="option.id">
                                    {{ option.name }} 
                                  </option>
                                </select>
                            </div></div>
                            <div v-if="call_email.advice_details" class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4">Advice details</label>
                              <textarea :readonly="true" class="form-control" rows="5" v-model="call_email.advice_details"/>
                            </div></div>
                          </FormSection>

                        </div>  
                        <div :id="rTab" class="tab-pane fade in">
                            <FormSection :formCollapse="false" label="Related Items">
                                <div class="col-sm-12 form-group"><div class="row">
                                    <div class="col-sm-12" v-if="relatedItemsVisibility">
                                        <RelatedItems v-bind:key="relatedItemsBindId" :parent_update_related_items="setRelatedItems"/>
                                    </div>
                                </div></div>
                            </FormSection>
                        </div>
                    </div>
                </div>       


            </div>          
          </div>

        <div v-if="statusId ==='draft'" class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    
                                    <input type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                </p>
                            </div>
                        </div>
        </div>          
        <div v-if="workflow_type">
          <CallWorkflow ref="add_workflow" :workflow_type="workflow_type" v-bind:key="workflowBindId" />
        </div>
        <Offence ref="offence" :parent_update_function="loadCallEmail"/>
        <div v-if="sanctionOutcomeInitialised">
            <SanctionOutcome ref="sanction_outcome" :parent_update_function="loadCallEmail"/>
        </div>
        <div v-if="inspectionInitialised">
            <Inspection ref="inspection" :parent_update_function="loadCallEmail"/>
        </div>
    </div>
</template>
<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";

import CommsLogs from "@common-components/comms_logs.vue";
import MapLocation from "./map_location.vue";
import datatable from '@vue-utils/datatable.vue'
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import SearchPerson from "./search_person.vue";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import moment from 'moment';
import CallWorkflow from './call_email_workflow';
import Offence from '../offence/offence';
import SanctionOutcome from '../sanction_outcome/sanction_outcome_modal';
import 'bootstrap/dist/css/bootstrap.css';
import 'eonasdan-bootstrap-datetimepicker';
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import Inspection from '../inspection/inspection_modal';
import RelatedItems from "@common-components/related_items.vue";

export default {
  name: "ViewCallEmail",
  data: function() {
    return {
      cTab: 'cTab'+this._uid,
      rTab: 'rTab'+this._uid,
      sanctionOutcomeKey: 'sanctionOutcome' + this._uid,
      dtHeadersRelatedItems: [
          'Number',
          'Type',
          'Description',
          'Action',
      ],
      dtOptionsRelatedItems: {
          columns: [
              {
                  data: 'identifier',
              },
              {
                  data: 'model_name',
              },
              {
                  data: 'descriptor',
              },
              {
                  data: 'Action',
                  mRender: function(data, type, row){
                      // return '<a href="#" class="remove_button" data-offender-id="' + row.id + '">Remove</a>';
                      return '<a href="#">View (not implemented)</a>';
                  }
              },
          ]
      },
      disabledDates: {
        from: new Date(),
      },
      workflow_type: '',
      classification_types: [],
      report_types: [],
      referrers: [],
      referrersSelected: [],
      //allocated_group: [],
      current_schema: [],
      regionDistricts: [],
      sectionLabel: "Details",
      sectionIndex: 1,
      pBody: "pBody" + this._uid,
      loading: [],
      renderer_form: null,
      callemailTab: "callemailTab" + this._uid,
      comms_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/comms_log"
      ),
      comms_add_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/add_comms_log"
      ),
      logs_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/action_log"
      ),
      workflowBindId: '',
      sanctionOutcomeInitialised: false,
      offenceInitialised: false,
      inspectionInitialised: false,
    };
  },
  components: {
    CommsLogs,
    FormSection,
    MapLocation,
    SearchPerson,
    CallWorkflow,
    Offence,
    //datatable,
    RelatedItems,
    SanctionOutcome,
    Inspection,
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
    ...mapGetters({
      renderer_form_data: 'renderer_form_data',
      //current_user: 'current_user',
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    occurrenceDateLabel: function() {
      if (this.call_email.occurrence_from_to) {
        return "Occurrence date from";
      } else {
        return "Occurrence date";
      }
    },
    occurrenceTimeLabel: function() {
      if (this.call_email.occurrence_from_to) {
        return "Occurrence time from";
      } else {
        return "Occurrence time";
      }
    },
    readonlyForm: function() {
        return !this.call_email.can_user_edit_form;
    },
    statusDisplay: function() {
      return this.call_email.status ? this.call_email.status.name : '';
    },
    statusId: function() {
      return this.call_email.status ? this.call_email.status.id : '';
    },
    offenceExists: function() {
        for (let item of this.call_email.related_items) {
            if (item.model_name.toLowerCase() === "offence") {
                return true
            }
        }
        // return false if no related item is an Offence
        return false
    },
    reportAdviceUrl: function() {
        if (this.call_email.report_type) {
            return this.call_email.report_type.advice_url;
        } else {
            return null;
        }
    },
    relatedItemsBindId: function() {
        let timeNow = Date.now()
        if (this.call_email && this.call_email.id) {
            return 'call_email_' + this.call_email.id + '_' + this._uid;
        } else {
            return timeNow.toString();
        }
    },
    relatedItemsVisibility: function() {
        if (this.call_email && this.call_email.id) {
            return true;
        } else {
            return false;
        }
    }
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ...mapActions('callemailStore', {
      loadCallEmail: 'loadCallEmail',
      saveCallEmail: 'saveCallEmail',
      setCallEmail: 'setCallEmail', 
      setRegionId: 'setRegionId',
      setAllocatedGroupList: 'setAllocatedGroupList',
      setOccurrenceTimeStart: 'setOccurrenceTimeStart',
      setOccurrenceTimeEnd: 'setOccurrenceTimeEnd',
      setTimeOfCall: 'setTimeOfCall',
      setDateOfCall: 'setDateOfCall',
      setRelatedItems: 'setRelatedItems',
    }),
    ...mapActions({
      saveFormData: 'saveFormData',
    }),
    updateWorkflowBindId: function() {
        let timeNow = Date.now()
        if (this.workflow_type) {
            this.workflowBindId = this.workflow_type + '_' + timeNow.toString();
        } else {
            this.workflowBindId = timeNow.toString();
        }
    },
    addWorkflow(workflow_type) {
      this.workflow_type = workflow_type;
      this.updateWorkflowBindId();
      this.$nextTick(() => {
        this.$refs.add_workflow.isModalOpen = true;
      });
      // this.$refs.add_workflow.isModalOpen = true;
    },
    openSanctionOutcome(){
      console.log('sanction_outcome');
      this.sanctionOutcomeInitialised = true;
      this.$nextTick(() => {
          this.$refs.sanction_outcome.isModalOpen = true;
      });
    },
    openOffence(){
      this.offenceInitialised = true;
      this.$refs.offence.isModalOpen = true;
    },
    allocateForInspection() {
      this.inspectionInitialised = true;
      this.$refs.inspection.isModalOpen = true;
    },
    save: async function () {
        if (this.call_email.id) {
            await this.saveCallEmail({ route: false, crud: 'save' });
        } else {
            await this.saveCallEmail({ route: false, crud: 'create'});
            this.$nextTick(function () {
                this.$router.push({name: 'view-call-email', params: {call_email_id: this.call_email.id}});
            });
        }
    },
    saveExit: async function() {
      if (this.call_email.id) {
        await this.saveCallEmail({ route: true, crud: 'save' });
      } else {
        await this.saveCallEmail({ route: true, crud: 'create'});
      }
    },
    duplicate: async function() {
      await this.saveCallEmail({ route: false, crud: 'duplicate'});
    },
    loadSchema: function() {
      this.$nextTick(async function() {
      let url = helpers.add_endpoint_json(
                    api_endpoints.report_types,
                    this.call_email.report_type_id + '/get_schema',
                    );
      let returned_schema = await cache_helper.getSetCache(
        'CallEmail_ReportTypeSchema', 
        this.call_email.id.toString(), 
        url);
      if (returned_schema) {
        this.current_schema = returned_schema.schema;
      }
        
      });
    },
    updateAssignedToId: async function (user) {
        let url = helpers.add_endpoint_join(
            api_endpoints.call_email, 
            this.call_email.id + '/update_assigned_to_id/'
            );
        let payload = null;
        if (user === 'current_user' && this.call_email.user_in_group) {
            payload = {'current_user': true};
        } else if (user === 'blank') {
            payload = {'blank': true};
        } else {
            payload = { 'assigned_to_id': this.call_email.assigned_to_id };
        }
        let res = await Vue.http.post(
            url,
            payload
        );
        await this.setCallEmail(res.body); 
    },
    addEventListeners: function() {
      let vm = this;
      let el_fr_date = $(vm.$refs.occurrenceDateFromPicker);
      let el_fr_time = $(vm.$refs.occurrenceTimeFromPicker);
      let el_to_date = $(vm.$refs.occurrenceDateToPicker);
      let el_to_time = $(vm.$refs.occurrenceTimeToPicker);
      let el_date_of_call = $(vm.$refs.dateOfCallPicker);
      let el_time_of_call = $(vm.$refs.timeOfCallPicker);

      // "From" field
      el_fr_date.datetimepicker({
        format: "DD/MM/YYYY",
        maxDate: "now",
        showClear: true
      });
      el_fr_date.on("dp.change", function(e) {
        if (el_fr_date.data("DateTimePicker").date()) {
          vm.call_email.occurrence_date_from = e.date.format("DD/MM/YYYY");
        } else if (el_fr_date.data("date") === "") {
          vm.call_email.occurrence_date_from = "";
        }
      });
      el_fr_time.datetimepicker({ format: "LT", showClear: true });
      el_fr_time.on("dp.change", function(e) {
        if (el_fr_time.data("DateTimePicker").date()) {
          vm.call_email.occurrence_time_from = e.date.format("LT");
        } else if (el_fr_time.data("date") === "") {
          vm.call_email.occurrence_time_from = "";
        }
      });

      // "To" field
      el_to_date.datetimepicker({
        format: "DD/MM/YYYY",
        maxDate: "now",
        showClear: true
      });
      el_to_date.on("dp.change", function(e) {
        if (el_to_date.data("DateTimePicker").date()) {
          vm.call_email.occurrence_date_to = e.date.format("DD/MM/YYYY");
        } else if (el_to_date.data("date") === "") {
          vm.call_email.occurrence_date_to = "";
        }
      });
      el_to_time.datetimepicker({ format: "LT", showClear: true });
      el_to_time.on("dp.change", function(e) {
        if (el_to_time.data("DateTimePicker").date()) {
          vm.call_email.occurrence_time_to = e.date.format("LT");
        } else if (el_to_time.data("date") === "") {
          vm.call_email.occurrence_time_to = "";
        }
      });
      // Date/Time of call
      el_date_of_call.datetimepicker({
        format: "DD/MM/YYYY",
        maxDate: "now",
        //useCurrent: true,
        //showClear: true
      });
      el_date_of_call.on("dp.change", function(e) {
        if (el_date_of_call.data("DateTimePicker").date()) {
          vm.call_email.date_of_call = e.date.format("DD/MM/YYYY");
        } else if (el_date_of_call.data("date") === "") {
          vm.call_email.date_of_call = "";
        }
      });
      el_time_of_call.datetimepicker({ format: "LT", showClear: true });
      el_time_of_call.on("dp.change", function(e) {
        if (el_time_of_call.data("DateTimePicker").date()) {
          vm.call_email.time_of_call = e.date.format("LT");
        } else if (el_time_of_call.data("date") === "") {
          vm.call_email.time_of_call = "";
        }
      });
    },
  },
  created: async function() {
    
    if (this.$route.params.call_email_id) {
      await this.loadCallEmail({ call_email_id: this.$route.params.call_email_id });
    }
    // await this.loadComplianceAllocatedGroup(this.call_email.allocated_group_id);
    // load drop-down select lists
    // classification_types
    let returned_classification_types = await cache_helper.getSetCacheList('CallEmail_ClassificationTypes', '/api/classification.json');
    Object.assign(this.classification_types, returned_classification_types);
    // blank entry allows user to clear selection
    this.classification_types.splice(0, 0, 
      {
        id: null, 
        name: "",
      });
    //report_types
    let returned_report_types = await cache_helper.getSetCacheList('CallEmail_ReportTypes', helpers.add_endpoint_json(
                    api_endpoints.report_types,
                    'get_distinct_queryset'));
    Object.assign(this.report_types, returned_report_types);
    // blank entry allows user to clear selection
    this.report_types.splice(0, 0, 
      {
        id: "", 
        name: "",
      });
    // referrers
    let returned_referrers = await cache_helper.getSetCacheList('CallEmail_Referrers', '/api/referrers.json');
    Object.assign(this.referrers, returned_referrers);
    // blank entry allows user to clear selection
    this.referrers.splice(0, 0, 
      {
        id: "", 
        name: "",
      });

     // load selected referrers into local var
    for (let referrer_id of this.call_email.selected_referrers) {
        this.referrersSelected.push(referrer_id)
    }
    //Object.assign(this.referrersSelected, this.call_email.selected_referrers)

    // load current CallEmail renderer schema
    if (this.call_email.report_type_id) {
      await this.loadSchema();
    }

    // regionDistricts
    let returned_region_districts = await cache_helper.getSetCacheList(
      'CallEmail_RegionDistricts', 
      api_endpoints.region_district
      );
    Object.assign(this.regionDistricts, returned_region_districts);
    
    // Apply current timestamp to date and time of call
    if (!this.call_email.date_of_call && this.call_email.can_user_edit_form) {
        this.setDateOfCall(moment().format('DD/MM/YYYY'));
    }
    if (!this.call_email.time_of_call && this.call_email.can_user_edit_form) {
        this.setTimeOfCall(moment().format('LT'));
    }
    
  },
  mounted: function() {
      let vm = this;
      $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
          var chev = $( this ).children()[ 0 ];
          window.setTimeout( function () {
              $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
          }, 100 );
      });
      // Time field controls
      $('#occurrenceTimeStartPicker').datetimepicker({
              format: 'LT'
          });
      $('#occurrenceTimeEndPicker').datetimepicker({
              format: 'LT'
          });
      $('#occurrenceTimeStartPicker').on('dp.change', function(e) {
          vm.setOccurrenceTimeStart(e.date.format('LT'));
      });
      $('#occurrenceTimeEndPicker').on('dp.change', function(e) {
          vm.setOccurrenceTimeEnd(e.date.format('LT'));
      }); 
      $('#timeOfCallPicker').datetimepicker({
              format: 'LT'
          });
      $('#timeOfCallPicker').on('dp.change', function(e) {
          vm.setTimeOfCall(e.date.format('LT'));
      }); 
      // Initialise select2 for referrer
      $(vm.$refs.referrerList).select2({
          "theme": "bootstrap",
          allowClear: true,
          placeholder:"Select Referrer"
                  }).
      on("select2:select",function (e) {
                          var selected = $(e.currentTarget);
                          vm.referrersSelected = selected.val();
                      }).
      on("select2:unselect",function (e) {
                          var selected = $(e.currentTarget);
                          vm.referrersSelected = selected.val();
                      });
      
      vm.$nextTick(() => {
          vm.addEventListeners();
      });

  }
};
</script>

<style lang="css">
.action-button {
    margin-top: 5px;
}
#main-column {
  padding-left: 2%;
  padding-right: 0;
  margin-bottom: 50px;
}
.awesomplete {
    width: 100% !important;
}
.nav>li>a:focus, .nav>li>a:hover {
  text-decoration: none;
  background-color: #eee;
}
.nav-item {
  background-color: hsla(0, 0%, 78%, .8) !important;
  margin-bottom: 2px;
}
.advice-url-label {
  visibility: hidden;
}
.advice-url {
  padding-left: 20%;
}
</style>
