<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-1">Type</label>
                    <div class="col-sm-4">
                        <!-- <select class="form-control" v-on:change="typeSelected($event)"> -->
                        <!-- <select class="form-control" v-on:change="typeSelected($event)" v-bind:value="sanction_outcome.type"> -->
                        <select class="form-control" v-model="sanction_outcome.type">
                            <option v-for="option in options_for_types" v-bind:value="option.id" v-bind:key="option.id">
                                {{ option.display }} 
                            </option>
                        </select>
                    </div>
                </div></div>

                <div v-show="displayTabs">
                    <ul class="nav nav-pills">
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+nTab">{{ firstTabTitle }}</a></li>
                        <li class="nav-item" v-show="displayRemediationActions"><a data-toggle="tab" :href="'#'+aTab">Remediation Actions</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="nTab" class="tab-pane fade in active"><div class="row">

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Region</label>
                                </div>
                                <div class="col-sm-7">
                                  <select class="form-control col-sm-9" v-on:change.prevent="sanction_outcome.region_id=$event.target.value; updateDistricts('updatefromUI')" v-bind:value="sanction_outcome.region_id">
                                    <option  v-for="option in regions" :value="option.id" v-bind:key="option.id">
                                      {{ option.display_name }} 
                                    </option>
                                  </select>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">District</label>
                                </div>
                                <div class="col-sm-7">
                                  <select class="form-control" v-model="sanction_outcome.district_id">
                                    <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                      {{ option.display_name }} 
                                    </option>
                                  </select>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="identifier">Identifier</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-show="sanction_outcome">
                                        <input type="text" class="form-control" name="identifier" placeholder="" v-model="sanction_outcome.identifier" >
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Offence</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-show="sanction_outcome">
                                        <select class="form-control" v-on:change="offenceSelected($event)" v-bind:value="sanction_outcome.current_offence.id">
                                            <option value=""></option>
                                            <option v-for="option in options_for_offences" v-bind:value="option.id" v-bind:key="option.id">
                                                {{ option.id + ': ' + option.status + ', ' + option.identifier }} 
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Offender</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome && sanction_outcome.current_offence && sanction_outcome.current_offence.offenders">
                                    <!-- <div v-if="sanction_outcome"> -->
                                        <select class="form-control" v-on:change="offenderSelected($event)" v-bind:value="sanction_outcome.current_offender.id">
                                            <option value=""></option>
                                            <!-- <option v-for="offender in options_for_offenders" v-bind:value="offender.id" v-bind:key="offender.id"> -->
                                            <option v-for="offender in sanction_outcome.current_offence.offenders" v-bind:value="offender.id" v-bind:key="offender.id">
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

                            <div class="col-sm-12 form-group">
                                <div class="row col-sm-12">
                                    <label class="control-label pull-left">Alleged committed offences</label>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <datatable ref="tbl_alleged_offence" id="tbl_alleged_offence" :dtOptions="dtOptionsAllegedOffence" :dtHeaders="dtHeadersAllegedOffence" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Issued on paper?</label>
                                </div>
                                <div class="col-sm-7">

                                  <input class="col-sm-1" id="issued_on_paper_yes" type="radio" v-model="sanction_outcome.issued_on_paper" :value="true" />
                                  <label class="col-sm-1 radio-button-label" for="issued_on_paper_yes">Yes</label>
                                  <input class="col-sm-1" id="issued_on_paper_no" type="radio" v-model="sanction_outcome.issued_on_paper" :value="false" />
                                  <label class="col-sm-1 radio-button-label" for="issued_on_paper_no">No</label>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Paper ID</label>
                                </div>
                                <div class="col-sm-7">
                                    <input type="text" class="form-control" name="paper_id" placeholder="" v-model="sanction_outcome.paper_id" :disabled="!sanction_outcome.issued_on_paper" /> 
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Paper notice</label>
                                </div>
                                <div id="paper_id_notice">
                                    <div v-if="sanction_outcome.issued_on_paper" class="col-sm-7">
                                        <filefield ref="sanction_outcome_file" name="sanction-outcome-file" :isRepeatable="true" :disabled="!sanction_outcome.issued_on_paper"/>
                                    </div>
                                </div>
                            </div></div>

                        </div></div>

                        <div :id="aTab" class="tab-pane fade in"><div class="row">

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Action</label>
                                </div>
                                <div class="col-sm-7">
                                    <textarea class="form-control" placeholder="add description" id="sanction-outcome-description" v-model="current_remediation_action.action" />
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Due Date</label>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="dueDatePicker">
                                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="current_remediation_action.due_date" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-12">
                                    <input type="button" class="btn btn-primary pull-right" value="Add" @click.prevent="addRemediationActionClicked()" />
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group">
                                <div class="row col-sm-12">
                                    <label class="control-label pull-left">Remediation Actions</label>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <datatable ref="tbl_remediation_actions" id="tbl_remediation_actions" :dtOptions="dtOptionsRemediationActions" :dtHeaders="dtHeadersRemediationActions" />
                                    </div>
                                </div>
                            </div>

                        </div></div>

                        <div :id="dTab" class="tab-pane fade in"><div class="row">
                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Description</label>
                                </div>
                                <div class="col-sm-7">
                                    <textarea class="form-control" placeholder="add description" id="sanction-outcome-description" v-model="sanction_outcome.description"/>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Date of Issue</label>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="dateOfIssuePicker">
                                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="sanction_outcome.date_of_issue" :disabled="!sanction_outcome.issued_on_paper"/>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left">Time of Issue</label>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="timeOfIssuePicker">
                                        <input type="text" class="form-control" placeholder="HH:MM" v-model="sanction_outcome.time_of_issue" :disabled="!sanction_outcome.issued_on_paper" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div></div>
                        </div></div>
                    </div>

                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" :disabled="!displaySendToManagerButton" class="btn btn-default" @click="ok">Send to Manager</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from "vue";
import modal from "@vue-utils/bootstrap-modal.vue";
import datatable from "@vue-utils/datatable.vue";
import filefield from "@/components/common/compliance_file.vue";
import { mapGetters, mapActions } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "../utils";
import $ from "jquery";
import "jquery-ui/ui/widgets/draggable.js";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";

export default {
  name: "SanctionOutcome",
  data: function() {
    let vm = this;

    return {
      nTab: "nTab" + vm._uid,
      aTab: "aTab" + vm._uid,
      dTab: "dTab" + vm._uid,
      isModalOpen: false,
      processingDetails: false,

      regionDistricts: [],
      regions: [], // this is the list of options
      availableDistricts: [], // this is generated from the regionDistricts[] above
      documentActionUrl: null,
      elem_paper_id_notice: null,

      // This is the object to be sent to the server when saving
      sanction_outcome: {
        type: "",
        region_id: null,
        district_id: null,
        identifier: "",
        current_offence: {}, // Store an offence to be saved as an attribute of the sanction outcome
        // The offenders and the alleged_offences under this offence object are used
        // to construct a dropdown list for the offenders and the alleged offences datatable
        current_offender: {}, // Store an offender to be saved as an attribute of the sanction outcome
        issued_on_paper: false,
        paper_id: "",
        description: "",
        date_of_issue: null,
        time_of_issue: null,

        remediation_actions: []
      },
      current_remediation_action: {
        action: "",
        due_date: null
      },

      // List for dropdown
      options_for_types: [],
      options_for_offences: [],

      dtHeadersAllegedOffence: [
        "id",
        "Act",
        "Section/Regulation",
        "Alleged Offence",
        "Include"
      ],
      dtOptionsAllegedOffence: {
        columns: [
          {
            data: "id",
            visible: false
          },
          {
            data: "Act"
          },
          {
            data: "Section/Regulation"
          },
          {
            data: "Alleged Offence"
          },
          {
            data: "Include",
            mRender: function(data, type, row) {
              let ret_line = null;

              if (vm.sanction_outcome.type == 'infringement_notice'){
                ret_line = '<input type="radio" name="infringement_radio_button" class="alleged_offence_include" value="' + data + '"></input>';
              } else if (vm.sanction_outcome.type == '' || vm.sanction_outcome.type == null) {
                // Should not reach here
                ret_line = '';
              } else {
                ret_line = '<input type="checkbox" class="alleged_offence_include" value="' + data + '" checked="checked"></input>';
              }

              return ret_line;
            }
          }
        ]
      },
      dtHeadersRemediationActions: ["id", "Due Date", "Action", "Action"],
      dtOptionsRemediationActions: {
        columns: [
          {
            data: "id",
            visible: false
          },
          {
            data: "due_date"
          },
          {
            data: "action_text"
          },
          {
            data: "action",
            mRender: function(data, type, row) {
              return (
                '<a href="#" class="remove_button" data-remediation-action-id="' +
                row.id +
                '">Remove</a>'
              );
            }
          }
        ]
      }
    };
  },
  components: {
    modal,
    datatable,
    filefield,
  },
  watch: {
    current_type: {
      handler: function(){
        let vm = this;
        vm.sanction_outcome.current_offence = {};
      }
    },
    isModalOpen: {
      handler: function() {
        if (this.isModalOpen) {
          this.modalOpened();
        } else {
          this.modalClosed();
        }
      }
    },
    issued_on_paper: {
      handler: function(){
        let vm = this;
        if (!vm.sanction_outcome.issued_on_paper) {
          vm.sanction_outcome.date_of_issue = null;
          vm.sanction_outcome.time_of_issue = null;

          vm.elem_paper_id_notice.slideUp(500);
        } else {
          vm.elem_paper_id_notice.slideDown(500);
        }
      }
    },
    current_offence: {
      handler: function() {
        this.currentOffenceChanged();
      }
    },
    current_offender: {
      handler: function() {
        this.currentOffenderChanged();
      }
    },
    current_region_id: {
      handler: function() {
        this.currentRegionIdChanged();
      }
    },
    // current_district_id: {
    //   handler: function() {
    //     this.currentDistrictIdChanged();
    //   }
    // }
  },
  computed: {
    ...mapGetters("callemailStore", {
      call_email: "call_email"
    }),
    ...mapGetters("offenceStore", {
      offence: "offence"
    }),
    issued_on_paper: function() {
      return this.sanction_outcome.issued_on_paper;
    },
    current_offence: function() {
      return this.sanction_outcome.current_offence;
    },
    current_offender: function() {
      return this.sanction_outcome.current_offender;
    },
    current_region_id: function() {
      return this.sanction_outcome.region_id;
    },
    current_type: function() {
      return this.sanction_outcome.type;
    },
    modalTitle: function() {
      return "Identify Sanction Outcome";
    },
    firstTabTitle: function() {
      for (let i = 0; i < this.options_for_types.length; i++) {
        if (this.options_for_types[i]["id"] == this.sanction_outcome.type) {
          return this.options_for_types[i]["display"];
        }
      }
      return "";
    },
    displayTabs: function() {
      return this.sanction_outcome.type == "" ? false : true;
    },
    displaySendToManagerButton: function() {
      let retValue = false;
      if (!this.processingDetails && this.sanction_outcome.type) {
        if (this.regionDistrictId) {
          if ((this.sanction_outcome.issued_on_paper && this.sanction_outcome.date_of_issue) || !this.sanction_outcome.issued_on_paper) {
            retValue = true;
          }
        }
      }
      return retValue;
    },
    displayRemediationActions: function() {
      return this.sanction_outcome.type == "remediation_notice" ? true : false;
    },
    regionDistrictId: function() {
      if (
        this.sanction_outcome.district_id ||
        this.sanction_outcome.region_id
      ) {
        return this.sanction_outcome.district_id
          ? this.sanction_outcome.district_id
          : this.sanction_outcome.region_id;
      } else {
        return null;
      }
    }
  },
  methods: {
    ...mapActions("callemailStore", {
      loadCallEmail: "loadCallEmail"
    }),
    ...mapActions("offenceStore", {}),
    ok: async function() {
      await this.sendData();
      this.close();
    },
    cancel: async function() {
        await this.$refs.sanction_outcome_file.cancel();
        this.close();
    },
    makeModalsDraggable: function(){
      this.elem_modal = $('.modal > .modal-dialog');
      for (let i=0; i<this.elem_modal.length; i++){
        $(this.elem_modal[i]).draggable();
      }
    },
    close: function() {
        this.$parent.sanctionOutcomeInitialised = false;
        this.isModalOpen = false;
    },
    modalOpened: function() {},
    modalClosed: function() {
      //this.loadDefaultData();
    },
    loadDefaultData: function() {
      let vm = this;

      vm.sanction_outcome.type = "";
      vm.sanction_outcome.region_id = vm.call_email.region_id;
      vm.sanction_outcome.district_id = vm.call_email.district_id;
      vm.sanction_outcome.identifier = "";
      vm.sanction_outcome.current_offence = {};
      vm.sanction_outcome.current_offender = {};
      vm.sanction_outcome.issued_on_paper = false;
      vm.sanction_outcome.paper_id = "";
      vm.sanction_outcome.description = "";
      vm.sanction_outcome.date_of_issue = null;
      vm.sanction_outcome.time_of_issue = null;
      vm.sanction_outcome.remediation_actions = [];
      vm.current_remediation_action = {
        action: "",
        due_date: null
      };
      vm.clearTableRemediationActions();
    },
    currentRegionIdChanged: function() {
      console.log('currentRegionIdChanged');
      this.updateDistricts();
    },
    addRemediationActionClicked: function() {
      let vm = this;
      if (vm.current_remediation_action) {
        vm.$refs.tbl_remediation_actions.vmDataTable.row
          .add({
            id: helpers.guid(),
            due_date: vm.current_remediation_action.due_date,
            action_text: vm.current_remediation_action.action
          })
          .draw();
        vm.current_remediation_action.action = "";
        vm.current_remediation_action.due_date = null;
      }
    },
    updateDistricts: function(updateFromUI) {
      console.log('updateDistricts');
      if (updateFromUI) {
        // We don't want to clear the default district selection when initially loaded, which derived from the call_email
        this.sanction_outcome.district_id = null;
      }

      this.availableDistricts = []; // This is a list of options for district
      for (let record of this.regionDistricts) {
        if (this.sanction_outcome.region_id == record.id) {
          for (let district_id of record.districts) {
            for (let district_record of this.regionDistricts) {
              if (district_record.id == district_id) {
                this.availableDistricts.push(district_record);
              }
            }
          }
        }
      }

      this.availableDistricts.splice(0, 0, {
        id: "",
        display_name: "",
        district: "",
        districts: [],
        region: null
      });
      // ensure security group members list is up to date
      // this.updateAllocatedGroup();
    },
    // updateAllocatedGroup: function() {
    //   console.log('implement updateAllocatedGroup()');
    // },
    addEventListeners: function() {
      let vm = this;
      let el_issue_date = $(vm.$refs.dateOfIssuePicker);
      let el_due_date = $(vm.$refs.dueDatePicker);
      let el_issue_time = $(vm.$refs.timeOfIssuePicker);

      // Issue "Date" field
      el_issue_date.datetimepicker({
        format: "DD/MM/YYYY",
        maxDate: "now",
        showClear: true
      });
      el_issue_date.on("dp.change", function(e) {
        if (el_issue_date.data("DateTimePicker").date()) {
          vm.sanction_outcome.date_of_issue = e.date.format("DD/MM/YYYY");
        } else if (el_issue_date.data("date") === "") {
          vm.sanction_outcome.date_of_issue = "";
        }
      });

      // Issue "Time" field
      el_issue_time.datetimepicker({ format: "LT", showClear: true });
      el_issue_time.on("dp.change", function(e) {
        if (el_issue_time.data("DateTimePicker").date()) {
          vm.sanction_outcome.time_of_issue = e.date.format("LT");
        } else if (el_issue_time.data("date") === "") {
          vm.sanction_outcome.time_of_issue = "";
        }
      });

      // Due "Date" field
      el_due_date.datetimepicker({
        format: "DD/MM/YYYY",
        maxDate: "now",
        showClear: true
      });
      el_due_date.on("dp.change", function(e) {
        if (el_due_date.data("DateTimePicker").date()) {
          vm.current_remediation_action.due_date = e.date.format("DD/MM/YYYY");
        } else if (el_due_date.data("date") === "") {
          vm.current_remediation_action.due_date = "";
        }
      });

      $("#tbl_remediation_actions").on(
        "click",
        ".remove_button",
        vm.removeClicked
      );
    },
    removeClicked: function(e) {
      let vm = this;
      let remediationActionId = e.target.getAttribute(
        "data-remediation-action-id"
      );
      vm.$refs.tbl_remediation_actions.vmDataTable.rows(function(
        idx,
        data,
        node
      ) {
        if (data.id == remediationActionId) {
          vm.$refs.tbl_remediation_actions.vmDataTable
            .row(idx)
            .remove()
            .draw();
        }
      });
    },
    offenceSelected: function(e) {
      let vm = this;
      let offence_id = parseInt(e.target.value);
      for (let i = 0; i < vm.options_for_offences.length; i++) {
        if (vm.options_for_offences[i].id == offence_id) {
          // Update current offence
          vm.sanction_outcome.current_offence = vm.options_for_offences[i];
          return;
        }
      }
      // User selected the empty line
      vm.sanction_outcome.current_offence = {};
    },
    offenderSelected: function(e) {
      let vm = this;
      let offender_id = parseInt(e.target.value);
      for (
        let i = 0;
        i < vm.sanction_outcome.current_offence.offenders.length;
        i++
      ) {
        if (
          vm.sanction_outcome.current_offence.offenders[i].id == offender_id
        ) {
          // Update current offender
          vm.sanction_outcome.current_offender =
            vm.sanction_outcome.current_offence.offenders[i];
          return;
        }
      }
      // User selected the empty line
      vm.sanction_outcome.current_offender = {};
    },
    typeSelected: function(e) {
      this.sanction_outcome.type = e.target.value;
    },
    constructRegionsAndDistricts: async function() {
      let returned_regions = await cache_helper.getSetCacheList(
        "CallEmail_Regions",
        "/api/region_district/get_regions/"
      );
      Object.assign(this.regions, returned_regions);
      // blank entry allows user to clear selection
      this.regions.splice(0, 0, {
        id: "",
        display_name: "",
        district: "",
        districts: [],
        region: null
      });
      // regionDistricts
      let returned_region_districts = await cache_helper.getSetCacheList(
        "CallEmail_RegionDistricts",
        api_endpoints.region_district
      );
      Object.assign(this.regionDistricts, returned_region_districts);
    },
    sendData: async function() {
      let vm = this;
      let alleged_offence_ids = [];
      let checkboxes = $(".alleged_offence_include");
      for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
          alleged_offence_ids.push(checkboxes[i].value);
        }
      }

      try {
        let fetchUrl = helpers.add_endpoint_json(
          api_endpoints.sanction_outcome,
          "sanction_outcome_save"
        );

        let payload = new Object();
        Object.assign(payload, vm.sanction_outcome);
        if (payload.date_of_issue) {
          payload.date_of_issue = moment(
            payload.date_of_issue,
            "DD/MM/YYYY"
          ).format("YYYY-MM-DD");
        }
        payload.alleged_offence_ids_included = alleged_offence_ids;

        // Retrieve remediation actions and set them to the payload
        let remediation_actions = vm.$refs.tbl_remediation_actions.vmDataTable
          .rows()
          .data()
          .toArray();
        payload.remediation_actions = remediation_actions;
        for (let i = 0; i < payload.remediation_actions.length; i++) {
          payload.remediation_actions[i].due_date = moment(
            payload.remediation_actions[i].due_date,
            "DD/MM/YYYY"
          ).format("YYYY-MM-DD");
        }

        payload.call_email_id = vm.call_email ? vm.call_email.id : null;

        // Set set_sequence to generate lodgement number at the backend
        payload.set_sequence = true;
        console.log(payload);
        const savedObj = await Vue.http.post(fetchUrl, payload);
        await swal("Saved", "The record has been saved", "success");
      } catch (err) {
        if (err.body.non_field_errors) {
          await swal("Error", err.body.non_field_errors[0], "error");
        } else {
          await swal("Error", "There was an error saving the record", "error");
        }
      }
    },
    currentOffenderChanged: function() {
      console.log("currentOffenderChanged");
    },
    clearTableAllegedOffence: function() {
      this.$refs.tbl_alleged_offence.vmDataTable.rows().remove().draw(); // Clear the table anyway
    },
    clearTableRemediationActions: function() {
      this.$refs.tbl_remediation_actions.vmDataTable.rows().remove().draw(); // Clear the table anyway
    },
    currentOffenceChanged: function() {
      let vm = this;

      vm.sanction_outcome.current_offender = {};

      // The dropdown list of the offenders are directly linked to the vm.sanction_outcome.offence.offenders.
      // That's why the dropdown list is updated automatically whenever vm.sanction_outcome.offence is chanaged.

      // Construct the datatable of the alleged offences
      vm.clearTableAllegedOffence();
      if (vm.sanction_outcome.current_offence && vm.sanction_outcome.current_offence.alleged_offences) {
        for (let j = 0; j < vm.sanction_outcome.current_offence.alleged_offences.length; j++) {
          vm.$refs.tbl_alleged_offence.vmDataTable.row
            .add({
              id: vm.sanction_outcome.current_offence.alleged_offences[j].id,
              Act: vm.sanction_outcome.current_offence.alleged_offences[j].act,
              "Section/Regulation": vm.sanction_outcome.current_offence.alleged_offences[j].name,
              "Alleged Offence": vm.sanction_outcome.current_offence.alleged_offences[j].offence_text,
              Include: vm.sanction_outcome.current_offence.alleged_offences[j].id
            })
            .draw();
        }
      }
      // Use checkbox instead of cell click
      // vm.addEventListener();
    },
    updateOptionsForOffences: function(call_email_id) {
      let vm = this;
      let returned = Vue.http.get("/api/offence/filter_by_call_email.json", {
        params: { call_email_id: call_email_id }
      });
      returned.then(res => {
        console.log(res.body);
        vm.options_for_offences = res.body;
      });
    },
    createDocumentActionUrl: async function() {
        // create sanction outcome and get id
        let returned_sanction_outcome = await Vue.http.post(api_endpoints.sanction_outcome);
        this.sanction_outcome.id = returned_sanction_outcome.body.id;
        
        return helpers.add_endpoint_join(
                api_endpoints.sanction_outcome,
                this.sanction_outcome.id + "/process_default_document/"
                )
      },
    },
  created: async function() {
    console.log("In created");
    let vm = this;

    // create sanction outcome and get id
    //let returned_sanction_outcome = await Vue.http.post(api_endpoints.sanction_outcome);
    //this.sanction_outcome.id = returned_sanction_outcome.body.id;
    
    //this.documentActionUrl = helpers.add_endpoint_join(
      //      api_endpoints.sanction_outcome,
        //    this.sanction_outcome.id + "/process_default_document/"
          //  )

    // Load all the types for the sanction outcome
    let options_for_types = await cache_helper.getSetCacheList(
      "SanctionOutcome_Types",
      "/api/sanction_outcome/types.json"
    );
    vm.options_for_types.push({ id: "", display: "" });
    for (let i = 0; i < options_for_types.length; i++) {
      vm.options_for_types.push(options_for_types[i]);
    }
    await vm.updateOptionsForOffences(vm.call_email.id);
    await vm.constructRegionsAndDistricts();
    vm.loadDefaultData();
  },
  mounted: function() {
    this.$nextTick(() => {
      console.log("mounted sanction");
      this.addEventListeners();
      this.elem_paper_id_notice = $('#paper_id_notice');
      this.makeModalsDraggable();
    });
  }
};
</script>

<style lang="css" scoped>
.btn-file {
  position: relative;
  overflow: hidden;
}
.btn-file input[type="file"] {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 100%;
  min-height: 100%;
  font-size: 100px;
  text-align: right;
  filter: alpha(opacity=0);
  opacity: 0;
  outline: none;
  background: white;
  cursor: inherit;
  display: block;
}
.top-buffer {
  margin-top: 5px;
}
.top-buffer-2x {
  margin-top: 10px;
}
.radio-button-label {
  padding-left: 0;
}
.tab-content {
  background: white;
  padding: 10px;
  border: solid 1px lightgray;
}
#DataTable {
  padding: 10px 5px;
  border: 1px solid lightgray;
}
</style>
