<template lang="html">
    <div v-if="application" class="container" id="internalReferral">
            <div class="row">
        <h3>Application: {{ application.id }}</h3>
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
                                {{ application.submitter }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ application.lodgement_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgment</th>
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
                                {{ application.processing_status }}
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Referrals</strong><br/>
                                <div class="form-group" v-if="!isFinalised">
                                    <select :disabled="isFinalised || application.can_user_edit" ref="department_users" class="form-control">
                                        <option value="null"></option>
                                        <option v-for="user in department_users" :value="user.email">{{user.name}}</option>
                                    </select>
                                    <template v-if='!sendingReferral'>
                                        <template v-if="selected_referral">
                                            <a v-if="!isFinalised && !application.can_user_edit && referral.sent_from == 1" @click.prevent="sendReferral()" class="actionBtn pull-right">Send</a>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <span v-if="!isFinalised && !application.can_user_edit && referral.sent_from == 1" class="text-primary pull-right">
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
                                    <tr v-for="r in application.latest_referrals">
                                        <td>
                                            <small><strong>{{r.referral}}</strong></small><br/>
                                            <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                        </td>
                                        <td><small><strong>{{r.processing_status}}</strong></small></td>
                                    </tr>
                                </table>
                                <MoreReferrals @refreshFromResponse="refreshFromResponse" :application="application" :canAction="false" :isFinalised="isFinalised"/>
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && referral.referral == application.current_assessor.id">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <strong>Action</strong><br/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="application.can_user_edit" @click.prevent="completeReferral">Complete Referral</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div v-show="false" class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Level of Licence</h3>
                            </div>
                            <div class="panel-body panel-collapse">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
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
                                            <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.applicant.name">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="application.applicant.abn">
                                        </div>
                                      </div>
                                  </form>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
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
                                            <input disabled type="text" class="form-control" name="street" placeholder="" v-model="application.applicant.address.line1">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="application.applicant.address.locality">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="country" placeholder="" v-model="application.applicant.address.state">
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="application.applicant.address.postcode">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <input disabled type="text" class="form-control" name="country" v-model="application.applicant.address.country"/>
                                        </div>
                                      </div>
                                   </form>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
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
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
                            <Application form_width="inherit" :withSectionsSelector="false" v-if="application" :application="application">
                                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                                <input type='hidden' name="application_id" :value="1" />
                                <div v-if="!application.can_user_edit" class="row" style="margin-bottom:20px;">
                                  <div class="col-lg-12 pull-right" v-if="!isFinalised">
                                    <button class="btn btn-primary pull-right" @click.prevent="save()">Save Changes</button>
                                  </div>
                                </div>
                            </Application>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
</template>
<script>
import Application from '../../form.vue'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import MoreReferrals from '@common-utils/more_referrals.vue'
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
            //"application": null,
            referral: null,
            "loading": [],
            selected_referral: '',
            sendingReferral: false,
            form: null,
            members: [],
            department_users : [],
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
            logs_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/comms_log'),
            panelClickersInitialised: false,
            referral: {}
        }
    },
    components: {
        Application,
        datatable,
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
        application: function(){
            return this.referral != null && this.referall != 'undefined' ? this.referral.application : null;
        },
        contactsURL: function(){
            return this.application!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.application.applicant.id+'/contacts') : '';
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
            return !(this.referral != null  && this.referral.processing_status == 'Awaiting'); 
        }
    },
    methods: {
        refreshFromResponse:function(response){
            let vm = this;
            vm.application = helpers.copyObject(response.body);
            vm.application.applicant.address = vm.application.applicant.address != null ? vm.application.applicant.address : {};
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            if (vm.application && !vm.contacts_table_initialised){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.application.applicant.id+'/contacts');
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
          vm.$http.post(vm.application_form_url,formData).then(res=>{
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
            if ( vm.application.assigned_officer != 'null'){
                let data = {'user_id': vm.application.assigned_officer};
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.application.id+'/assign_to')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    console.log(response);
                    vm.application = response.body;
                }, (error) => {
                    console.log(error);
                });
                console.log('there');
            }
            else{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.application.id+'/unassign')))
                .then((response) => {
                    console.log(response);
                    vm.application = response.body;
                }, (error) => {
                    console.log(error);
                });
            }
        },
        fetchApplicationGroupMembers: function(){
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

            let data = {'email':vm.selected_referral};
            vm.sendingReferral = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,(vm.referral.id+'/send_referral')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                vm.sendingReferral = false;
                vm.referral = response.body;
                vm.referral.application.applicant.address = vm.referral.application.applicant.address != null ? vm.referral.application.applicant.address : {};
                swal(
                    'Referral Sent',
                    'The referral has been sent to '+vm.department_users.find(d => d.email == vm.selected_referral).name,
                    'success'
                )
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
        completeReferral:function(){
            let vm = this;
            
            swal({
                title: "Complete Referral",
                text: "Are you sure you want to complete this referral?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Submit'
            }).then((result) => {
                if (result.value) {
                    vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,vm.$route.params.referral_id+'/complete')).then(res => {
                        vm.referral = res.body;
                        vm.referral.application.applicant.address = vm.referral.application.applicant.address != null ? vm.referral.application.applicant.address : {};
                    },
                    error => {
                        swal(
                            'Referral Error',
                            helpers.apiVueResourceError(error),
                            'error'
                        )
                    });
                }
            },(error) => {
            });
        }
    },
    mounted: function() {
        let vm = this;
        vm.fetchApplicationGroupMembers();
        vm.fetchDeparmentUsers();
        
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
        });
    },
    beforeRouteEnter: function(to, from, next) {
          //Vue.http.get(`/api/application/${to.params.application_id}/referral_application.json`).then(res => {
          Vue.http.get(helpers.add_endpoint_json(api_endpoints.referrals,to.params.referral_id)).then(res => {
              next(vm => {
                vm.referral = res.body;
                vm.referral.application.applicant.address = vm.application.applicant.address != null ? vm.application.applicant.address : {};
              });
            },
            err => {
              console.log(err);
            });
    },
    beforeRouteUpdate: function(to, from, next) {
          Vue.http.get(`/api/application/${to.params.application_id}/referall_application.json`).then(res => {
              next(vm => {
                vm.referral = res.body;
                vm.referral.application.applicant.address = vm.referral.application.applicant.address != null ? vm.referral.application.applicant.address : {};
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
