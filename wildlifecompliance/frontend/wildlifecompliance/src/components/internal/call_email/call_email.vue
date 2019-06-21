<template lang="html">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <h3>Call/Email: {{ call_email.number }}</h3>
        </div>
        <div class="col-md-3 pull-right">
          <input  v-if="current_user && current_user.is_volunteer" type="button" @click.prevent="duplicate" class="pull-right btn btn-primary" value="Create Duplicate Call/Email"/>  
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
                              
                              <select class="form-control" v-model="call_email.assigned_to_id" @change="updateAssignedToId()">
                                <option  v-for="option in call_email.allocated_group.members" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
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
                        <div v-if="statusId ==='draft'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="forwardToWildlifeProtectionBranch" @click="addWorkflow('forward_to_wildlife_protection_branch')" class="btn btn-primary btn-block">
                                  Forward to Wildlife Protection Branch
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='draft'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="forwardToRegions" @click="addWorkflow('forward_to_regions')" class="btn btn-primary btn-block">
                                  Forward to Regions
                                </a>
                          </div>
                        </div>

                        <div v-if="statusId ==='open'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="save" @click="save()" class="btn btn-primary btn-block">
                                  Save
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open_followup'" class="row action-button">
                          <div class="col-sm-12">
                                <a @click="offence()" class="btn btn-primary btn-block">
                                  Offence
                                </a>
                          </div>
                        </div>

                        <div v-if="statusId ==='open_followup'" class="row action-button">
                          <div class="col-sm-12">
                                <a class="btn btn-primary btn-block">
                                  Sanction Outcome
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="allocateForFollowUp" @click="addWorkflow('allocate_for_follow_up')" class="btn btn-primary btn-block" >
                                  Allocate for Follow Up
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="statusId ==='open'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="allocateForInspection" @click="addWorkflow('allocate_for_inspection')" class="btn btn-primary btn-block" >
                                  Allocate for Inspection
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->

                        <div v-if="statusId ==='open'" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="allocateForCase" @click="addWorkflow('allocate_for_case')" class="btn btn-primary btn-block" >
                                  Allocate for Case
                                </a>
                          </div>
                        </div>
                        <!-- <div class="row">
                          <div class="col-sm-12"/>
                        </div> -->
                        <div v-if="!(statusId === 'closed')" class="row action-button">
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
          <div class="col-md-1"/>        
          <div class="col-md-8">  
            <div class="row">

              <FormSection :formCollapse="false" label="Caller" Index="0">
                
                <div class="row"><div class="col-sm-8 form-group">
                  <label class="col-sm-12">Caller name</label>
                  <input :readonly="isReadonly" class="form-control" v-model="call_email.caller"/>
                </div></div>
                <div class="col-sm-4 form-group"><div class="row">
                  <label class="col-sm-12">Caller contact number</label>
                <input :readonly="isReadonly" class="form-control" v-model="call_email.caller_phone_number"/>
                </div></div>
                
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Anonymous call?</label>
                    <input :disabled="isReadonly" class="col-sm-1" id="yes" type="radio" v-model="call_email.anonymous_call" v-bind:value="true">
                    <label class="col-sm-1" for="yes">Yes</label>
                    <input :disabled="isReadonly" class="col-sm-1" id="no" type="radio" v-model="call_email.anonymous_call" v-bind:value="false">
                    <label class="col-sm-1" for="no">No</label>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Caller wishes to remain anonymous?</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>

                <div v-if="personSearchVisible">
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
                  <label class="col-sm-4">Use occurrence from/to</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                    <div class="col-sm-3" :disabled="isReadonly">
                      <datepicker :typeable="true" :disabledDates="disabledDates" placeholder="DD/MM/YYYY" input-class="form-control" v-model="call_email.occurrence_date_from"/>
                    </div>
                    <div v-show="call_email.occurrence_from_to" :disabled="isReadonly">
                      <label class="col-sm-3">Occurrence date to</label>
                      <div class="col-sm-3" :disabled="isReadonly">
                        <datepicker :typeable="true" :disabledDates="disabledDates" placeholder="DD/MM/YYYY" input-class="form-control" v-model="call_email.occurrence_date_to" />
                      </div>
                    </div>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                  <div class="col-sm-3">
                      <div class="input-group date" id="occurrenceTimeStartPicker">
                        <input :disabled="isReadonly" type="text" class="form-control" placeholder="HH:MM" v-model="call_email.occurrence_time_start"/>
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                      </div>
                  </div>
                  <div v-show="call_email.occurrence_from_to">
                      <label class="col-sm-3">Occurrence time to</label>
                      <div class="col-sm-3">
                          <div class="input-group date" id="occurrenceTimeEndPicker">
                            <input :disabled="isReadonly" type="text" class="form-control" placeholder="HH:MM" v-model="call_email.occurrence_time_end"/>
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                          </div>
                      </div>
                  </div>
                </div></div>
  
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Classification</label>
                  <select :disabled="isReadonly" class="form-control" v-model="call_email.classification_id">
                        <option v-for="option in classification_types" :value="option.id" v-bind:key="option.id">
                          {{ option.name }} 
                        </option>
                    </select>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Report Type</label>
                  <select :disabled="isReadonly" @change.prevent="loadSchema" class="form-control" v-model="call_email.report_type_id">
                          <option v-for="option in report_types" :value="option.id" v-bind:key="option.id">
                            {{ option.report_type }} 
                          </option>
                  </select>
                </div></div>
                
                <div v-for="(item, index) in current_schema">
                  <compliance-renderer-block
                     :readonly=isReadonly"
                     :component="item"
                     v-bind:key="`compliance_renderer_block_${index}`"
                    />
                </div>
              </FormSection>

              <FormSection :formCollapse="true" label="Outcome" Index="3">
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Referred To</label>
                  <select :disabled="isReadonly" class="form-control" v-model="call_email.referrer_id">
                          <option  v-for="option in referrers" :value="option.id" v-bind:key="option.id">
                            {{ option.name }} 
                          </option>
                  </select>
                </div></div>
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice given</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input :disabled="isReadonly" class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>
                <div v-if="call_email.advice_given" class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice details</label>
                  <textarea :readonly="isReadonly" class="form-control" rows="5" v-model="call_email.advice_details"/>
                </div></div>
              </FormSection>
              
              <div class="col-sm-12 form-group"><div class="row">
              <h3></h3>
              </div></div>
            
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
          <CallWorkflow ref="add_workflow" :workflow_type="workflow_type" v-bind:key="workflow_type" />
        </div>
        <Offence ref="offence" />
    </div>
</template>
<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";

import CommsLogs from "@common-components/comms_logs.vue";
import MapLocation from "./map_location.vue";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import SearchPerson from "./search_person.vue";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import Datepicker from 'vuejs-datepicker';
import moment from 'moment';
import CallWorkflow from './call_email_workflow';
import Offence from '../offence/offence';
import 'bootstrap/dist/css/bootstrap.css';
import 'eonasdan-bootstrap-datetimepicker';

export default {
  name: "ViewCallEmail",
  data: function() {
    return {
      disabledDates: {
        from: new Date(),
      },
      workflow_type: '',
      classification_types: [],
      report_types: [],
      referrers: [],
      allocated_group: [],
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
    };
  },
  components: {
    CommsLogs,
    FormSection,
    MapLocation,
    SearchPerson,
    Datepicker,
    CallWorkflow,
    Offence,
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
    ...mapGetters({
      renderer_form_data: 'renderer_form_data',
      current_user: 'current_user',
      // compliance_allocated_group: 'compliance_allocated_group',
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
    personSearchVisible: function(){
        if (this.call_email.status && this.call_email.status.id === 'draft') {
          return false;
        } else {
          return true;
        }
    },
    isReadonly: function() {
        if (this.call_email.status && this.call_email.status.id === 'draft' &&
        this.call_email.assigned_to_id === this.current_user.id) {
          return false;
        } else {
          return true;
        }
    },
    statusDisplay: function() {
      return this.call_email.status ? this.call_email.status.name : '';
    },
    statusId: function() {
      return this.call_email.status ? this.call_email.status.id : '';
    },
    allocateToVisibility: function() {
      if (this.workflow_type.includes('allocate') && this.call_email.allocated_group) {
        return true;
      } else {
        return false;
      }
    },
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
      // loadAllocatedGroup: 'loadAllocatedGroup',
      setRegionId: 'setRegionId',
      setAllocatedGroupList: 'setAllocatedGroupList',
      setOccurrenceTimeStart: 'setOccurrenceTimeStart',
      setOccurrenceTimeEnd: 'setOccurrenceTimeEnd',
    }),
    ...mapActions({
      saveFormData: "saveFormData",
    }),
    ...mapActions({
      loadCurrentUser: "loadCurrentUser",
    }),

    addWorkflow(workflow_type) {
      this.workflow_type = workflow_type;
      this.$nextTick(() => {
        this.$refs.add_workflow.isModalOpen = true;
      });
      // this.$refs.add_workflow.isModalOpen = true;
    },
    offence(){
      this.$refs.offence.isModalOpen = true;
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
    updateAssignedToId: async function () {
        let url = helpers.add_endpoint_join(
            api_endpoints.call_email, 
            this.call_email.id + '/update_assigned_to_id/'
            );
        let res = await Vue.http.post(
            url, 
            { 'assigned_to_id': this.call_email.assigned_to_id }
        );
    }
  },
  beforeRouteEnter: function(to, from, next) {
            next(async (vm) => {
                await vm.loadCurrentUser({ url: `/api/my_compliance_user_details` });
                
            });
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

    // load volunteer group list
    let url = helpers.add_endpoint_join(
                api_endpoints.call_email, 
                this.call_email.id + '/get_allocated_group/'
                );
    let returned_volunteer_list = await Vue.http.get(url);
    if (returned_volunteer_list.body.allocated_group) {
      this.setAllocatedGroupList(returned_volunteer_list.body.allocated_group.members);
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

  }
};
</script>

<style lang="css">
.action-button {
    margin-top: 5px;
}
</style>
