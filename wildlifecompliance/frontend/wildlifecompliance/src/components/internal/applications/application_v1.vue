<template lang="html">
  <div class="container" >

    <p v-if="errors.length">
      <b>Please correct the following error(s):</b>
      <ul>
        <li v-for="error in errors" style='color: red'>{{ error }}</li>
      </ul>
    </p>

    <!-- <div v-if="application" class="container" id="internalApplication"> -->
    <div v-if="application" id="internalApplication">
        <div class="row">
            <!--<span v-if="application.pdf_licence" style="float:right"> -->
            <div v-if="pdf_exists" style="float:right">
                <a :href="application.pdf_licence" target="_blank">Download Licence</a><br>
                <a :href="application.pdf_licence" target="_blank"> <i class="fa fa-file-pdf-o" style="font-size:36px;color:red"></i> </a>
            </div>
            <div style="float:left">
                <h3>Application: {{ application.lodgement_number }}</h3>
                <p>Licence category: {{ application.licence_category }}</p>
            </div>
        </div>

        <div class="col-md-9">
            <div class="row">
                <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">

                    <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
                      <li class="nav-item" v-for="activity_type in application.activity_types">
                        <a class="nav-link" :id="'pills-tab-'+activity_type.activity_name_str" data-toggle="pill" :href="'#pills-'+activity_type.activity_name_str" role="tab" :aria-controls="'pills-'+activity_type.activity_name_str">
                          {{ activity_type.activity_name }}
                        </a>
                      </li>
                    </ul>

                    <div class="tab-content" id="pills-tabContent">
                      <div class="tab-pane fade" v-for="activity_type in application.activity_types" :id="'pills-'+activity_type.activity_name_str" role="tabpanel" :aria-labelledby="'pills-tab-'+activity_type.activity_name_str">
                        <ActivityType :readonly="pdf_exists" :application="application" :activity_type="activity_type" :id="'id_'+activity_type.activity_name_str"></ActivityType>
                      </div>
                    </div>

                    <button class="btn btn-primary btn-save" @click.prevent="save()" :title="saveTitle" :disabled="pdf_exists">Save Changes</button>
                    <button class="btn btn-primary btn-save" @click.prevent="process()" :title="processTitle" :disabled="pdf_exists">Process</button>

                </form>
            </div>
        </div>

<!--
        <div class="col-md-12">
            <div class="row">
                <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
                    <Application form_width="inherit" " v-if="application" :application="application">
                        <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                        <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                        <input type='hidden' name="application_id" :value="1" />
                        <input type='hidden' id="selected_activity_type_tab_id" v-model="selected_activity_type_tab_id" :value=0 />
                        <div v-if="hasAssessorMode" class="row" style="margin-bottom:50px;">
                            <div v-if="wc_version != 1.0" class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                                <div class="navbar-inner">
                                    <div class="container">
                                        <p class="pull-right" style="margin-top:5px;">
                                            <button v-if="canReturnToConditions" class="btn btn-primary" @click.prevent="returnToOfficerConditions()">Return to Officer - Conditions</button>
                                            <button v-if="canCompleteAssessment" class="btn btn-info" @click.prevent="toggleConditions()">Assess</button>
                                            <button v-if="!applicationIsDraft && canRequestAmendment" class="btn btn-primary" @click.prevent="save()">Save Changes</button>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Application>
                </form>
            </div>
        </div>
-->

    </div>
  </div>
</template>
<script>
import Application from '../../form.vue'
import Vue from 'vue'
import ActivityType from './activity_type.vue'
import ProposedDecline from './application_proposed_decline.vue'
import AmendmentRequest from './amendment_request.vue'
import SendToAssessor from './application_send_assessor.vue'
import datatable from '@vue-utils/datatable.vue'
import Conditions from './application_conditions.vue'
import OfficerConditions from './application_officer_conditions.vue'
import ProposedLicence from './proposed_issuance.vue'
import IssueLicence from './application_issuance.vue'
import LicenceScreen from './application_licence.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import MoreReferrals from '@common-utils/more_referrals.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalApplication',
    data: function() {
        let vm = this;
        return {
            applicantTab: 'applicantTab'+vm._uid,
            applicationTab: 'applicationTab'+vm._uid,
            taking_fauna: 'taking_fauna'+vm._uid,
            detailsBody: 'detailsBody'+vm._uid,
            identificationBody: 'identificationBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            checksBody: 'checksBody'+vm._uid,
            assessorsBody:'assessorsBody'+vm._uid,
            isSendingToAssessor: false,
            assessorGroup:{},
            "selectedAssessor":{},
            "application": null,
            "original_application": null,
            "loading": [],
            selected_referral: '',
            selected_assessment_tab:null,
            selected_assessment_id:null,
            selected_activity_type_tab_id:null,
            form: null,
            members: [],
            department_users : [],
            // activity_type_data:[],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingApplication:true,
            showingConditions:false,
            assessmentComplete:false,
            isOfficerConditions:false,
            isFinalViewConditions:false,
            isofficerfinalisation:false,
            state_options: ['conditions','processing'],
            contacts_table_id: vm._uid+'contacts-table',
            application_assessor_datatable:vm._uid+'assessment-table',
            selected_assesment_index:0,
            contacts_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.contactsURL,
                    "dataSrc": ''
                },
                columns: [
                    {
                        title: 'Name',
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {
                        title: 'Phone',
                        data:'phone_number'
                    },
                    {
                        title: 'Mobile',
                        data:'mobile_number'
                    },
                    {
                        title: 'Fax',
                        data:'fax_number'
                    },
                    {
                        title: 'Email',
                        data:'email'
                    },
                  ],
                  processing: true
            },
            contacts_table: null,
            assessors_headers:["Assessor Group","Date Sent","Status","Action"],
            assessors_options:{},
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            comms_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/action_log'),
            panelClickersInitialised: false,
            sendingReferral: false,
            title: null,
            errors: [],

        }
    },
    components: {
        Application,
        ActivityType,
        datatable,
        ProposedDecline,
        AmendmentRequest,
        SendToAssessor,
        Conditions,
        OfficerConditions,
        ProposedLicence,
        IssueLicence,
        LicenceScreen,
        CommsLogs,
        MoreReferrals
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    watch: {
    },
    computed: {
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        application_form_url: function() {
          return (this.application) ? `/api/application/${this.application.id}/assess_save.json` : '';
        },
        wc_version: function (){
            return this.$root.wc_version;
        },
        pdf_exists: function() {
            return this.application.pdf_licence != null;
        },
        saveTitle: function() {
            return this.pdf_exists ? 'The application has already been processed': 'Save and continue'
        },
        processTitle: function() {
            return this.pdf_exists ? 'The application has already been processed': 'Create Licences and PDF'
        },

    },
    methods: {
        save: function(e) {
            let vm = this;
            vm.form = document.forms.new_application;
            let formData = new FormData(vm.form);
            vm.$http.post(vm.application_form_url,formData).then(res=>{
              swal(
                'Saved',
                'Your application has been saved',
                'success'
              )
            },err=>{
            });
        },
        validate: function(formData) {
            let vm = this;
            vm.errors = [];

            formData.forEach((value,key) => {
                if (key.indexOf('comment-field') == -1) { // exclude comment fields in validation
                    if (key.indexOf('issue_date') !== -1 || key.indexOf('start_date') !== -1 || key.indexOf('expiry_date') !== -1) {
                        if (value == '') {
                            vm.errors.push('Required field: ' + key);
                            console.log(key+" "+value)
                        }
                    }
                }
            });

            if (!vm.errors.length) {
                // there are no errors
                return true;
            } else {
                return false;
            }

        },
        process: function(e) {
            let vm = this;
            vm.form = document.forms.new_application;
            let formData = new FormData(vm.form);
            if (! vm.validate(formData)) {
                return
            };
            formData.append('action', 'process');
            vm.$http.post(vm.application_form_url,formData).then(res=>{
              swal(
                'Processed',
                'Your application has been processed',
                'success'
              )
            },err=>{
            });
            //location.reload(true);
        },


        save_wo: function() {
            let vm = this;
            let formData = new FormData(vm.form);
            vm.$http.post(vm.application_form_url,formData).then(res=>{

            },err=>{
            });
        },

    },
    mounted: function() {
        let vm = this;
    },
    updated: function(){
        let vm = this;
        $('.nav-pills a:first').tab('show'); // doing it this way since the tabs loop has no 'active' tab set
    },
    beforeRouteEnter: function(to, from, next) {
          Vue.http.get(`/api/application/${to.params.application_id}/internal_application.json`).then(res => {
              next(vm => {
                vm.application = res.body;
                vm.original_application = helpers.copyObject(res.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
              });
            },
            err => {
              console.log(err);
            });
    },
    beforeRouteUpdate: function(to, from, next) {
          Vue.http.get(`/api/application/${to.params.application_id}.json`).then(res => {
              next(vm => {
                vm.application = res.body;
                vm.original_application = helpers.copyObject(res.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
              });
            },
            err => {
              console.log(err);
            });
    }
}

</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
