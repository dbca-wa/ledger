<template id="application_issuance">
                <div class="col-md-12">
                    <div class="row" v-for="(item,index) in visibleLicenceActivities" v-bind:key="`issue_activity_${index}`">
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
                                                    <input type="radio"  id="issue" name="licence_category" v-model="licence.activity[index].final_status"  value="issued" > Issue
                                                </div>
                                                <div class="col-sm-3">
                                                    <input type="radio"  id="decline" name="licence_category" v-model="licence.activity[index].final_status"  value="declined" > Decline
                                                </div>
                                            </div>
                                            <div class="row" v-if="licence.activity[index].final_status == 'issued'">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left">Proposed Start Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="start_date" style="width: 70%;">
                                                        <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="licence.activity[index].start_date">
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>

                                            </div>
                                            <div class="row" v-if="licence.activity[index].final_status == 'issued'">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Proposed Expiry Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="end_date" style="width: 70%;">
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
                    </div>
                    <div class="row">
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
                                            <input type="text" class="form-control" name="details">
                                            
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="details">CC Email</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cc_email" style="width: 70%;">
                                            <input type="text" class="form-control" name="cc_email">
                                            
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


                    <div class="row">
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
                                            <button v-if="isIdCheckAccepted" disabled class="btn btn-light">Accepted</button>
                                            <label v-if="isIdNotChecked">Has not been accepted. Override to Issue: </label><input v-if="isIdNotChecked" type="checkbox" v-model="licence.id_check" >
                                            
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="details">Character Check</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cc_email" style="width: 70%;">
                                            <button v-if="isCharacterCheckAccepted" disabled class="btn btn-light">Accepted</button>
                                            <label v-if="isCharacterNotChecked">Has not been accepted. Override to Issue: </label><input v-if="isCharacterNotChecked" type="checkbox" v-model="licence.character_check" >
                                            
                                            
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
            datepickerInitialised: false,
            licence:{
                activity:[],
                id_check:false,
                character_check:false,
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
        canIssueOrDecline: function() {
            return this.licence.id_check && this.licence.character_check && this.visibleLicenceActivities.length;
        },
        visibleLicenceActivities: function() {
            const finalisingActivities = this.application.licence_type_data.activity.filter(
                activity => ['with_officer_finalisation'].includes(activity.processing_status.id)
            ).map(activity => activity.id);
            return this.licence.activity.filter(
                activity => finalisingActivities.includes(activity.id) && this.userHasRole('issuing_officer', activity.id)
            );
        },
        isIdCheckAccepted: function(){
            return this.application.id_check_status.id == 'accepted';
        },
        isIdNotChecked: function(){
            return this.application.id_check_status.id == 'not_checked';
        },
        isCharacterCheckAccepted: function(){
            return this.application.character_check_status.id == 'accepted';
        },
        isCharacterNotChecked: function(){
            return this.application.character_check_status.id == 'not_checked';
        },
    },
    methods:{
        ok: function () {
            let vm = this;
            let licence = JSON.parse(JSON.stringify(vm.licence));
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/final_decision'),JSON.stringify(licence),{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                             'Issue activity',
                             'The activity is successfully issued',
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
        },
        initialiseLicenceDetails() {
            let vm=this;
            var final_status=null
            for(var i=0, len=vm.proposed_licence.length; i<len; i++){
                if (vm.proposed_licence[i].proposed_action.id =='propose_issue'){
                    final_status="issued"
                }
                if (vm.proposed_licence[i].proposed_action.id =='propose_decline'){
                    final_status="declined"
                }
                const processing_status = vm.proposed_licence[i].processing_status;
                if(!['with_officer_finalisation'].includes(processing_status)) {
                    continue;
                }
                vm.licence.activity.push({
                                        id:         vm.proposed_licence[i].licence_activity.id,
                                        name:       vm.proposed_licence[i].licence_activity.name,
                                        start_date: vm.proposed_licence[i].proposed_start_date,
                                        end_date: vm.proposed_licence[i].proposed_end_date,
                                        final_status:final_status
                                    })
            }
            if(vm.application.id_check_status.id == 'accepted'){
                vm.licence.id_check=true;
            }
            if(vm.application.id_check_status.id == 'not_checked'){
                vm.licence.id_check=false;
            }
            if(vm.application.character_check_status.id == 'accepted'){
                vm.licence.character_check=true;
            }
            if(vm.application.character_check_status.id == 'not_checked'){
                vm.licence.character_check=false;
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
            if(this.datepickerInitialised || this.$refs === undefined || this.$refs.end_date === undefined) {
                return;
            }

            for (let i=0; i < this.$refs.end_date.length; i++) {
                const start_date = this.$refs.start_date[i];
                const end_date = this.$refs.end_date[i];

                const proposedStartDate = new Date(this.licence.activity[i].start_date);
                const proposedEndDate = new Date(this.licence.activity[i].end_date);

                $(end_date).datetimepicker(this.datepickerOptions);
                $(end_date).data('DateTimePicker').date(proposedEndDate);
                $(end_date).off('dp.change').on('dp.change', (e) => {
                    const selected_end_date = $(end_date).data('DateTimePicker').date().format('YYYY-MM-DD');
                    if (selected_end_date && selected_end_date != this.licence.activity[i].end_date) {
                        this.licence.activity[i].end_date = selected_end_date;
                    }
                });

                $(start_date).datetimepicker(this.datepickerOptions);
                $(start_date).data('DateTimePicker').date(proposedStartDate);
                $(start_date).off('dp.change').on('dp.change', (e) => {
                    const selected_start_date = $(start_date).data('DateTimePicker').date().format('YYYY-MM-DD');
                    if (selected_start_date && selected_start_date != this.licence.activity[i].start_date) {
                        this.licence.activity[i].start_date = selected_start_date;
                    }
                });
            }
            this.datepickerInitialised = true;
        }
    },
    mounted: function(){
        let vm = this;
        this.fetchProposeIssue();

        this.$nextTick(() => {
            vm.eventListeners();
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
</style>