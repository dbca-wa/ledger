<template lang="html">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <h3>Inspection: {{ inspection.number }}</h3>
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

                        <div v-if="inspection.allocated_group" class="form-group">
                          <div class="row">
                            <div class="col-sm-12 top-buffer-s">
                              <strong>Currently assigned to</strong><br/>
                            </div>
                          </div>
                          <div class="row">
                            <div class="col-sm-12">
                              
                              <select :disabled="!inspection.user_in_group" class="form-control" v-model="inspection.assigned_to_id" @change="updateAssignedToId()">
                                <option  v-for="option in inspection.allocated_group" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div v-if="inspection.user_in_group">
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
                        
                        <!--div v-if="statusId ==='open' && this.call_email.can_user_action" class="row action-button">
                          <div class="col-sm-12">
                                <a ref="save" @click="save()" class="btn btn-primary btn-block">
                                  Save
                                </a>
                          </div>
                        </div-->

                        <div class="row action-button">
                          <div v-if="sendToManagerVisibility" class="col-sm-12">
                                <a ref="close" @click="addWorkflow('send_to_manager')" class="btn btn-primary btn-block">
                                  Send to Manager
                                </a>
                          </div>
                        </div>
                        
                        <div class="row action-button">
                          <div v-if="endorseVisibility" class="col-sm-12">
                                <a ref="close" @click="addWorkflow('endorse')" class="btn btn-primary btn-block">
                                  Endorse
                                </a>
                          </div>
                        </div>
                        
                        <div class="row action-button">
                          <div v-if="requestAmendmentVisibility" class="col-sm-12">
                                <a ref="close" @click="addWorkflow('request_amendment')" class="btn btn-primary btn-block">
                                  Request Amendment
                                </a>
                          </div>
                        </div>
                        
                        <div class="row action-button">
                          <div v-if="offenceVisibility" class="col-sm-12">
                                <a @click="open_offence()" class="btn btn-primary btn-block">
                                  Offence
                                </a>
                          </div>
                        </div>

                        <div  class="row action-button">
                          <div v-if="sanctionOutcomeVisibility" class="col-sm-12">
                                <a @click="open_sanction_outcome()" class="btn btn-primary btn-block">
                                  Sanction Outcome
                                </a>
                          </div>
                        </div>
                        
                        <div  class="row action-button">
                          <div v-if="!readonlyForm" class="col-sm-12">
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
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+iTab">Inspection</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+cTab">Checklist</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+oTab">Outcomes</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+rTab">Related Items</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="iTab" class="tab-pane fade in active">

                          <FormSection :formCollapse="false" label="Inspection Details" Index="0">
                            
                            <div class="form-group">
                              <div class="row">
                                <div class="col-sm-3">
                                  <label>Inspection Type</label>
                                </div>
                                <div class="col-sm-6">
                                  <select :disabled="readonlyForm" class="form-control" v-model="inspection.inspection_type_id" @change="loadSchema">
                                    <option  v-for="option in inspectionTypes" :value="option.id" v-bind:key="option.id">
                                      {{ option.inspection_type }}
                                    </option>
                                  </select>
                                </div>
                              </div>
                            </div>
                            <div class="form-group">
                              <div class="row">
                                <div class="col-sm-3">
                                  <label>Title</label>
                                </div>
                                <div class="col-sm-9">
                                  <input :readonly="readonlyForm" class="form-control" v-model="inspection.title"/>
                                </div>
                              </div>
                            </div>
                            <div class="form-group">
                              <div class="row">
                                <div class="col-sm-3">
                                  <label>Details</label>
                                </div>
                                <div class="col-sm-9">
                                  <textarea :readonly="readonlyForm" class="form-control" v-model="inspection.details"/>
                                </div>
                              </div>
                            </div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Planned for (Date)</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="plannedForDatePicker">
                                        <input :disabled="readonlyForm" type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="inspection.planned_for_date" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                
                                <label class="col-sm-3">Planned for (Time)</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" id="plannedForTimePicker">
                                      <input :disabled="readonlyForm" type="text" class="form-control" placeholder="HH:MM" v-model="inspection.planned_for_time"/>
                                      <span class="input-group-addon">
                                          <span class="glyphicon glyphicon-calendar"></span>
                                      </span>
                                    </div>
                                </div>
                            </div></div>
                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-4">Party Inspected</label>
                                    <input :disabled="readonlyForm" class="col-sm-1" id="individual" type="radio" v-model="inspection.party_inspected" v-bind:value="`individual`">
                                    <label class="col-sm-1" for="individual">Person</label>
                                    <input :disabled="readonlyForm" class="col-sm-1" id="organisation" type="radio" v-model="inspection.party_inspected" v-bind:value="`organisation`">
                                    <label class="col-sm-1" for="organisation">Organisation</label>
                            </div></div>
                            
                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-8">
                                    <SearchPerson :isEditable="!readonlyForm" classNames="form-control" elementId="search-person" :search_type="inspection.party_inspected" @person-selected="personSelected"ref="search_person"/>
                                </div>
                                <!--div class="col-sm-1">
                                    <input type="button" class="btn btn-primary" value="Add" @click.prevent="addOffenderClicked()" />
                                </div-->
                                <div class="col-sm-2">
                                    <input type="button" class="btn btn-primary" value="Create New Person" @click.prevent="createNewPersonClicked()" />
                                </div>
                            </div></div>
                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-12">
                                  <CreateNewPerson :displayComponent="displayCreateNewPerson" @new-person-created="newPersonCreated"/>
                                </div>
                            </div></div>
                            <div class="col-sm-12 form-group"><div class="row">
                              <label class="col-sm-4" for="inspection_inform">Inform party being inspected</label>
                              <input type="checkbox" id="inspection_inform" v-model="inspection.inform_party_being_inspected">
                              
                            </div></div>
                          </FormSection>
                          <FormSection :formCollapse="false" label="Inspection Team" Index="1">
                            <div class="form-group">
                              <div class="row">
                                <div class="col-sm-6">
                                  <select :disabled="readonlyForm" class="form-control" v-model="teamMemberSelected" >
                                    <option  v-for="option in inspection.allocated_group" :value="option.id" v-bind:key="option.id">
                                      {{ option.full_name }}
                                    </option>
                                  </select>
                                </div>
                                <div class="col-sm-2">
                                    <button @click.prevent="addTeamMember" class="btn btn-primary">Add Member</button>
                                </div>
                                <!--div class="col-sm-2">
                                    <button @click.prevent="makeTeamLead" class="btn btn-primary">Make Team Lead</button>
                                </div-->
                                <!--div class="col-sm-2">
                                    <button @click.prevent="clearInspectionTeam" class="btn btn-primary pull-right">Clear</button>
                                </div-->
                              </div>
                            </div>
                            <div class="col-sm-12 form-group"><div class="row">
                                <div v-if="inspection">
                                    <datatable ref="inspection_team_table" id="inspection-team-table" :dtOptions="dtOptionsInspectionTeam" :dtHeaders="dtHeadersInspectionTeam" />
                                </div>
                            </div></div>
                          </FormSection>
            
                          
                        </div>  
                        <div :id="cTab" class="tab-pane fade in">
                            <FormSection :formCollapse="false" label="Checklist">
                                <div class="col-sm-12 form-group"><div class="row">
                                    <div v-if="current_schema" v-for="(item, index) in current_schema">
                                      <compliance-renderer-block
                                         :component="item"
                                         v-bind:key="`compliance_renderer_block${index}`"
                                        />
                                    </div>
                                </div></div>
                            </FormSection>
                        </div>
                        <div :id="oTab" class="tab-pane fade in">
                            <FormSection :formCollapse="false" label="Inspection report">
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="Name">Inspection Report</label>
                                        </div>
                                        <div class="col-sm-9" v-if="inspection.inspectionReportDocumentUrl">
                                            <filefield ref="inspection_report_file" name="inspection-report-file" :isRepeatable="false" :documentActionUrl="inspection.inspectionReportDocumentUrl" @update-parent="loadInspectionReport"/>
                                        </div>
                                    </div>
                                </div>
                            </FormSection>
                            <FormSection :formCollapse="false" label="Sanction Outcomes">
                                <div class="col-sm-12 form-group"><div class="row">
                                    <div class="col-sm-12">
                                        
                                    </div>
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

        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    
                                    <input type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                </p>
                            </div>
                        </div>
        </div>          
        <!--div v-if="workflow_type">
          <InspectionWorkflow ref="add_workflow" :workflow_type="workflow_type" v-bind:key="workflowBindId" />
        </div-->
        <Offence ref="offence" :parent_update_function="loadInspection" />
        <div v-if="sanctionOutcomeInitialised">
            <SanctionOutcome ref="sanction_outcome" :parent_update_function="loadInspection"/>
        </div>
        <InspectionWorkflow ref="inspection_workflow" :workflow_type="workflow_type" v-bind:key="workflowBindId" />
    </div>
</template>
<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";
import SearchPerson from "@/components/common/search_person.vue";
import CreateNewPerson from "@common-components/create_new_person.vue";
import CommsLogs from "@common-components/comms_logs.vue";
import datatable from '@vue-utils/datatable.vue'
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import moment from 'moment';
import 'bootstrap/dist/css/bootstrap.css';
import 'eonasdan-bootstrap-datetimepicker';
import Offence from '../offence/offence';
import SanctionOutcome from '../sanction_outcome/sanction_outcome_modal';
import filefield from '@/components/common/compliance_file.vue';
import InspectionWorkflow from './inspection_workflow.vue';
import RelatedItems from "@common-components/related_items.vue";


export default {
  name: "ViewInspection",
  data: function() {
    return {
      iTab: 'iTab'+this._uid,
      rTab: 'rTab'+this._uid,
      oTab: 'oTab'+this._uid,
      cTab: 'cTab'+this._uid,
      current_schema: [],
      //createInspectionBindId: '',
      workflowBindId: '',
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
      dtHeadersInspectionTeam: [
          'Name',
          'Role',
          '',
          '',
      ],
      dtOptionsInspectionTeam: {
          ajax: {
              'url': '/api/inspection/' + this.$route.params.inspection_id + '/get_inspection_team/',
              'dataSrc': '',
          },

          columns: [
              {
                  data: 'full_name',
              },
              {
                  data: 'member_role',
              },
              {
                  data: 'id',
                  mRender: function(data, type, row){
                        return (
                        '<a href="#" class="remove_button" data-member-id="' + row.id + '">Remove</a>'
                              );
                  }
              },
              {
                  data: 'action',
                  mRender: function(data, type, row){
                      if (data === 'Member') {
                        return (
                        '<a href="#" class="make_team_lead" data-member-id="' + row.id + '">Make Team Lead</a>'
                              );
                      } else {
                          return ('');
                      }
                  }
              }
          ]
      },
      // disabledDates: {
      //   from: new Date(),
      // },
      workflow_type: '',
      
      sectionLabel: "Details",
      sectionIndex: 1,
      pBody: "pBody" + this._uid,
      loading: [],
      inspectionTypes: [],
      teamMemberSelected: null,
      displayCreateNewPerson: false,
      newPersonBeingCreated: false,
      //party_inspected: '',
      
      //callemailTab: "callemailTab" + this._uid,
      comms_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/comms_log"
      ),
      comms_add_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/add_comms_log"
      ),
      logs_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/action_log"
      ),
      //workflowBindId: '',
      sanctionOutcomeInitialised: false,
    };
  },
  components: {
    CommsLogs,
    FormSection,
    datatable,
    SearchPerson,
    CreateNewPerson,
    Offence,
    SanctionOutcome,
    filefield,
    InspectionWorkflow,
    RelatedItems,
  },
  computed: {
    ...mapGetters('inspectionStore', {
      inspection: "inspection",
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    statusDisplay: function() {
        return this.inspection.status ? this.inspection.status.name : '';
    },
    readonlyForm: function() {
        return !this.inspection.can_user_action;
    },
    canUserAction: function() {
        return this.inspection.can_user_action;
    },
    inspectionReportExists: function() {
        return this.inspection.inspection_report.length > 0 ? true : false;
    },
    offenceExists: function() {
        for (let item of this.inspection.related_items) {
            if (item.model_name.toLowerCase() === 'offence') {
                return true
            }
        }
        // return false if no related item is an Offence
        return false
    },
    sendToManagerVisibility: function() {
        if (this.inspection.status && !this.readonlyForm && this.inspectionReportExists) {
            if (this.inspection.status.id.includes('open', 'request_amendment')) {
                return true;
            }
        } else {
            return false;
        }
    },
    endorseVisibility: function() {
        if (this.inspection.status && !this.readonlyForm) {
            return this.inspection.status.id === 'with_manager' ? true : false;
        } else {
            return false;
        }
    },
    testProblem: function() {
        if (this.canUserAction) {
            return true;
        } else {
            return false;
        }
    },
    requestAmendmentVisibility: function() {
        if (this.inspection.status && !this.readonlyForm) {
            return this.inspection.status.id === 'with_manager' ? true : false;
        } else {
            return false;
        }
    },
    offenceVisibility: function() {
        if (this.inspection.status && !this.readonlyForm) {
            return this.inspection.status.id === 'open' ? true : false;
        } else {
            return false;
        }
    },
    sanctionOutcomeVisibility: function() {
        if (this.inspection.status && this.offenceExists && !this.readonlyForm) {
            return this.inspection.status.id === 'open' ? true : false;
        } else {
            return false;
        }
    },
    relatedItemsBindId: function() {
        let timeNow = Date.now()
        if (this.inspection && this.inspection.id) {
            return 'inspection_' + this.inspection.id + '_' + this._uid;
        } else {
            return timeNow.toString();
        }
    },
    relatedItemsVisibility: function() {
        if (this.inspection && this.inspection.id) {
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
    ...mapActions('inspectionStore', {
      loadInspection: 'loadInspection',
      saveInspection: 'saveInspection',
      setInspection: 'setInspection', 
      setPlannedForTime: 'setPlannedForTime',
      modifyInspectionTeam: 'modifyInspectionTeam',
      setPartyInspected: 'setPartyInspected',
      setRelatedItems: 'setRelatedItems',
    }),
    newPersonCreated: function(obj) {
        console.log(obj);
        if(obj.person){
            this.setPartyInspected({data_type: 'individual', id: obj.person.id});

        // Set fullname and DOB into the input box
        let full_name = [obj.person.first_name, obj.person.last_name].filter(Boolean).join(" ");
        let dob = obj.person.dob ? "DOB:" + obj.person.dob : "DOB: ---";
        let value = [full_name, dob].filter(Boolean).join(", ");
        this.$refs.search_person.setInput(value);
      } else if (obj.err) {
        console.log(err);
      } else {
        // Should not reach here
      }
    },
    loadInspectionReport: function() {
        console.log("loadInspectionReport")
        this.loadInspection({inspection_id: this.inspection.id});
    },

    loadSchema: function() {
      this.$nextTick(async function() {
      let url = helpers.add_endpoint_json(
                    api_endpoints.inspection_types,
                    this.inspection.inspection_type_id + '/get_schema',
                    );
      let returned_schema = await cache_helper.getSetCache(
        'InspectionTypeSchema', 
        this.inspection.id.toString(),
        url);
      if (returned_schema) {
        this.current_schema = returned_schema.schema;
      }
        
      });
    },

    open_sanction_outcome(){

      this.sanctionOutcomeInitialised = true;
      this.$nextTick(() => {
          this.$refs.sanction_outcome.isModalOpen = true;
          this.constructRelatedItemsTable();
      });
    },
    open_offence(){
      this.offenceInitialised = true;
      this.$refs.offence.isModalOpen = true;
    },
    createNewPersonClicked: function() {
      this.newPersonBeingCreated = true;
      this.displayCreateNewPerson = !this.displayCreateNewPerson;
    },
    addTeamMember: async function() {
        await this.modifyInspectionTeam({
            user_id: this.teamMemberSelected, 
            action: 'add'
        });
        this.$refs.inspection_team_table.vmDataTable.ajax.reload()
    },
    removeTeamMember: async function(e) {
        let memberId = e.target.getAttribute("data-member-id");
        await this.modifyInspectionTeam({
            user_id: memberId,
            action: 'remove'
        });
        this.$refs.inspection_team_table.vmDataTable.ajax.reload()
    },
    makeTeamLead: async function(e) {
        let memberId = e.target.getAttribute("data-member-id");
        await this.modifyInspectionTeam({
            user_id: memberId, 
            action: 'make_team_lead'
        });
        this.$refs.inspection_team_table.vmDataTable.ajax.reload()
    },
    personSelected: function(para) {
        console.log(para);
        this.setPartyInspected(para);
    },
    updateWorkflowBindId: function() {
        let timeNow = Date.now()
        if (this.workflow_type) {
            this.workflowBindId = this.workflow_type + '_' + timeNow.toString();
        } else {
            this.workflowBindId = timeNow.toString();
        }
    },
    constructRelatedItemsTable: function() {
        console.log('constructRelatedItemsTable');
        
        let vm = this;
        
        vm.$refs.related_items_table.vmDataTable.clear().draw();

        if(vm.inspection.related_items){
          for(let i = 0; i<vm.inspection.related_items.length; i++){
            let already_exists = vm.$refs.related_items_table.vmDataTable.columns(0).data()[0].includes(vm.inspection.related_items[i].id);

            if (!already_exists){
                vm.$refs.related_items_table.vmDataTable.row.add(
                    {
                        'identifier': vm.inspection.related_items[i].identifier,
                        'descriptor': vm.inspection.related_items[i].descriptor,
                        'model_name': vm.inspection.related_items[i].model_name,
                        'Action': vm.inspection.related_items[i],
                    }
                ).draw();
            }
          }
        }
    },
    addWorkflow(workflow_type) {
      this.workflow_type = workflow_type;
      this.updateWorkflowBindId();
      this.$nextTick(() => {
        this.$refs.inspection_workflow.isModalOpen = true;
      });
      // this.$refs.add_workflow.isModalOpen = true;
    },
    save: async function () {
        if (this.inspection.id) {
            await this.saveInspection({ route: false, crud: 'save' });
        } else {
            await this.saveInspection({ route: false, crud: 'create'});
            this.$nextTick(function () {
                this.$router.push(
                  { name: 'view-inspection', 
                    params: { id: this.inspection.id }
                  });
            });
        }
    },
    saveExit: async function() {
      if (this.inspection.id) {
        await this.saveInspection({ route: true, crud: 'save' });
      } else {
        await this.saveInspection({ route: true, crud: 'create'});
      }
    },
    duplicate: async function() {
      await this.saveInspection({ route: false, crud: 'duplicate'});
    },
    addEventListeners: function() {
      let vm = this;
      let el_fr_date = $(vm.$refs.plannedForDatePicker);
      let el_fr_time = $(vm.$refs.plannedForTimePicker);

      // "From" field
      el_fr_date.datetimepicker({
        format: "DD/MM/YYYY",
        minDate: "now",
        showClear: true
      });
      el_fr_date.on("dp.change", function(e) {
        if (el_fr_date.data("DateTimePicker").date()) {
          vm.inspection.planned_for_date = e.date.format("DD/MM/YYYY");
        } else if (el_fr_date.data("date") === "") {
          vm.inspection.planned_for_date = "";
        }
      });
      el_fr_time.datetimepicker({ format: "LT", showClear: true });
      el_fr_time.on("dp.change", function(e) {
        if (el_fr_time.data("DateTimePicker").date()) {
          vm.inspection.planned_for_time = e.date.format("LT");
        } else if (el_fr_time.data("date") === "") {
          vm.inspection.planned_for_time = "";
        }
      });
      $('#inspection-team-table').on(
          'click',
          '.remove_button',
          vm.removeTeamMember,
          );
      $('#inspection-team-table').on(
          'click',
          '.make_team_lead',
          vm.makeTeamLead,
          );
    },
    updateAssignedToId: async function (user) {
        let url = helpers.add_endpoint_join(
            api_endpoints.inspection, 
            this.inspection.id + '/update_assigned_to_id/'
            );
        let payload = null;
        if (user === 'current_user' && this.inspection.user_in_group) {
            payload = {'current_user': true};
        } else if (user === 'blank') {
            payload = {'blank': true};
        } else {
            payload = { 'assigned_to_id': this.inspection.assigned_to_id };
        }
        let res = await Vue.http.post(
            url,
            payload
        );
        await this.setInspection(res.body); 
    },
  },
  created: async function() {
      if (this.$route.params.inspection_id) {
          await this.loadInspection({ inspection_id: this.$route.params.inspection_id });
      }
      console.log(this)

      // inspection_types
      let returned_inspection_types = await cache_helper.getSetCacheList(
          'InspectionTypes',
          api_endpoints.inspection_types
          );
      Object.assign(this.inspectionTypes, returned_inspection_types);
      // blank entry allows user to clear selection
      this.inspectionTypes.splice(0, 0,
          {
            id: "",
            description: "",
          });
    
    //if (this.$route.params.inspection_id) {
      //await this.loadInspection({ inspection_id: this.$route.params.inspection_id });
    //}

      // Set Individual or Organisation in search field
      if (this.inspection.individual_inspected) {
          let value = [
              this.inspection.individual_inspected.full_name, 
              this.inspection.individual_inspected.dob].
              filter(Boolean).join(", ");
          this.$refs.search_person.setInput(value);
      } else if (this.inspection.organisation_inspected) {
          let value = [
              this.inspection.organisation_inspected.name,
              this.inspection.organisation_inspected.abn].
              filter(Boolean).join(", ");
          this.$refs.search_person.setInput(value);
      }
      // load Inspection report
      //await this.$refs.inspection_report_file.get_documents();
      // load current Inspection renderer schema
      if (this.inspection.inspection_type_id) {
          await this.loadSchema();
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
      $('#plannedForTimePicker').datetimepicker({
              format: 'LT'
          });
      $('#plannedForTimePicker').on('dp.change', function(e) {
          vm.setPlannedForTime(e.date.format('LT'));
      });
      
      this.$nextTick(async () => {
          this.addEventListeners();
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
</style>
