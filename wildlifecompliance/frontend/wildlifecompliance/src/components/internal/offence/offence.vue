<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <h3>Offence: {{ displayLodgementNumber }}</h3>
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

                            <div v-if="offence.allocated_group" class="form-group">
                            <div class="row">
                                <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <select :disabled="!offence.user_in_group" class="form-control" v-model="offence.assigned_to_id" @change="updateAssignedToId()">
                                        <option  v-for="option in offence.allocated_group" :value="option.id" v-bind:key="option.id">
                                        {{ option.full_name }} 
                                        </option>
                                    </select>
                                </div>
                            </div>
                            </div>
                            <div v-if="offence.user_in_group">
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
                            <div v-if="visibilitySaveButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="save()" class="btn btn-primary btn-block">
                                        Save
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Save
                            </div>

                            <div v-if="visibilitySanctionOutcomeButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="openSanctionOutcome()" class="btn btn-primary btn-block">
                                        Sanction Outcome
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Sanction Outcome
                            </div>

                            <div v-if="visibilityCloseButton" class="row action-button">
                                <div class="col-sm-12">
                                    <a @click="addWorkflow('close')" class="btn btn-primary btn-block">
                                        Close
                                    </a>
                                </div>
                            </div>
                            <div v-else>
                                Close
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-9" id="main-column">  
                <div class="row">
                    <div class="container-fluid">
                        <ul class="nav nav-pills aho2">
                            <li class="nav-item active"><a data-toggle="tab" :href="'#'+offenceTab">Offence</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+detailsTab">Details</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+offenderTab">Offender(s)</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+locationTab" @click="mapOffenceClicked">Location</a></li>
                            <li class="nav-item"><a data-toggle="tab" :href="'#'+relatedItemsTab">Related Items</a></li>
                        </ul>
                        <div class="tab-content">
                            <div :id="offenceTab" class="tab-pane fade in active">
                                <FormSection :formCollapse="false" label="Offence" Index="0">

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left" for="offence-identifier">Identifier</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <div v-if="offence">
                                                <input type="text" class="form-control" name="identifier" placeholder="" v-model="offence.identifier" v-bind:key="offence.id">
                                            </div>
                                        </div>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <label class="col-sm-3">Use occurrence from/to</label>
                                        <input class="col-sm-1" id="occurrence_from_to_true" type="radio" v-model="offence.occurrence_from_to" v-bind:value="true">
                                        <label class="col-sm-1 radio-button-label" for="occurrence_from_to_true">Yes</label>
                                        <input class="col-sm-1" id="occurrence_from_to_false" type="radio" v-model="offence.occurrence_from_to" v-bind:value="false">
                                        <label class="col-sm-1 radio-button-label" for="occurrence_from_to_false">No</label>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                                        <div class="col-sm-3">
                                            <div class="input-group date" ref="occurrenceDateFromPicker">
                                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_from" />
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                        <div v-show="offence.occurrence_from_to">
                                            <div class="col-sm-3">
                                                <div class="input-group date" ref="occurrenceDateToPicker">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_to" />
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
                                            <div class="input-group date" ref="occurrenceTimeFromPicker">
                                                <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_from" />
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                        <div v-show="offence.occurrence_from_to">
                                            <div class="col-sm-3">
                                                <div class="input-group date" ref="occurrenceTimeToPicker">
                                                    <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_to" />
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <label class="col-sm-3">Alleged Offence</label>
                                        <div class="col-sm-6">
                                            <input class="form-control" id="alleged-offence" />
                                        </div>
                                        <div class="col-sm-3">
                                            <input type="button" class="btn btn-primary" value="Add" @click.prevent="addAllegedOffenceClicked()" />
                                        </div>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <div class="col-sm-12">
                                            <datatable ref="alleged_offence_table" id="alleged-offence-table" :dtOptions="dtOptionsAllegedOffence" :dtHeaders="dtHeadersAllegedOffence" />
                                        </div>
                                    </div></div>
                                </FormSection>
                            </div>
                            <div :id="detailsTab" class="tab-pane face in">
                                <FormSection :formCollapse="false" label="Details" Index="1">
                                    <textarea class="form-control" placeholder="add details" v-model="offence.details" />
                                </FormSection>
                            </div>
                            <div :id="offenderTab" class="tab-pane face in">
                                <FormSection :formCollapse="false" label="Offender(s)" Index="2">
                                    <div class="col-sm-12 form-group"><div class="row">
                                        <input class="col-sm-1" id="offender_individual" type="radio" v-model="offender_search_type" value="individual">
                                        <label class="col-sm-1 radio-button-label" for="offender_individual">Individual</label>
                                        <input class="col-sm-1" id="offender_organisation" type="radio" v-model="offender_search_type" value="organisation">
                                        <label class="col-sm-1 radio-button-label" for="offender_organisation">Organisation</label>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <label class="col-sm-2">Offender</label>
                                        <div class="col-sm-6">
                                            <PersonSearch ref="person_search" elementId="idSetInParent" classNames="col-sm-5 form-control" @person-selected="personSelected" :search_type="offender_search_type" />
                                        </div>
                                        <div class="col-sm-1">
                                            <input type="button" class="btn btn-primary" value="Add" @click.prevent="addOffenderClicked()" />
                                        </div>
                                        <div class="col-sm-2">
                                            <input type="button" class="btn btn-primary" value="Create New Person" @click.prevent="createNewPersonClicked()" />
                                        </div>
                                    </div></div>

                                    <div class="col-sm-12 form-group"><div class="row">
                                        <div class="col-sm-12">
                                          <CreateNewPerson :displayComponent="displayCreateNewPerson" @new-person-created="newPersonCreated"/>
                                        </div>

                                        <div class="col-sm-12">
                                            <datatable ref="offender_table" id="offender-table" :dtOptions="dtOptionsOffender" :dtHeaders="dtHeadersOffender" />
                                        </div>
                                    </div></div>

                                </FormSection>
                            </div>
                            <div :id="locationTab" class="tab-pane face in">
                                <FormSection :formCollapse="false" label="Location" Index="3">
                                    <MapLocation v-if="offence.location" v-bind:key="locationTab" ref="mapLocationComponent" :marker_longitude="offence.location.geometry.coordinates[0]" :marker_latitude="offence.location.geometry.coordinates[1]" @location-updated="locationUpdated"/>
                                    <div :id="idLocationFieldsAddress" v-if="offence.location">
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">Street</label>
                                            <input class="form-control" v-model="offence.location.properties.street" readonly />
                                        </div></div>
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">Town/Suburb</label>
                                            <input class="form-control" v-model="offence.location.properties.town_suburb" readonly />
                                        </div></div>
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">State</label>
                                            <input class="form-control" v-model="offence.location.properties.state" readonly />
                                        </div></div>
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">Postcode</label>
                                            <input class="form-control" v-model="offence.location.properties.postcode" readonly />
                                        </div></div>
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">Country</label>
                                            <input class="form-control" v-model="offence.location.properties.country" readonly />
                                        </div></div>
                                    </div>

                                    <div :id="idLocationFieldsDetails" v-if="offence.location">
                                        <div class="col-sm-12 form-group"><div class="row">
                                            <label class="col-sm-4">Details</label>
                                            <textarea class="form-control location_address_field" v-model="offence.location.properties.details" />
                                        </div></div>
                                    </div>
                                </FormSection>
                            </div>
                            <div :id="relatedItemsTab" class="tab-pane face in">
                                <FormSection :formCollapse="false" label="Related Items" Index="4">
                                    <div class="col-sm-12 form-group"><div class="row">
                                        <div class="col-sm-12">
                                            <RelatedItems v-bind:key="relatedItemsBindId"/>
                                        </div>
                                    </div></div>
                                </FormSection>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="sanctionOutcomeInitialised">
            <SanctionOutcome ref="sanction_outcome" />
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";
import datatable from '@vue-utils/datatable.vue'
import utils from "../utils";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import CommsLogs from "@common-components/comms_logs.vue";
import filefield from '@/components/common/compliance_file.vue';
import OffenceWorkflow from './offence_workflow';
import PersonSearch from "@common-components/search_person.vue";
import CreateNewPerson from "@common-components/create_new_person.vue";
import MapLocation from "../../common/map_location";
import SanctionOutcome from '../sanction_outcome/sanction_outcome_modal';
import 'bootstrap/dist/css/bootstrap.css';
import "awesomplete/awesomplete.css";
import RelatedItems from "@common-components/related_items.vue";
import moment from 'moment';

export default {
    name: 'ViewOffence',
    data() {
        let vm = this;
        vm.STATUS_DRAFT = 'draft';
        vm.STATUS_CLOSING = 'closing';
        vm.STATUS_CLOSED = 'closed';
        vm.STATUS_OPEN = 'open';
        vm.STATUS_DISCARDED = 'discarded';

        vm.max_items = 20;
        vm.ajax_for_alleged_offence = null;
        vm.ajax_for_offender = null;
        vm.suggest_list = []; // This stores a list of alleged offences displayed after search.
        vm.suggest_list_offender = []; // This stores a list of alleged offences displayed after search.
        vm.awe = null;

        return {
            workflow_type :'',
            workflowBindId :'',
            offender_search_type: "individual",
            offenceTab: 'offenceTab' + vm._uid,
            detailsTab: 'detailsTab' + vm._uid,
            offenderTab: 'offenderTab' + vm._uid,
            locationTab: 'locationTab' + vm._uid,
            relatedItemsTab: 'relatedItemsTab' + vm._uid,
            displayCreateNewPerson: false,
            idLocationFieldsAddress: vm.guid + "LocationFieldsAddress",
            idLocationFieldsDetails: vm.guid + "LocationFieldsDetails",
            sanctionOutcomeInitialised: false,

            offence: {
                id: null,
                call_email_id: null,
                inspection_id: null,
                identifier: '',
                status: 'draft',
                offenders: [],
                alleged_offences: [],
                location: {
                    type: 'Feature',
                    properties: {
                        town_suburb: null,
                        street: null,
                        state: 'WA',
                        postcode: null,
                        country: 'Australia',
                        details: ''
                    },
                    geometry: {
                        'type': 'Point',
                        'coordinates': []
                    }
                },
                occurrence_from_to: true,
                occurrence_date_from: null,
                occurrence_date_to: null,
                occurrence_time_from: null,
                occurrence_time_to: null,
                details: ''
            },
            current_alleged_offence: {  // Store the alleged offence temporarily once selected in awesomplete. Cleared when clicking on the "Add" button.
                id: null,
                act: "",
                name: "",
                offence_text: ""
            },
            current_offender: null,  // Store the offender temporarily once selected in awesomplete. Cleared when clicking on the "Add" button.
            offender_search_type: "individual",

            comms_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/comms_log"
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/add_comms_log"
            ),
            logs_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/action_log"
            ),
            dtHeadersOffender: ["id", "Individual/Organisation", "Details", "Action"],
            dtHeadersAllegedOffence: [
                "id",
                "Act",
                "Section/Regulation",
                "Alleged Offence",
                "Action"
            ],
            dtOptionsOffender: {
                columns: [
                    {
                        data: "id",
                        visible: false
                    },
                    {
                        data: "data_type",
                        visible: true,
                        mRender: function(data, type, row) {
                            if(row.removed){
                                return '<strike>' + row.data_type + '</strike>';
                            } else {
                                return row.data_type;
                            }
                        }
                    },
                    {
                        //data: "",
                        mRender: function(data, type, row) {
                            console.log('mRender');
                            if (row.data_type == "individual") {
                                let full_name = [row.first_name, row.last_name].filter(Boolean).join(" ");
                                let email = row.email ? "E:" + row.email : "";
                                let p_number = row.phone_number ? "P:" + row.phone_number : "";
                                let m_number = row.mobile_number ? "M:" + row.mobile_number : "";
                                let dob = row.dob ? "DOB:" + row.dob : "DOB: ---";
                                let myLabel = ["<strong>" + full_name + "</strong>", email, p_number, m_number, dob].filter(Boolean).join("<br />");
                                if (row.removed){
                                    myLabel = '<strike>' + myLabel + '</strike>';
                                }

                                return myLabel;
                            } else if (row.data_type == "organisation") {
                                let name = row.name ? row.name : "";
                                let abn = row.abn ? "ABN:" + row.abn : "";
                                let myLabel = ["<strong>" + name + "</strong>", abn].filter(Boolean).join("<br />");
                                if (row.removed){
                                    myLabel = '<strike>' + myLabel + '</strike>';
                                }

                                return myLabel;
                            }
                        }
                    },
                    {
                        data: "Action",
                        mRender: function(data, type, row) {
                            if (row.removed){
                                return ('<a href="#" class="restore_button" data-offender-id="' + row.id + '">Restore</a>');
                            } else {
                                return ('<a href="#" class="remove_button" data-offender-id="' + row.id + '">Remove</a>');
                            }
                        }
                    }
                ]
            },
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
                    data: "Action",
                    mRender: function(data, type, row) {
                    return (
                        '<a href="#" class="remove_button" data-alleged-offence-id="' +
                        row.id +
                        '">Remove</a>'
                    );
                    }
                }
                ]
            }
        }
    },
    components: {
        FormSection,
        OffenceWorkflow,
        CommsLogs,
        datatable,
        PersonSearch,
        MapLocation,
        CreateNewPerson,
        RelatedItems,
        SanctionOutcome,
    },
    computed: {
        ...mapGetters('offenceStore', {
            //offence: "offence",
        }),
        occurrenceDateLabel: function() {
            if (this.offence.occurrence_from_to) {
                return "Occurrence date from";
            } else {
                return "Occurrence date";
            }
        },
        occurrenceTimeLabel: function() {
            if (this.offence.occurrence_from_to) {
                return "Occurrence time from";
            } else {
                return "Occurrence time";
            }
        },
        statusDisplay: function() {
            let ret = '';
            if (this.offence){
                if (this.offence.status){
                    ret = this.offence.status.name;
                }
            }
            return ret;
        },
        displayLodgementNumber: function() {
            let ret = '';
            if (this.offence){
                ret = this.offence.lodgement_number;
            }
            return ret;
        },
        canUserAction: function() {
            return this.offence.can_user_action;
        },
        visibilitySaveButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.offence.status.id === this.STATUS_DRAFT || this.offence.status.id === this.STATUS_OPEN){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilitySanctionOutcomeButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.offence.status.id === this.STATUS_OPEN){
                    visibility = true;
                }
            }
            return visibility;
        },
        visibilityCloseButton: function() {
            let visibility = false;
            if (this.canUserAction){
                if (this.offence.status.id === this.STATUS_OPEN){
                    visibility = true;
                }
            }
            return visibility;
        },
        relatedItemsBindId: function() {
            let timeNow = Date.now()
            if (this.offence && this.offence.id) {
                return 'offence_' + this.offence.id + '_' + this._uid;
            } else {
                return timeNow.toString();
            }
        },
    },
    methods: {
        save: async function() {
            try{
                let fetchUrl = helpers.add_endpoint_json(api_endpoints.offence, this.offence.id + '/update_offence');
                //fetchUrl = '/api/offence/' + this.offence.id + '/update_offence.json';

                let payload = new Object();
                Object.assign(payload, this.offence);
                if (payload.occurrence_date_from) {
                    payload.occurrence_date_from = moment(payload.occurrence_date_from, 'DD/MM/YYYY').format('YYYY-MM-DD');
                }
                if (payload.occurrence_date_to) {
                    payload.occurrence_date_to = moment(payload.occurrence_date_to, 'DD/MM/YYYY').format('YYYY-MM-DD');
                }
                payload.status = 'open'

                  // Collect offenders data from the datatable, and set them to the vuex
                  let offenders = this.$refs.offender_table.vmDataTable.rows().data().toArray();
                  payload.offenders = offenders;

                  // Collect alleged offence data from the datatable, and set them to the vuex
                  let alleged_offences = this.$refs.alleged_offence_table.vmDataTable.rows().data().toArray();
                  let alleged_offence_ids = alleged_offences.map(a => {
                    return { id: a.id }; // We just need id to create relations between the offence and the alleged offence(s)
                  });
                  payload.alleged_offences = alleged_offence_ids;

                const savedOffence = await Vue.http.post(fetchUrl, payload);
                Vue.set(this, 'offence', savedOffence.body);
                await swal("Saved", "The record has been saved", "success");
                return savedOffence;
            } catch (err) {
                if (err.body.non_field_errors){
                    await swal("Error", err.body.non_field_errors[0], "error");
                } else {
                    await swal("Error", "There was an error saving the record", "error");
                }
            }

        },
        openSanctionOutcome: function() {
          this.sanctionOutcomeInitialised = true;
          this.$nextTick(() => {
              this.$refs.sanction_outcome.isModalOpen = true;
          });
        },
        addWorkflow: function(workflow_type) {

        },
        showHideAddressDetailsFields: function(showAddressFields, showDetailsFields) {
          if (showAddressFields) {
            $("#" + this.idLocationFieldsAddress).fadeIn();
          } else {
            $("#" + this.idLocationFieldsAddress).fadeOut();
          }
          if (showDetailsFields) {
            $("#" + this.idLocationFieldsDetails).fadeIn();
          } else {
            $("#" + this.idLocationFieldsDetails).fadeOut();
          }
        },
        reverseGeocoding: function(coordinates_4326) {
          var self = this;

          $.ajax({
            url:
              "https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/" +
              coordinates_4326.lng +
              "," +
              coordinates_4326.lat +
              ".json?" +
              $.param({
                limit: 1,
                types: "address"
              }),
            dataType: "json",
            success: function(data, status, xhr) {
              let address_found = false;
              if (data.features && data.features.length > 0) {
                for (var i = 0; i < data.features.length; i++) {
                  if (data.features[i].place_type.includes("address")) {
                    self.setAddressFields(data.features[i]);
                    address_found = true;
                  }
                }
              }
              if (address_found) {
                self.showHideAddressDetailsFields(true, false);
                self.setLocationDetailsFieldEmpty();
              } else {
                self.showHideAddressDetailsFields(false, true);
                self.setLocationAddressEmpty();
              }
            }
          });
        },
        setAddressFields(feature) {
            if (this.offence.location){
                  let state_abbr_list = {
                    "New South Wales": "NSW",
                    Queensland: "QLD",
                    "South Australia": "SA",
                    Tasmania: "TAS",
                    Victoria: "VIC",
                    "Western Australia": "WA",
                    "Northern Territory": "NT",
                    "Australian Capital Territory": "ACT"
                  };
                  let address_arr = feature.place_name.split(",");

                  /* street */
                  this.offence.location.properties.street = address_arr[0];

                  /*
                   * Split the string into suburb, state and postcode
                   */
                  let reg = /^([a-zA-Z0-9\s]*)\s(New South Wales|Queensland|South Australia|Tasmania|Victoria|Western Australia|Northern Territory|Australian Capital Territory){1}\s+(\d{4})$/gi;
                  let result = reg.exec(address_arr[1]);
                  /* suburb */
                  this.offence.location.properties.town_suburb = result[1].trim();

                  /* state */
                  let state_abbr = state_abbr_list[result[2].trim()];
                  this.offence.location.properties.state = state_abbr;

                  /* postcode */
                  this.offence.location.properties.postcode = result[3].trim();
                  /* country */

                  this.offence.location.properties.country = "Australia";
            }
        },
        setLocationAddressEmpty() {
            if(this.offence.location){
                this.offence.location.properties.town_suburb = "";
                this.offence.location.properties.street = "";
                this.offence.location.properties.state = "";
                this.offence.location.properties.postcode = "";
                this.offence.location.properties.country = "";
            }
        },
        setLocationDetailsFieldEmpty() {
            if(this.offence.location){
                this.offence.location.properties.details = "";
            }
        },
        locationUpdated: function(latlng){
            // Update coordinate
            this.offence.location.geometry.coordinates[1] = latlng.lat;
            this.offence.location.geometry.coordinates[0] = latlng.lng;
            // Update Address/Details
            this.reverseGeocoding(latlng);
        },
        mapOffenceClicked: function() {
            // Call this function to render the map correctly
            // In some case, leaflet map is not rendered correctly...   Just partialy shown...
            if(this.$refs.mapLocationComponent){
                this.$refs.mapLocationComponent.invalidateSize();
            }
        },
        newPersonCreated: function(obj) {
          if(obj.person){
            this.setCurrentOffender('individual', obj.person.id);

            // Set fullname and DOB into the input box
            let full_name = [obj.person.first_name, obj.person.last_name].filter(Boolean).join(" ");
            let dob = obj.person.dob ? "DOB:" + obj.person.dob : "DOB: ---";
            let value = [full_name, dob].filter(Boolean).join(", ");
            this.$refs.person_search.setInput(value);
          } else if (obj.err) {
            console.log(err);
          } else {
            // Should not reach here
          }
        },
        personSelected: function(para) {
            let vm = this;
            vm.setCurrentOffender(para.data_type, para.id);
        },
        createNewPersonClicked: function() {
          let vm = this;
          vm.newPersonBeingCreated = true;
          vm.displayCreateNewPerson = !vm.displayCreateNewPerson;
        },
        cancelCreateNewPersonClicked: function() {
          let vm = this;
          vm.newPersonBeingCreated = false;
        },
        saveNewPersonClicked: function() {
          let vm = this;
          vm.newPersonBeingCreated = false;
        },
        removeOffenderClicked: function(e) {
          let vm = this;

          let offenderId = parseInt(e.target.getAttribute("data-offender-id"));
          vm.$refs.offender_table.vmDataTable.rows(function(idx, data, node) {
            if (data.id === offenderId) {
                console.log('removeOffenderClicked');
                console.log('idx:' + idx);
              vm.$refs.offender_table.vmDataTable.rows(idx).data()[0].removed = true;
                vm.$refs.offender_table.vmDataTable.rows(idx).invalidate();
            }
          });
        },
        restoreOffenderClicked: function(e){
          let vm = this;

          let offenderId = parseInt(e.target.getAttribute("data-offender-id"));
          vm.$refs.offender_table.vmDataTable.rows(function(idx, data, node) {
            if (data.id === offenderId) {
                console.log('removeOffenderClicked');
                console.log('idx:' + idx);
              vm.$refs.offender_table.vmDataTable.rows(idx).data()[0].removed = false;
                vm.$refs.offender_table.vmDataTable.rows(idx).invalidate();
            }
          });

        },
        removeClicked: function(e) {
          let vm = this;

          let allegedOffenceId = parseInt(
            e.target.getAttribute("data-alleged-offence-id")
          );
          vm.$refs.alleged_offence_table.vmDataTable.rows(function(
            idx,
            data,
            node
          ) {
            if (data.id === allegedOffenceId) {
              vm.$refs.alleged_offence_table.vmDataTable
                .row(idx)
                .remove()
                .draw();
            }
          });
        },
        addOffenderClicked: function() {
          let vm = this;

          if (
            vm.current_offender &&
            vm.current_offender.id &&
            vm.current_offender.data_type
          ) {
            let already_exists = false;

            let ids = vm.$refs.offender_table.vmDataTable.columns(0).data()[0];
            let data_types = vm.$refs.offender_table.vmDataTable.columns(1).data()[0];

            for (let i = 0; i < ids.length; i++) {
              if (ids[i] == vm.current_offender.id && data_types[i] == vm.current_offender.data_type) {
                already_exists = true;
                break;
              }
            }

            if (!already_exists) {
                vm.addOffenderToTable(vm.current_offender);
            }
          }

          vm.setCurrentOffenderEmpty();
        },
        addAllegedOffenceClicked: function() {
          let vm = this;

          if (vm.current_alleged_offence.id) {
            let already_exists = vm.$refs.alleged_offence_table.vmDataTable
              .columns(0)
              .data()[0]
              .includes(vm.current_alleged_offence.id);

            if (!already_exists) {
                vm.addAllegedOffenceToTable(vm.current_alleged_offence);
            }
          }

          vm.setCurrentAllegedOffenceEmpty();
        },
        transferAllegedOffencesToTable: function(){
            // This function is for filling existing alleged offences data into the table
            if (this.offence.alleged_offences){
                for(let i=0; i<this.offence.alleged_offences.length; i++){
                    this.addAllegedOffenceToTable(this.offence.alleged_offences[i]);
                }
                this.offence.alleged_offences = [];
            }
        },
        transferOffendersToTable: function(){
            // This function is for filling existing offenders data into the table
            if (this.offence.offenders){
                for(let i=0; i<this.offence.offenders.length; i++){
                    this.addOffenderToTable(this.offence.offenders[i]);
                }
                this.offence.offenders = [];
            }
        },
        addAllegedOffenceToTable: function(allegedOffence){
              this.$refs.alleged_offence_table.vmDataTable.row.add({
                  id: allegedOffence.id,
                  Act: allegedOffence.act,
                  "Section/Regulation": allegedOffence.name,
                  "Alleged Offence": allegedOffence.offence_text
              }).draw();
        },
        addPersonToTable: function(person) {
              this.$refs.offender_table.vmDataTable.row
                .add({
                  removed: false,
                  reason_for_removal: '',
                  data_type: 'individual',
                  id: person.id,
                  first_name: person.first_name,
                  last_name: person.last_name,
                  email: person.email,
                  p_number: person.p_number,
                  m_number: person.m_numberum,
                  dob: person.dob
                }).draw();
        },
        addPersonExistingToTable: function(offender) {
              this.$refs.offender_table.vmDataTable.row
                .add({
                  removed: offender.removed,
                  reason_for_removal: offender.reason_for_removal,
                  data_type: 'individual',
                  id: offender.person.id,
                  first_name: offender.person.first_name,
                  last_name: offender.person.last_name,
                  email: offender.person.email,
                  p_number: offender.person.p_number,
                  m_number: offender.person.m_numberum,
                  dob: offender.person.dob
                }).draw();
        },
        addOrganisationToTable: function(organisation){
            this.$refs.offender_table.vmDataTable.row
              .add({
                removed: false,
                reason_for_removal: '',
                data_type: 'organisation',
                id: organisation.id,
                name: organisation.name,
                abn: organisation.abn
              }).draw();
        },
        addOrganisationExistingToTable: function(offender){
            this.$refs.offender_table.vmDataTable.row
              .add({
                removed: offender.removed,
                reason_for_removal: offender.reason_for_removal,
                data_type: 'organisation',
                id: offender.organisation.id,
                name: offender.organisation.name,
                abn: offender.organisation.abn
              }).draw();
        },
        addOffenderToTable: function(offender){
            console.log('addOffenderToTable');
            console.log(offender);
            let vm = this;
            if(offender.data_type){
                // When person/organisation is going to be added via input box (awesomplete)
                if (offender.data_type == "individual") {
                    this.addPersonToTable(offender);
                } else if (offender.data_type == "organisation") {
                    this.addOrganisationToTable(offender);
                }
            } else {
                // When inserting the existing data into the table
                if (offender.person) {
                    this.addPersonExistingToTable(offender);
                } else if (offender.organisation) {
                    this.addOrganisationExistingToTable(offender);
                }
            }
        },
        markMatchedText(original_text, input) {
          let ret_text = original_text.replace(new RegExp(input, "gi"), function(
            a,
            b
          ) {
            return "<mark>" + a + "</mark>";
          });
          return ret_text;
        },
        initAwesompleteAllegedOffence: function() {
          var self = this;

          var element_search = document.getElementById("alleged-offence");
          self.awe = new Awesomplete(element_search, {
            maxItems: self.max_items,
            sort: false,
            filter: () => {
              return true;
            }, // Display all the items in the list without filtering.
            item: function(text, input) {
              let ret = Awesomplete.ITEM(text, ""); // Not sure how this works but this doesn't add <mark></mark>
              return ret;
            },
            data: function(item, input) {
              let act = item.act ? item.act : "";
              let name = item.name ? item.name : "";
              let offence_text = item.offence_text ? item.offence_text : "";

              let act_marked = self.markMatchedText(act, input);
              let name_marked = self.markMatchedText(name, input);
              let offence_text_marked = self.markMatchedText(offence_text, input);

              let myLabel = [
                "<strong>" + act_marked + ", " + name_marked + "</strong>",
                offence_text_marked
              ]
                .filter(Boolean)
                .join("<br />");
              myLabel = '<div data-item-id="' + item.id + '">' + myLabel + "</div>";

              return {
                label: myLabel, // Displayed in the list below the search box
                value: [act, name, offence_text].filter(Boolean).join(", "), // Inserted into the search box once selected
                id: item.id
              };
            }
          });
          $(element_search)
            .on("keyup", function(ev) {
              var keyCode = ev.keyCode || ev.which;
              if (
                (48 <= keyCode && keyCode <= 90) ||
                (96 <= keyCode && keyCode <= 105) ||
                keyCode == 8 ||
                keyCode == 46
              ) {
                self.search(ev.target.value);
                return false;
              }
            })
            .on("awesomplete-selectcomplete", function(ev) {
              ev.preventDefault();
              ev.stopPropagation();
              return false;
            })
            .on("awesomplete-select", function(ev) {
              /* Retrieve element id of the selected item from the list
               * By parsing it, we can get the order-number of the item in the list
               */
              let origin = $(ev.originalEvent.origin);
              let originTagName = origin[0].tagName;
              if (originTagName != "DIV") {
                // Assuming origin is a child element of <li>
                origin = origin.parent();
              }
              let elem_id = origin[0].getAttribute("data-item-id");
              for (let i = 0; i < self.suggest_list.length; i++) {
                if (self.suggest_list[i].id == parseInt(elem_id)) {
                  self.setCurrentOffenceSelected(self.suggest_list[i]);
                  break;
                }
              }
            });
        },
        search: function(searchTerm) {
          var vm = this;
          vm.suggest_list = [];
          vm.suggest_list.length = 0;
          vm.awe.list = [];

          /* Cancel all the previous requests */
          if (vm.ajax_for_alleged_offence != null) {
            vm.ajax_for_alleged_offence.abort();
            vm.ajax_for_alleged_offence = null;
          }

          vm.ajax_for_alleged_offence = $.ajax({
            type: "GET",
            url: "/api/search_alleged_offences/?search=" + searchTerm,
            success: function(data) {
              if (data && data.results) {
                let persons = data.results;
                let limit = Math.min(vm.max_items, persons.length);
                for (var i = 0; i < limit; i++) {
                  vm.suggest_list.push(persons[i]);
                }
              }
              vm.awe.list = vm.suggest_list;
              vm.awe.evaluate();
            },
            error: function(e) {}
          });
        },
        searchOrganisation: function(id) {
          return new Promise((resolve, reject) => {
            Vue.http.get("/api/search_organisation/" + id).then(
              response => {
                resolve(response.body);
              },
              error => {
                reject(error);
              }
            );
          });
        },
        setCurrentOffender: function(data_type, id) {
          let vm = this;

          if (data_type == "individual") {
            let initialisers = [utils.fetchUser(id)];
            Promise.all(initialisers).then(data => {
              vm.current_offender = data[0];
              vm.current_offender.data_type = "individual";
            });
          } else if (data_type == "organisation") {
            let initialisers = [vm.searchOrganisation(id)];
            Promise.all(initialisers).then(data => {
              vm.current_offender = data[0];
              vm.current_offender.data_type = "organisation";
            });
          }
        },
        setCurrentOffenceSelected: function(offence) {
          let vm = this;

          if (offence.id) {
            vm.current_alleged_offence.id = offence.id;
            vm.current_alleged_offence.act = offence.act;
            vm.current_alleged_offence.name = offence.name;
            vm.current_alleged_offence.offence_text = offence.offence_text;
          } else {
            vm.setCurrentAllegedOffenceEmpty();
          }
        },
        setCurrentOffenderEmpty: function() {
          let vm = this;

          vm.current_offender = null;

          $("#offender_input").val("");
            vm.$refs.person_search.clearInput();
        },
        setCurrentAllegedOffenceEmpty: function() {
          let vm = this;

          vm.current_alleged_offence.id = null;
          vm.current_alleged_offence.act = "";
          vm.current_alleged_offence.name = "";
          vm.current_alleged_offence.offence_text = "";

          $("#alleged-offence").val("");
        },
        addEventListeners: function() {
          let vm = this;
          let el_fr_date = $(vm.$refs.occurrenceDateFromPicker);
          let el_fr_time = $(vm.$refs.occurrenceTimeFromPicker);
          let el_to_date = $(vm.$refs.occurrenceDateToPicker);
          let el_to_time = $(vm.$refs.occurrenceTimeToPicker);

          // "From" field
          el_fr_date.datetimepicker({
            format: "DD/MM/YYYY",
            maxDate: "now",
            showClear: true
          });
          el_fr_date.on("dp.change", function(e) {
            if (el_fr_date.data("DateTimePicker").date()) {
              vm.offence.occurrence_date_from = e.date.format("DD/MM/YYYY");
            } else if (el_fr_date.data("date") === "") {
              vm.offence.occurrence_date_from = "";
            }
          });
          el_fr_time.datetimepicker({ format: "LT", showClear: true });
          el_fr_time.on("dp.change", function(e) {
            if (el_fr_time.data("DateTimePicker").date()) {
              vm.offence.occurrence_time_from = e.date.format("LT");
            } else if (el_fr_time.data("date") === "") {
              vm.offence.occurrence_time_from = "";
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
              vm.offence.occurrence_date_to = e.date.format("DD/MM/YYYY");
            } else if (el_to_date.data("date") === "") {
              vm.offence.occurrence_date_to = "";
            }
          });
          el_to_time.datetimepicker({ format: "LT", showClear: true });
          el_to_time.on("dp.change", function(e) {
            if (el_to_time.data("DateTimePicker").date()) {
              vm.offence.occurrence_time_to = e.date.format("LT");
            } else if (el_to_time.data("date") === "") {
              vm.offence.occurrence_time_to = "";
            }
          });

          $("#alleged-offence-table").on("click", ".remove_button", vm.removeClicked);
          $("#offender-table").on("click", ".remove_button", vm.removeOffenderClicked);
          $("#offender-table").on("click", ".restore_button", vm.restoreOffenderClicked);
        },
        loadOffence: async function (offence_id) {
            let returnedOffence = await Vue.http.get(helpers.add_endpoint_json(api_endpoints.offence, offence_id));
            if (returnedOffence.body.occurrence_date_to) {
                returnedOffence.body.occurrence_date_to = moment(returnedOffence.body.occurrence_date_to, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            if (returnedOffence.body.occurrence_date_from) {
                returnedOffence.body.occurrence_date_from = moment(returnedOffence.body.occurrence_date_from, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            Vue.set(this, 'offence', returnedOffence.body);
            console.log('returnedOffence');
            console.log(returnedOffence);
        }
    },
    created: async function() {
        if (this.$route.params.offence_id) {
            await this.loadOffence(this.$route.params.offence_id);
            this.transferAllegedOffencesToTable();
            this.transferOffendersToTable();
        }
        this.$nextTick(function() {
            this.initAwesompleteAllegedOffence();
        });
    },
    mounted: function() {
        let vm = this;
        vm.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style>

</style>
