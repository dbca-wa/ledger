<template id="application_issuance">
                <div class="col-md-12">

                    <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs">
                        <li v-for="(activity, index) in visibleLicenceActivities" v-bind:key="`issue_activity_tab_${index}`">
                            <a data-toggle="tab" v-on:click="selectTab(activity)">{{activity.name}}</a>
                        </li>
                    </ul>
                    <div class="tab-content">
                        <div class="row" v-for="(item, index) in selectedActivity" v-bind:key="`issue_activity_content_${index}`">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Issue/Decline - {{item.name}}
                                        <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="col-sm-12">
                                            <div class="form-group">
                                                <div class="row">
                                                    <div class="col-sm-3">
                                                        <input type="radio"  id="issue" name="licence_category" v-model="getActivity(item.id).final_status"  value="issued" > Issue
                                                    </div>
                                                    <div class="col-sm-3">
                                                        <input type="radio"  id="decline" name="licence_category" v-model="getActivity(item.id).final_status"  value="declined" > Decline
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-sm-3">
                                                        <label class="control-label pull-left">Ready for finalisation?</label>
                                                    </div>
                                                    <div class="col-sm-9">
                                                        <input type="checkbox" class="confirmation-checkbox" v-model="getActivity(item.id).confirmed">
                                                    </div>
                                                </div>
                                                <div class="row" v-if="finalStatus(item.id) === 'issued' && canEditLicenceDates">
                                                    <div class="col-sm-3">
                                                        <label class="control-label pull-left">Proposed Start Date</label>
                                                    </div>
                                                    <div class="col-sm-9">
                                                        <div class="input-group date" ref="start_date" style="width: 70%;" :data-init="false" :data-activity="item.id">
                                                            <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY">
                                                            <span class="input-group-addon">
                                                                <span class="glyphicon glyphicon-calendar"></span>
                                                            </span>
                                                        </div>
                                                    </div>

                                                </div>
                                                <div class="row" v-if="finalStatus(item.id) === 'issued' && canEditLicenceDates">
                                                    <div class="col-sm-3">
                                                        <label class="control-label pull-left">Proposed Expiry Date</label>
                                                    </div>
                                                    <div class="col-sm-9">
                                                        <div class="input-group date" ref="end_date" style="width: 70%;" :data-activity="item.id">
                                                            <input type="text" class="form-control" name="end_date" placeholder="DD/MM/YYYY">
                                                            <span class="input-group-addon">
                                                                <span class="glyphicon glyphicon-calendar"></span>
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                    </form>
                                </div>
                            </div>
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Emailing
                                        <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            
                                            <label class="control-label pull-left"  for="details">Details</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <div class="input-group date" ref="details" style="width: 70%;">
                                                <input type="text" class="form-control" name="details" v-model="getActivity(item.id).reason">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="details">CC Email</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <div class="input-group date" ref="cc_email" style="width: 70%;">
                                                <input type="text" class="form-control" name="cc_email" v-model="getActivity(item.id).cc_email">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="details">Files to be attached to email</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="row" v-if="licence.activity.some(activity => activity.final_status === 'issued')">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Issue
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="details">ID Check</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="details" style="width: 70%;">
                                            <button v-if="isIdCheckAccepted" disabled class="btn btn-success">Accepted</button>
                                            <label v-if="isIdCheckAwaitingUpdate">Awaiting update. Override to Issue: &nbsp;</label>
                                            <label v-if="isIdNotChecked">Has not been accepted. Override to Issue: &nbsp;</label>
                                            <input v-if="isIdNotChecked || isIdCheckAwaitingUpdate" type="checkbox" v-model="licence.id_check" />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="details">Character Check</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cc_email" style="width: 70%;">
                                            <button v-if="isCharacterCheckAccepted" disabled class="btn btn-success">Accepted</button>
                                            <label v-if="isCharacterNotChecked">Has not been accepted. Override to Issue: &nbsp;</label>
                                            <input v-if="isCharacterNotChecked" type="checkbox" v-model="licence.character_check" />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="details">Return Check</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cc_email" style="width: 70%;">
                                            <button v-if="isReturnCheckAccepted" disabled class="btn btn-success">Accepted</button>
                                            <label v-if="isReturnCheckAwaitingReturns">Awaiting return. Override to Issue: &nbsp;</label>
                                            <label v-if="isReturnNotChecked">Has not been accepted. Override to Issue: &nbsp;</label>
                                            <input v-if="isReturnNotChecked || isReturnCheckAwaitingReturns" type="checkbox" v-model="licence.return_check" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom:50px;">
                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                            <div class="navbar-inner">
                                <div class="container">
                                    <p class="pull-right" style="margin-top:5px;">
                                        <button v-if="canIssueOrDecline" class="btn btn-primary pull-right" @click.prevent="ok()">Issue/Decline</button>
                                        <button v-else disabled class="btn btn-primary pull-right">Issue/Decline</button>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            
</template>
<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
import { mapGetters, mapActions } from 'vuex'

export default {
    name: 'InternalApplicationIssuance',
    props: {
        application: Object,
        licence_activity_tab:Number
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "application-issuance-"+vm._uid,
            proposed_licence:{},
            licence:{
                activity: [],
                id_check:false,
                character_check:false,
                return_check:false,
                current_application: vm.application.id,
                },
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                allowInputToggle:true
            },
        }
    },
    watch:{
    },
    computed:{
        ...mapGetters([
            'selected_activity_tab_id',
            'licenceActivities',
            'filterActivityList',
        ]),
        canIssueOrDecline: function() {
            return (this.allActivitiesDeclined || (
                this.licence.id_check && this.licence.character_check && this.licence.return_check)
            ) && this.visibleLicenceActivities.length;
        },
        selectedActivity: function() {
            return this.visibleLicenceActivities.filter(
                activity => activity.id == this.selected_activity_tab_id
            );
        },
        visibleLicenceActivities: function() {
            return this.filterActivityList({
                activity_list: this.licenceActivities([
                    'with_officer_finalisation',
                    'awaiting_licence_fee_payment'
                ], 'issuing_officer'),
                exclude_processing_statuses: ['discarded']
            });
        },
        isIdCheckAccepted: function(){
            return this.application.id_check_status.id == 'accepted';
        },
        isIdCheckAwaitingUpdate: function(){
            return this.application.id_check_status.id == 'awaiting_update';
        },
        isIdNotChecked: function(){
            return this.application.id_check_status.id == 'not_checked'
                || this.application.id_check_status.id == 'updated' ;
        },
        isCharacterCheckAccepted: function(){
            return this.application.character_check_status.id == 'accepted';
        },
        isCharacterNotChecked: function(){
            return this.application.character_check_status.id == 'not_checked';
        },
        isReturnCheckAccepted: function(){
            return this.application.return_check_status.id == 'accepted';
        },
        isReturnCheckAwaitingReturns: function(){
            return this.application.return_check_status.id == 'awaiting_returns';
        },
        isReturnNotChecked: function(){
            return this.application.return_check_status.id == 'not_checked'
                || this.application.return_check_status.id == 'updated' ;
        },
        finalStatus: function() {
            return (id) => {
                return this.getActivity(id).final_status;
            }
        },
        allActivitiesDeclined: function() {
            return this.licence && !this.licence.activity.filter(
                activity => activity.final_status !== 'declined'
            ).length;
        },
        canSubmit: function() {
            const missingConfirmations = this.licence.activity.filter(
                activity => !activity.confirmed
            ).length;
            return missingConfirmations === 0;
        },
        canEditLicenceDates: function() {
            return this.application.application_type && this.application.application_type.id !== 'amend_activity';
        },
    },
    methods:{
        ...mapActions([
            'setActivityTab'
        ]),
        selectTab: function(component) {
            this.setActivityTab({id: component.id, name: component.name});
        },
        ok: function () {
            let vm = this;

            if(!this.canSubmit) {
                return swal(
                    'Cannot issue/decline',
                    "One or more activity tabs hasn't been marked as ready for finalisation!",
                    'error'
                );
            }

            swal({
                title: "Issue/Decline Activities",
                text: "Payment for issued licences will be charged from the applicant's last used card.",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Finalise'
            }).then((result) => {
                if (result.value) {
                    let licence = JSON.parse(JSON.stringify(vm.licence));
                    licence.activity = this.licence.activity.map(activity => {
                        const date_formats = ["DD/MM/YYYY", "YYYY-MM-DD"];
                        return {
                            ...activity,
                            start_date: activity.start_date ?
                                moment(activity.start_date, date_formats).format('YYYY-MM-DD') : null,
                            end_date: activity.end_date ?
                                moment(activity.end_date, date_formats).format('YYYY-MM-DD') : null,
                        }
                    });
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/final_decision'),JSON.stringify(licence),{
                                emulateJSON:true,
                            }).then((response)=>{
                                swal(
                                    'Activities Finalised',
                                    'The selected activities have been successfully finalised!',
                                    'success'
                                );
                                vm.$parent.refreshFromResponse(response);
                            },(error)=>{
                                swal(
                                    'Application Error',
                                    helpers.apiVueResourceError(error),
                                    'error'
                                )
                            });
                }
            },(error) => {
            });
        },
        getActivity: function(id) {
            const activity = this.licence.activity.find(activity => activity.id == id);
            return activity ? activity : {};
        },
        initialiseLicenceDetails() {
            var final_status = null;
            for(let proposal of this.proposed_licence){
                if (proposal.proposed_action.id =='propose_issue'){
                    final_status="issued"
                }
                if (proposal.proposed_action.id =='propose_decline'){
                    final_status="declined"
                }
                const processing_status = proposal.processing_status;
                if(!['with_officer_finalisation', 'awaiting_licence_fee_payment'].includes(processing_status)) {
                    continue;
                }
                const activity_id = proposal.licence_activity.id;
                this.licence.activity.push({
                    id: activity_id,
                    name: proposal.licence_activity.name,
                    start_date: proposal.proposed_start_date,
                    end_date: proposal.proposed_end_date,
                    reason: proposal.reason,
                    cc_email: proposal.cc_email,
                    final_status: final_status,
                    confirmed: false,
                });
            }
            if(this.application.id_check_status.id == 'accepted'){
                this.licence.id_check = true;
            }
            if(this.application.id_check_status.id == 'not_checked'){
                this.licence.id_check = false;
            }
            if(this.application.character_check_status.id == 'accepted'){
                this.licence.character_check = true;
            }
            if(this.application.character_check_status.id == 'not_checked'){
                this.licence.character_check = false;
            }
            if(this.application.return_check_status.id == 'accepted'){
                this.licence.return_check=true;
            }
            if(this.application.return_check_status.id == 'not_checked'){
                this.licence.return_check=false;
            }
        },
        
        fetchProposeIssue(){
            let vm = this;
            
           vm.$http.get(helpers.add_endpoint_join(api_endpoints.applications,(vm.application.id+'/get_proposed_decisions/')))
            .then((response) => {
                vm.proposed_licence = response.body;
                this.initialiseLicenceDetails();
                
            }, (error) => {
               
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
       
        eventListeners(){
        },

        userHasRole: function(role, activity_id) {
            return this.application.user_roles.filter(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            ).length;
        },

        //Initialise Date Picker
        initDatePicker: function() {
            if(this.$refs === undefined || this.$refs.end_date === undefined) {
                return;
            }

            for (let i=0; i < this.$refs.end_date.length; i++) {
                const start_date = this.$refs.start_date[i];
                const end_date = this.$refs.end_date[i];
                const activity_id = end_date.dataset.activity;
                if(end_date.dataset.init) {
                    continue;
                }

                const activity = this.getActivity(activity_id);
                const proposedStartDate = new Date(activity.start_date);
                const proposedEndDate = new Date(activity.end_date);

                end_date.dataset.init = true;
                start_date.dataset.init = true;
                $(end_date).datetimepicker(this.datepickerOptions);
                $(end_date).data('DateTimePicker').date(proposedEndDate);
                $(end_date).off('dp.change').on('dp.change', (e) => {
                    const selected_end_date = $(end_date).data('DateTimePicker').date().format('DD/MM/YYYY');
                    if (selected_end_date && selected_end_date != activity.end_date) {
                        activity.end_date = selected_end_date;
                    }
                });

                $(start_date).datetimepicker(this.datepickerOptions);
                $(start_date).data('DateTimePicker').date(proposedStartDate);
                $(start_date).off('dp.change').on('dp.change', (e) => {
                    const selected_start_date = $(start_date).data('DateTimePicker').date().format('DD/MM/YYYY');
                    if (selected_start_date && selected_start_date != activity.start_date) {
                        activity.start_date = selected_start_date;
                    }
                });
            }
        }
    },
    mounted: function(){
        let vm = this;
        this.fetchProposeIssue();

        this.$nextTick(() => {
            vm.eventListeners();
            $('#tabs-section li:first-child a').click();
        });
    },
    updated: function() {
        this.$nextTick(() => {
            this.initDatePicker();
        });
    }
    
}
</script>
<style scoped>
    .confirmation-checkbox {
        margin-top: 10px;
    }
</style>
