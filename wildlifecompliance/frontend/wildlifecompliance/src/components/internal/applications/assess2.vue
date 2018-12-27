<template lang="html">
    <!-- <div v-if="application" class="container" id="internalApplication"> -->
    <div v-if="application" id="internalApplication">
        <div class="row">
            <h3>Application: {{ application.lodgement_number }}</h3>
            <h3>Class name: {{ application.class_name }}</h3>
            <h3>Activity Types: {{ application.activity_types }}</h3>
        </div>

        <div class="col-md-9">
            <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">

              <li class="nav-item">
                <div class ="col-sm-12" v-for="activity_type in application.activity_types">
                  <a class="nav-link active" id="'pills-tab-'+activity_type.activity_name" data-toggle="pill" href="'#pills-'+activity_type.activity_name" role="tab" aria-controls="'pills-'+activity_type.activity_name" aria-selected="true">
                    {{ activity_type }}
                  </a>
                </div>
              </li>


              <!--
              <li class="nav-item">
                <a class="nav-link active" id="pills-applicant-tab" data-toggle="pill" href="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
                  Fauna Exporting
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-activities-land-tab" data-toggle="pill" href="#pills-activities-land" role="tab" aria-controls="pills-activities-land" aria-selected="false">
                  Fauna Importing
                </a>
              </li>
              -->

            </ul>

            <div class="tab-content" id="pills-tabContent">

              <div class="tab-pane fade show active" id="'pills-'+activity_type.activity_name" role="tabpanel" aria-labelledby="'pills-tab-'+activity_type.activity_name">
                <ActivityType :activity_type="activity_type" id="'id_'+activity_type.activity_name"></ActivityType> -->
              </div>


              <!--
              <div class="tab-pane fade show active" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab"> 
                <ActivityType :activity_type="activity_type" id="'id_'+activity_type"></ActivityType> -->
              </div>
              <div class="tab-pane fade" id="pills-activities-land" role="tabpanel" aria-labelledby="pills-activities-land-tab">
                <ActivityType :activity_type="activity_type" id="'id_'+activity_type"></ActivityType> -->
              </div>
              -->
            </div>
        </div>

    </div>
</template>
<script>
import Application from '../../form.vue'
import Vue from 'vue'
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
        }
    },
    components: {
        Application,
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
        applicationIsDraft: function(){
            return this.application.processing_status == 'Draft';
        },
        selectedTabId: function(){
            return this.selected_activity_type_tab_id;
        },
        selectedActivityType: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].id == this.selectedTabId){
                    return activity_types_list[i];
                }
            }
        },
        canIssueDecline: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].processing_status == 'With Officer-Finalisation'){
                    return true;
                }
            }
            return false;
        },
        canRequestAmendment: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].processing_status == 'With Officer'){
                    return true;
                }
            }
            return false;
        },
        canSendToAssessor: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].processing_status == 'With Officer' || activity_types_list[i].processing_status == 'With Officer-Conditions' || activity_types_list[i].processing_status == 'With Assessor'){
                    return true;
                }
            }
            return false;
        },
        canReturnToConditions: function(){
            return this.selectedTabId && this.selectedActivityType.processing_status == 'With Officer-Finalisation' ? true : false;
        },
        canOfficerReviewConditions: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].processing_status == 'With Officer-Conditions'){
                    return true;
                }
            }
            return false;
        },
        canProposeIssueOrDecline: function(){
            var activity_types_list = this.application.licence_type_data.activity_type
            for(var i=0;i<activity_types_list.length;i++){
                if(activity_types_list[i].processing_status == 'With Officer-Conditions'){
                    return true;
                }
            }
            return false;
        },
        canCompleteAssessment: function(){
            return this.selectedTabId && this.selectedActivityType.processing_status == 'With Assessor' ? true : false;
        },
        contactsURL: function(){
            return this.application!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.application.org_applicant.id+'/contacts') : '';
        },
        applicantType: function(){
            if (this.application.org_applicant){
                return 'org';
            } else if (this.application.proxy_applicant){
                return 'proxy';
            } else {
                return 'submitter';
            }
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        application_form_url: function() {
          return (this.application) ? `/api/application/${this.application.id}/assessor_save.json` : '';
        },
        isFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity_type.length; i<len; i++){
                if(vm.application.licence_type_data.activity_type[i].processing_status == 'Declined' || vm.application.licence_type_data.activity_type[i].processing_status == 'Accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag==len){
                return true;
            }
            else{
                return false;
            }
            
        },
        isPartiallyFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity_type.length; i<len; i++){
                if(vm.application.licence_type_data.activity_type[i].processing_status == 'Declined' || vm.application.licence_type_data.activity_type[i].processing_status == 'Accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag!=len){
                return true;
            }
            else{
                return false;
            }
            
        },
        canAssess: function(){
            return this.application && this.application.assessor_mode.assessor_can_assess ? true : false;
        },
        hasAssessorMode:function(){
            return this.application && this.application.assessor_mode.has_assessor_mode ? true : false;
        },
        isIdCheckAccepted: function(){
            return this.application.id_check_status == 'Accepted';
        },
        isIdNotChecked: function(){
            return this.application.id_check_status == 'Not Checked';
        },
        isIdCheckRequested: function(){
            return this.application.id_check_status == 'Awaiting Update';
        },
        isIdCheckUpdated: function(){
            return this.application.id_check_status == 'Updated';
        },
        isCharacterCheckAccepted: function(){
            return this.application.character_check_status == 'Accepted';
        },
        canAction: function(){
            if (this.application.processing_status == 'With Approver'){
                return this.application && (this.application.processing_status == 'With Approver' || this.application.processing_status == 'With Assessor' || this.application.processing_status == 'With Assessor (Conditions)') && !this.isFinalised && !this.application.can_user_edit && (this.application.current_assessor.id == this.application.assigned_approver || this.application.assigned_approver == null ) && this.application.assessor_mode.assessor_can_assess? true : false;
            }
            else{
                return this.application && (this.application.processing_status == 'With Approver' || this.application.processing_status == 'With Assessor' || this.application.processing_status == 'With Assessor (Conditions)') && !this.isFinalised && !this.application.can_user_edit && (this.application.current_assessor.id == this.application.assigned_officer || this.application.assigned_officer == null ) && this.application.assessor_mode.assessor_can_assess? true : false;
            }
        },
        canLimitedAction: function(){
            if (this.application.processing_status == 'With Approver'){
                return this.application && (this.application.processing_status == 'With Assessor' || this.application.processing_status == 'With Referral' || this.application.processing_status == 'With Assessor (Conditions)') && !this.isFinalised && !this.application.can_user_edit && (this.application.current_assessor.id == this.application.assigned_approver || this.application.assigned_approver == null ) && this.application.assessor_mode.assessor_can_assess? true : false;
            }
            else{
                return this.application && (this.application.processing_status == 'With Assessor' || this.application.processing_status == 'With Referral' || this.application.processing_status == 'With Assessor (Conditions)') && !this.isFinalised && !this.application.can_user_edit && (this.application.current_assessor.id == this.application.assigned_officer || this.application.assigned_officer == null ) && this.application.assessor_mode.assessor_can_assess? true : false;
            }
        },
        canSeeSubmission: function(){
            return this.application && (this.application.processing_status != 'With Assessor (Conditions)' && this.application.processing_status != 'With Approver' && !this.isFinalised)
        },
        wc_version: function (){
            return this.$root.wc_version;
        }
    },
    methods: {
        
        eventListeners: function(){
            let vm = this;

            // Listeners for Send to Assessor datatable actions
            if (vm.$refs.assessorDatatable) {
                for (var i=0; i < vm.$refs.assessorDatatable.length; i++) {
                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_remind',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/remind_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Sent',
                                 'An email has been sent to assessor with the request to assess this Application',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });

                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_resend',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/resend_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Sent',
                                 'An email has been sent to assessor with the request to re-assess this Application',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                                vm.refreshFromResponse(res);
                            });

                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });

                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_recall',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/recall_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Success',
                                 'An assessment for this Application has been recalled',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                                vm.refreshFromResponse(res);
                            });
                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });
                }
            }
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            if (vm.application && vm.applicantType == 'org' && !vm.contacts_table_initialised){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.application.org_applicant.id+'/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        proposedDecline: function(){
            this.$refs.proposed_decline.decline = this.application.applicationdeclineddetails != null ? helpers.copyObject(this.application.applicationdeclineddetails): {};
            this.$refs.proposed_decline.isModalOpen = true;
        },
        sendtoAssessor: function(item1){
            let vm=this;
            this.$refs.send_to_assessor.assessment.licence_activity_type=item1;
            this.$refs.send_to_assessor.assessment.assessor_group=this.selectedAssessor.id;
            this.$refs.send_to_assessor.assessment.assessor_group_name=this.selectedAssessor.display_name;
            this.$refs.send_to_assessor.assessment.text='';
            if (typeof this.selectedAssessor.id == 'undefined' || typeof this.selectedAssessor.display_name == 'undefined'){
              swal(
                'Error',
                'Please select an Assessor Group to send the request to.',
                'error'
              )
            } else {
                this.$refs.send_to_assessor.isModalOpen=true;
            }
        },
        clearSendToAssessorForm(){
            this.$refs.send_to_assessor.assessment.text='';
            this.selectedAssessor={};
        },
        setAssessorTab(_index){
            return _index === 0 ? 'active' : '';
        },
        setAssessorTabContent(_index){
            return _index === 0 ? 'tab-pane fade in active' : 'tab-pane fade in';
        },
        proposedLicence: function(){
            var activity_type_name=[]
            var selectedTabTitle = $("#tabs-section li.active");
            // var tab_id=selectedTabTitle.children().attr('href').split(/(\d)/)[1]
            var tab_id=selectedTabTitle.children().attr('href').split('#')[1]
            
            this.$refs.proposed_licence.propose_issue.licence_activity_type_id=tab_id
            this.$refs.proposed_licence.propose_issue.licence_activity_type_name=selectedTabTitle.text();
            // this.$refs.proposed_licence.licence = this.application.proposed_issuance_licence != null ? helpers.copyObject(this.application.proposed_issuance_licence) : {};
            this.$refs.proposed_licence.isModalOpen = true;
        },
        toggleIssue:function(){
            // this.$refs.proposed_licence.licence = helpers.copyObject(this.application.proposed_issuance_licence);
            // this.$refs.proposed_licence.state = 'final_licence';
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            this.isofficerfinalisation=true;
        },
        acceptIdRequest: function() {
            let vm = this;
            swal({
                title: "Accept ID Check",
                text: "Are you sure you want to accept this ID Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/accept_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        resetIdRequest: function() {
            let vm = this;
            swal({
                title: "Reset ID Check",
                text: "Are you sure you want to reset this ID Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/reset_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        updateIdRequest: function() {
            let vm = this;
            swal({
                title: "Request Update ID Check",
                text: "Are you sure you want to request this ID Check update?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/request_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        acceptCharacterRequest: function() {
            let vm = this;
            swal({
                title: "Accept Character Check",
                text: "Are you sure you want to accept this Character Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/accept_character_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        refreshAssessorDatatables: function(){
            var vm = this;
            for (var i=0;i<vm.$refs.assessorDatatable.length;i++){
                vm.$refs.assessorDatatable[i].vmDataTable.ajax.reload();
            }
        },
        amendmentRequest: function(){
            let vm = this;
            vm.save_wo();
            let values = '';
            var activity_type_name=[];
            var activity_type_id=[];
            var selectedTabTitle;

            $('.deficiency').each((i,d) => {
                values +=  $(d).val() != '' ? `Question - ${$(d).data('question')}\nDeficiency - ${$(d).val()}\n`: '';
            });

            selectedTabTitle = $("#tabs-section li.active");
            vm.tab_name = $(selectedTabTitle).text();
            vm.tab_id = selectedTabTitle.children().attr('href').split('#')[1];

            activity_type_id.push(vm.tab_id);
            activity_type_name.push(vm.tab_name);

            vm.$refs.amendment_request.amendment.text = values;
            vm.$refs.amendment_request.amendment.activity_type_name = activity_type_name;
            vm.$refs.amendment_request.amendment.activity_type_id = activity_type_id;
            vm.$refs.amendment_request.isModalOpen = true;

            if (values === ''){
               swal(
                  'Amendment Request',
                  'There are no deficiencies entered for this Application.',
                  'error'
               )
               vm.$refs.amendment_request.isModalOpen = false;
            }
        },
        togglesendtoAssessor:function(){
            let vm=this;
            $('#tabs-main li').removeClass('active');
            vm.isSendingToAssessor = !vm.isSendingToAssessor;
            vm.showingApplication = false;
            vm.showingConditions = false;
            setTimeout(function(){
                $('#tabs-assessor li:first-child a')[0].click();
            }, 50);
            vm.fetchAssessorGroup();
        },
        save: function(e) {
            let vm = this;
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
        save_wo: function() {
            let vm = this;
            let formData = new FormData(vm.form);
            vm.$http.post(vm.application_form_url,formData).then(res=>{

            },err=>{
            });
        },
        toggleApplication:function(){
            this.showingApplication = !this.showingApplication;
            if(this.isSendingToAssessor){
                this.isSendingToAssessor=!this.isSendingToAssessor
            }
            if(this.showingConditions){
                this.showingConditions=!this.showingConditions
            }
            if(this.isOfficerConditions){
                this.isOfficerConditions=!this.isOfficerConditions
            }
            if(this.isFinalViewConditions){
                this.isFinalViewConditions=!this.isFinalViewConditions
            }
            if(this.isofficerfinalisation){
                this.isofficerfinalisation=!this.isofficerfinalisation
            }
            setTimeout(function(){
                $('#tabs-main li a')[1].click();
            }, 50);
        },
        toggleConditions:function(){
            this.showingConditions = true;
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            var selectedTabTitle = $("#tabs-section li.active");
            var tab_id=selectedTabTitle.children().attr('href').split('#')[1]
            this.selected_assessment_tab=tab_id
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);
        },
        returnToOfficerConditions: function(){
            let vm = this;
            vm.updateActivityStatus(vm.selectedActivityType.id,'With Officer-Conditions');
            swal(
                 'Return to Officer - Conditions',
                 'The licenced activity has been returned to Officer - Conditions.',
                 'success'
            );
        },
        toggleOfficerConditions:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=true;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            var selectedTabTitle = $("#tabs-section li.active");
            var tab_id=selectedTabTitle.children().attr('href').split('#')[1]
            this.selected_assessment_tab=tab_id
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);

        },
        toggleFinalViewConditions:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=true;
            this.assessmentComplete=false;
            var selectedTabTitle = $("#tabs-section li.active");
            var tab_id=selectedTabTitle.children().attr('href').split('#')[1]
            this.selected_assessment_tab=tab_id
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);

        },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            if (vm.application.processing_status == 'With Approver'){
                $(vm.$refs.assigned_officer).val(vm.application.assigned_approver);
                $(vm.$refs.assigned_officer).trigger('change');
            }
            else{
                $(vm.$refs.assigned_officer).val(vm.application.assigned_officer);
                $(vm.$refs.assigned_officer).trigger('change');
            }
        },
        completeAssessment:function(){
            let vm = this;
            let data = new FormData();

            var selectedTabTitle = $("li.active");
            var tab_id=selectedTabTitle.children().attr('href').split('#')[1]
            
            vm.selected_assessment_tab=tab_id

            data.selected_assessment_tab=vm.selected_assessment_tab
            data.application_id=vm.application_id
            
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/complete_assessment')),JSON.stringify(data),{emulateJSON:true})
            .then((response) => {
                swal(
                             'Complete Assessment',
                             'The assessment is successfully marked as complete.',
                             'success'
                        );

                vm.application = response.body;
                vm.refreshFromResponse(response)
                vm.showingApplication = true;
                vm.isSendingToAssessor=false;
                vm.showingConditions=false;
                vm.assessmentComplete=true;
                swal(
                     'Complete Assessment',
                     'The assessment has been successfully completed',
                     'success'
                )
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        assignRequestUser: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assign_request_user')))
            .then((response) => {
                vm.application = response.body;
                vm.original_application = helpers.copyObject(response.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.original_application = helpers.copyObject(response.body);
            vm.application = helpers.copyObject(response.body);
            if (vm.applicantType == 'org') {
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
            };
            if (vm.applicantType == 'proxy') {
                vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
            };
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        assignTo: function(){
            let vm = this;
            let unassign = true;
            let data = {};
            if (vm.processing_status == 'With Approver'){
                unassign = vm.application.assigned_approver != null && vm.application.assigned_approver != 'undefined' ? false: true;
                data = {'assessor_id': vm.application.assigned_approver};
            }
            else{
                unassign = vm.application.assigned_officer != null && vm.application.assigned_officer != 'undefined' ? false: true;
                data = {'assessor_id': vm.application.assigned_officer};
            }
            if (!unassign){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assign_to')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    vm.application = response.body;
                    vm.original_application = helpers.copyObject(response.body);
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.application = helpers.copyObject(vm.original_application)
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Application Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
            else{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/unassign')))
                .then((response) => {
                    vm.application = response.body;
                    vm.original_application = helpers.copyObject(response.body);
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.application = helpers.copyObject(vm.original_application)
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Application Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
        },
        updateActivityStatus: function(activity_id, status){
            let vm = this;
            //vm.isSendingToAssessor = !vm.isSendingToAssessor;
            let data = {
                'activity_id' : activity_id,
                'status': status
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/update_activity_status')),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                vm.application = response.body;
                vm.original_application = helpers.copyObject(response.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
//                vm.$nextTick(() => {
//                    vm.initialiseAssignedOfficerSelect(true);
//                    vm.updateAssignedOfficerSelect();
//                });
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        fetchDeparmentUsers: function(){
            let vm = this;
            vm.loading.push('Loading Department Users');
            vm.$http.get(api_endpoints.department_users).then((response) => {
                vm.department_users = response.body
                vm.loading.splice('Loading Department Users',1);
            },(error) => {
                console.log(error);
                vm.loading.splice('Loading Department Users',1);
            })
        },
        fetchAssessorGroup: function(){
            let vm = this;
            let data = {'application_id' : vm.application.id };
            vm.loading.push('Fetching assessor group');
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessor_group,'user_list'),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                vm.assessorGroup = response.body;
            },(error) => {
                console.log(error);
            });
        },
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                if (vm.application.processing_status == 'With Approver'){
                    vm.application.assigned_approver = selected.val();
                }
                else{
                    vm.application.assigned_officer = selected.val();
                }
                vm.assignTo();
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                if (vm.application.processing_status == 'With Approver'){
                    vm.application.assigned_approver = null;
                }
                else{
                    vm.application.assigned_officer = null;
                }
                vm.assignTo();
            });
        },
        initialiseSelects: function(){
            let vm = this;
            if (!vm.initialisedSelects){
                $(vm.$refs.department_users).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Referral"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = '' 
                });
                vm.initialiseAssignedOfficerSelect();
                vm.initialisedSelects = true;
            }
        },
        sendReferral: function(){
            let vm = this;
            let data = {'email':vm.selected_referral};
            vm.sendingReferral = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assesor_send_referral')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                vm.sendingReferral = false;
                vm.original_application = helpers.copyObject(response.body);
                vm.application = response.body;
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                swal(
                    'Referral Sent',
                    'The referral has been sent to '+vm.department_users.find(d => d.email == vm.selected_referral).name,
                    'success'
                )
                $(vm.$refs.department_users).val(null).trigger("change");
                vm.selected_referral = '';
            }, (error) => {
                console.log(error);
                swal(
                    'Referral Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                vm.sendingReferral = false;
            });
        },
        remindReferral:function(r){
            let vm = this;
            
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind')).then(response => {
                vm.original_application = helpers.copyObject(response.body);
                vm.application = response.body;
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                swal(
                    'Referral Reminder',
                    'A reminder has been sent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        resendReferral:function(r){
            let vm = this;
            
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/resend')).then(response => {
                vm.original_application = helpers.copyObject(response.body);
                vm.application = response.body;
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                swal(
                    'Referral Resent',
                    'The referral has been resent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        recallReferral:function(r){
            let vm = this;
            
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/recall')).then(response => {
                vm.original_application = helpers.copyObject(response.body);
                vm.application = response.body;
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                swal(
                    'Referral Recall',
                    'The referall has been recalled from '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.fetchDeparmentUsers();
        vm.$nextTick(function () {
            for (var i=0;i<vm.application.licence_type_data.activity_type.length;i++) {
                var activity_type_id = vm.application.licence_type_data.activity_type[i].id
                vm.assessors_options[activity_type_id] = {
                     language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    ajax: {
                        "url": helpers.add_endpoint_join(api_endpoints.applications,vm.$route.params.application_id+'/assessment_details/?licence_activity_type='+activity_type_id),
                        "dataSrc": ''
                    },
                    columns: [
                        {data:'assessor_group.display_name'},
                        {data:'date_last_reminded'},
                        {data:'status'},
                        {
                            mRender:function (data,type,full) {
                                let links = '';
                                    if(full.status == 'Completed'){
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_resend">Resend</a>&nbsp;`;

                                    } else if(full.status == 'Awaiting Assessment'){
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_remind">Remind</a>&nbsp;`;
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_recall">Recall</a>&nbsp;`;
                                        // links +=  `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Recall</a><br/>`;
                                    }
                                return links;
                            }}
                    ],
                    processing: true
                }
            }

        })
    },
    updated: function(){
        let vm = this;
        if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            }); 
            vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
            vm.initialiseSelects();
            
            vm.form = document.forms.new_application;
            vm.eventListeners();
        });
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
