<template lang="html">
    <div v-if="proposal" class="container" id="internalReferral">
            <div class="row">
        <h3>Application: {{ proposal.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" comms_add_url="test"/>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ proposal.submitter.first_name }} {{ proposal.submitter.last_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ proposal.lodgement_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ proposal.processing_status }}
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Referrals</strong><br/>
                                <div class="form-group" v-if="!isFinalised">
                                    <!--
                                    <select :disabled="isFinalised || proposal.can_user_edit" ref="department_users" class="form-control">
                                        <option value="null"></option>
                                        <option v-for="user in department_users" :value="user.email">{{user.name}}</option>
                                    </select>
                                    -->

                                    <select :disabled="  proposal.can_user_edit || isFinalised" ref="referral_recipient_groups" class="form-control">
                                        <option value="null"></option>
                                        <option v-for="group in referral_recipient_groups" :value="group">{{group}}</option>
                                    </select>

                                    <template v-if='!sendingReferral'>
                                        <template v-if="selected_referral && !isFinalised && !proposal.can_user_edit && referral.sent_from == 1">
                                            <label class="control-label pull-left"  for="Name">Comments</label>
                                            <textarea class="form-control" name="name" v-model="referral_text"></textarea>
                                            <a v-if="!isFinalised && !proposal.can_user_edit && referral.sent_from == 1" @click.prevent="sendReferral()" class="actionBtn pull-right">Send</a>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <span v-if="!isFinalised && !proposal.can_user_edit && referral.sent_from == 1" class="text-primary pull-right">
                                            Sending Referral&nbsp;
                                            <i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
                                        </span>
                                    </template>
                                </div>
                                <table class="table small-table">
                                    <tr>
                                        <th>Referral</th>
                                        <th>Status/Action</th>
                                    </tr>
                                    <!-- <tr v-for="r in proposal.latest_referrals"> -->
                                    <tr v-for="r in referral.latest_referrals">
                                        <td>
                                            <small><strong>{{r.referral}}</strong></small><br/>
                                            <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                        </td>
                                        <td><small><strong>{{r.processing_status}}</strong></small><br/>
                                        <template v-if="!isFinalised && referral.referral == proposal.current_assessor.id">
                                            <template v-if="r.processing_status == 'Awaiting'">
                                                <small><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)"href="#">Recall</a></small>
                                            </template>
                                            <template v-else>
                                                <small><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                            </template>
                                        </template>
                                        </td>
                                    </tr>
                                </table>
                                <MoreReferrals @refreshFromResponse="refreshFromResponse" :proposal="proposal" :canAction="!isFinalised && referral.referral == proposal.current_assessor.id" :isFinalised="isFinalised" :referral_url="referralListURL"/>
                            </div>
                            <!-- {{!isFinalised}}
                            {{referral.referral == proposal.current_assessor.id}}
                            {{referral.can_be_completed}}
                            {{referral.referral}}
                            {{proposal.current_assessor.id}} -->
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12">
                                    <strong>Application</strong><br/>
                                    <a class="actionBtn" v-if="!showingProposal" @click.prevent="toggleProposal()">Show Application</a>
                                    <a class="actionBtn" v-else @click.prevent="toggleProposal()">Hide Application</a>
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <!--
                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && referral.referral == proposal.current_assessor.id && referral.can_be_completed">
                            -->
                            <!-- <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && referral.can_be_completed && referral.can_process"> -->
                            <div class="col-sm-12 top-buffer-s" v-if="referral.can_process && referral.can_be_completed">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <strong>Action</strong><br/>
                                    </div>
                                </div>
                                <div class="row">
                                    <!--
                                    <div class="col-sm-12">
                                        <label class="control-label pull-left"  for="Name">Comments</label>
                                        <textarea class="form-control" name="name" v-model="referral_comment"></textarea>
                                        <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="completeReferral">Complete Referral Task</button>
                                    </div>
                                    -->

                                    <div class="">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" @click.prevent="completeReferral2()">Complete Referral Task</button><br/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <CompleteReferral ref="complete_referral" :referral_id="referral.id" :proposal_id="referral.proposal.id"@refreshFromResponse="refreshFromResponse"></CompleteReferral>

        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row" >
                <!-- <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Applicant
                                    <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="detailsBody">
                                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                    </a>
                                </h3> 
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="detailsBody">
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Name</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.applicant.name">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="proposal.applicant.abn">
                                        </div>
                                      </div>
                                  </form>
                            </div>
                        </div>
                    </div>
                </div> -->
                <!-- <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Address Details
                                    <a class="panelClicker" :href="'#'+addressBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="addressBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3> 
                            </div>
                            <div class="panel-body panel-collapse collapse" :id="addressBody">
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Street</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="street" placeholder="" v-model="proposal.applicant.address.line1">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="proposal.applicant.address.locality">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="country" placeholder="" v-model="proposal.applicant.address.state">
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="proposal.applicant.address.postcode">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <input disabled type="text" class="form-control" name="country" v-model="proposal.applicant.address.country"/>
                                        </div>
                                      </div>
                                   </form>
                            </div>
                        </div>
                    </div>
                </div> -->
                <!-- <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Contact Details
                                    <a class="panelClicker" :href="'#'+contactsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="contactsBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse" :id="contactsBody">
                                <table ref="contacts_datatable" :id="contacts_table_id" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                                </table>
                            </div>
                        </div>
                    </div>
                </div> -->
                <Requirements :proposal="proposal" :hasReferralMode="hasReferralMode" :referral_group="referral.referral_group"/>
                <Assessment :proposal="proposal" :assessment="referral.referral_assessment" :hasReferralMode="hasReferralMode" :is_internal="is_internal" :is_referral="is_referral"></Assessment>
                <div class="col-md-12" v-if="showingProposal">
                    <div class="row">
                        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
                                
                                <ProposalTClass v-if="proposal && proposal.application_type=='T Class'" :proposal="proposal" id="proposalStart" :canEditActivities="false" :is_external="false" :is_referral="true" :referral="referral" :hasReferralMode="hasReferralMode"></ProposalTClass>
                                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                                <input type='hidden' name="proposal_id" :value="1" />
                                <div class="navbar navbar-fixed-bottom" v-if="!proposal.can_user_edit && !isFinalised" style="background-color: #f5f5f5 ">
                                        <div class="navbar-inner">
                                            <div v-if="!isFinalised" class="container">
                                            <p class="pull-right">                       
                                            <button class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="save()">Save Changes</button>
                                            </p>                      
                                            </div>                   
                                        </div>
                                </div>      
                        </form>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
</template>
<script>
import Proposal from '../../form.vue'
import ProposalTClass from '@/components/form_tclass.vue'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import MoreReferrals from '@common-utils/more_referrals.vue'
import CompleteReferral from './complete_referral.vue'
import Requirements from '@/components/internal/proposals/proposal_requirements.vue'
import Assessment from '@/components/common/tclass/assessment.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
export default {
    name: 'Referral',
    data: function() {
        let vm = this;
        return {
            detailsBody: 'detailsBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            //"proposal": null,
            referral: null,
            referral_sent_list: null,
            "loading": [],
            selected_referral: '',
            referral_text: '',
            referral_comment: '',
            sendingReferral: false,
            showingProposal:false,
            form: null,
            members: [],
            department_users : [],
            referral_recipient_groups : [],
            contacts_table_initialised: false,
            initialisedSelects: false,
            contacts_table_id: vm._uid+'contacts-table',
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
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            logs_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/comms_log'),
            panelClickersInitialised: false,
            referral: {}
        }
    },
    components: {
        Proposal,
        datatable,
        CommsLogs,
        MoreReferrals,
        CompleteReferral,
        ProposalTClass,
        Requirements,
        Assessment
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    watch: {
    },
    computed: {
        proposal: function(){
            return this.referral != null && this.referall != 'undefined' ? this.referral.proposal : null;
        },
        hasReferralMode: function(){
            return this.referral && this.referral.can_process? true: false;
        },
        contactsURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.proposal.applicant.id+'/contacts') : '';
        },
        referralListURL: function(){
            return this.referral!= null ? helpers.add_endpoint_json(api_endpoints.referrals,this.referral.id+'/referral_list') : '';
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        proposal_form_url: function() {
          return (this.proposal) ? `/api/proposal/${this.proposal.id}/assessor_save.json` : '';
        },
        isFinalised: function(){
            return !(this.referral != null  && this.referral.processing_status == 'Awaiting'); 
        },
        referral_form_url: function() {
          return (this.referral) ? `/api/referrals/${this.referral.id}/complete_referral.json` : '';
        },
    },
    methods: {
        completeReferral2: function(){
            //this.save_wo();
            let values = '';
            //$('.deficiency').each((i,d) => {
            //    values +=  $(d).val() != '' ? `Question - ${$(d).data('question')}\nDeficiency - ${$(d).val()}\n\n`: '';
            //}); 
            //this.$refs.amendment_request.amendment.text = values;
            this.$refs.complete_referral.isModalOpen = true;
        },
        toggleProposal:function(){
            this.showingProposal = !this.showingProposal;
        },
        save_wo: function() {
          let vm = this;
          //let formData = new FormData(vm.form);
          //vm.$http.post(vm.referral_form_url,formData).then(res=>{
          let data = {'email':vm.selected_referral, 'text': vm.referral_text};
          vm.$http.post(vm.referral_form_url, JSON.stringify(data)).then(res=>{

          },err=>{
          });
        },



        refreshFromResponse:function(response){
            let vm = this;
            vm.proposal = helpers.copyObject(response.body);
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            if (vm.proposal && !vm.contacts_table_initialised){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.proposal.applicant.id+'/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        proposedDecline: function(){
            this.$refs.proposed_decline.isModalOpen = true;
        },
        ammendmentRequest: function(){
            this.$refs.ammendment_request.isModalOpen = true;
        },
        save: function(e) {
          let vm = this;
          let formData = new FormData(vm.form);
          vm.$http.post(vm.proposal_form_url,formData).then(res=>{
              swal(
                'Saved',
                'Your application has been saved',
                'success'
              )
          },err=>{
          });
        },
        assignTo: function(){
            let vm = this;
            if ( vm.proposal.assigned_officer != 'null'){
                let data = {'user_id': vm.proposal.assigned_officer};
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.proposal.id+'/assign_to')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    console.log(response);
                    vm.proposal = response.body;
                }, (error) => {
                    console.log(error);
                });
            }
            else{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.proposal.id+'/unassign')))
                .then((response) => {
                    console.log(response);
                    vm.proposal = response.body;
                }, (error) => {
                    console.log(error);
                });
            }
        },
        fetchProposalGroupMembers: function(){
            let vm = this;
            vm.loading.push('Loading Application Group Members');
            vm.$http.get(api_endpoints.organisation_access_group_members).then((response) => {
                vm.members = response.body
                vm.loading.splice('Loading Application Group Members',1);
            },(error) => {
                console.log(error);
                vm.loading.splice('Loading Application Group Members',1);
            })
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
        fetchReferralRecipientGroups: function(){
            let vm = this;
            vm.loading.push('Loading Referral Recipient Groups');
            vm.$http.get(api_endpoints.referral_recipient_groups).then((response) => {
                vm.referral_recipient_groups = response.body
                vm.loading.splice('Loading Referral Recipient Groups',1);
            },(error) => {
                console.log(error);
                vm.loading.splice('Loading Referral Recipient Groups',1);
            })
        },


        initialiseSelects: function(){
            let vm = this;
            if (!vm.initialisedSelects){
                $(vm.$refs.referral_recipient_groups).select2({
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
                    vm.selected_referral = selected.val();
               });
                // Assigned officer select
                $(vm.$refs.assigned_officer).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Officer"
                }).
                on("select2:select",function (e) {
                   var selected = $(e.currentTarget);
                   vm.$emit('input',selected[0])
               }).
               on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.$emit('input',selected[0])
               });
                vm.initialisedSelects = true;
            }
        },
        sendReferral: function(){
            let vm = this;
            
            vm.sendingReferral = true;
            let data = {'email_group':vm.selected_referral, 'text': vm.referral_text};
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assesor_send_referral')),JSON.stringify(data),{
                emulateJSON:true
                }).then((response) => {
                vm.sendingReferral = false;
                vm.referral = response.body;
                // vm.referral.proposal.applicant.address = vm.referral.proposal.applicant.address != null ? vm.referral.proposal.applicant.address : {};
                swal(
                    'Referral Sent',
                    //'The referral has been sent to '+vm.department_users.find(d => d.email == vm.selected_referral).name,
                    // 'The referral has been sent to '+vm.referral_recipient_groups.find(d => d.email == vm.selected_referral).name,
                    'The referral has been sent to '+vm.selected_referral,
                    'success'
                )
                $(vm.$refs.referral_recipient_groups).val(null).trigger("change");
                vm.selected_referral = '';
                vm.referral_text = '';
             }, (error) => {
                console.log(error);
                swal(
                    'Referral Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                vm.sendingReferral = false;
                vm.selected_referral = '';
                vm.referral_text = '';
                });
            //let formData = new FormData(vm.form); //save data before completing referral
            // vm.$http.post(vm.proposal_form_url,formData).then(res=>{
                
            //     let data = {'email_group':vm.selected_referral, 'text': vm.referral_text};
            //     vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assesor_send_referral')),JSON.stringify(data),{
            //     emulateJSON:true
            //     }).then((response) => {
            //     vm.sendingReferral = false;
            //     vm.referral = response.body;
            //     vm.referral.proposal.applicant.address = vm.referral.proposal.applicant.address != null ? vm.referral.proposal.applicant.address : {};
            //     swal(
            //         'Referral Sent',
            //         //'The referral has been sent to '+vm.department_users.find(d => d.email == vm.selected_referral).name,
            //         'The referral has been sent to '+vm.referral_recipient_groups.find(d => d.email == vm.selected_referral).name,
            //         'success'
            //     )
            //     $(vm.$refs.referral_recipient_groups).val(null).trigger("change");
            //     vm.selected_referral = '';
            //     vm.referral_text = '';
            //  }, (error) => {
            //     console.log(error);
            //     swal(
            //         'Referral Error',
            //         helpers.apiVueResourceError(error),
            //         'error'
            //     )
            //     vm.sendingReferral = false;
            //     vm.selected_referral = '';
            //     vm.referral_text = '';
            //     });
            
             
            //  },err=>{
            //  });

        },
        remindReferral:function(r){
            let vm = this;
            
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind')).then(response => {
                // vm.original_proposal = helpers.copyObject(response.body);
                // vm.proposal = response.body;
                // vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.fetchReferral(vm.referral.id);
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
                // vm.original_proposal = helpers.copyObject(response.body);
                // vm.proposal = response.body;
                // vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.fetchReferral(vm.referral.id);
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
                // vm.original_proposal = helpers.copyObject(response.body);
                // vm.proposal = response.body;
                // vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.fetchReferral(vm.referral.id);
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
        fetchreferrallist: function(referral_id){
            let vm = this;

            Vue.http.get(helpers.add_endpoint_json(api_endpoints.referrals,referral_id+'/referral_list')).then(response => {
                vm.referral_sent_list = response.body;     
            },
            err => {
              console.log(err);
            });
        },
        fetchReferral: function(){
            let vm = this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.referrals,vm.referral.id)).then(res => {
              
                vm.referral = res.body;
                vm.referral.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                //vm.fetchreferrallist(vm.referral.id);
              
            },
            err => {
              console.log(err);
            });
        },
        completeReferral:function(){
            let vm = this;
            let data = {'referral_comment': vm.referral_comment};
            
            swal({
                title: "Complete Referral",
                text: "Are you sure you want to complete this referral?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Submit'
            }).then(() => { 
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,vm.$route.params.referral_id+'/complete'),JSON.stringify(data),{
                emulateJSON:true
                }).then(res => {
                    vm.referral = res.body;
                },
                error => {
                    swal(
                        'Referral Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
                // let formData = new FormData(vm.form);
                // vm.$http.post(vm.proposal_form_url,formData).then(res=>{
                    
                //     vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,vm.$route.params.referral_id+'/complete'),JSON.stringify(data),{
                // emulateJSON:true
                // }).then(res => {
                //     vm.referral = res.body;
                //     vm.referral.proposal.applicant.address = vm.referral.proposal.applicant.address != null ? vm.referral.proposal.applicant.address : {};
                // },
                // error => {
                //     swal(
                //         'Referral Error',
                //         helpers.apiVueResourceError(error),
                //         'error'
                //     )
                // });
                
                //  },err=>{
                //  });

               /* vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,vm.$route.params.referral_id+'/complete')).then(res => {
                    vm.referral = res.body;
                    vm.referral.proposal.applicant.address = vm.referral.proposal.applicant.address != null ? vm.referral.proposal.applicant.address : {};
                },
                error => {
                    swal(
                        'Referral Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                }); */


            },(error) => {
            });
        }
    },
    mounted: function() {
        let vm = this;
        vm.fetchProposalGroupMembers();
        vm.fetchDeparmentUsers();
        vm.fetchReferralRecipientGroups();
        //vm.fetchreferrallist()
        
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
            vm.form = document.forms.new_proposal;
        });
    },
    beforeRouteEnter: function(to, from, next) {
          //Vue.http.get(`/api/proposal/${to.params.proposal_id}/referral_proposal.json`).then(res => {
          Vue.http.get(helpers.add_endpoint_json(api_endpoints.referrals,to.params.referral_id)).then(res => {
              next(vm => {
                vm.referral = res.body;
                vm.referral.proposal.org_applicant.address = vm.proposal.org_applicant.address != null ? vm.proposal.org_applicant.address : {};
                //vm.fetchreferrallist(vm.referral.id);
              });
            },
            err => {
              console.log(err);
            });
    },
    beforeRouteUpdate: function(to, from, next) {
          Vue.http.get(`/api/proposal/${to.params.proposal_id}/referall_proposal.json`).then(res => {
              next(vm => {
                vm.referral = res.body;
                vm.referral.proposal.applicant.address = vm.referral.proposal.applicant.address != null ? vm.referral.proposal.applicant.address : {};
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
