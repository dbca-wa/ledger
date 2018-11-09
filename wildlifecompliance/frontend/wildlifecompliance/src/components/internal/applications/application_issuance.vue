<template id="application_issuance">

                <div class="col-md-12">
                    <div class="row" v-for="(item,index) in licence.activity_type">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Issue {{item.name}}
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
                                                    <input type="radio"  id="issue" name="licence_category" v-model="licence.activity_type[index].final_status"  value="Issue" > Issue
                                                </div>
                                                <div class="col-sm-3">
                                                    <input type="radio"  id="decline" name="licence_category" v-model="licence.activity_type[index].final_status"  value="Decline" > Decline
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left">Proposed Start Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="start_date" style="width: 70%;">
                                                        <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="licence.activity_type[index].start_date">
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>

                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Proposed Expiry Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="end_date" style="width: 70%;">
                                                        <input type="text" class="form-control" name="end_date" placeholder="DD/MM/YYYY" v-model="licence.activity_type[index].end_date">
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left">Fee</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="fee" style="width: 70%;">
                                                        <input type="text" class="form-control" name="fee" v-model="licence.activity_type[index].fee">
                                                        
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left">Reduced Fee</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="reduced_fee" style="width: 70%;">
                                                        <input type="text" class="form-control" name="reduced_fee" v-model="licence.activity_type[index].reduced_fee">
                                                        
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
                                        <button v-if="licence.id_check && licence.character_check" class="btn btn-primary pull-right" @click.prevent="ok()">Issue/Decline</button>
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
        licence_activity_type_tab:Number
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "application-issuance-"+vm._uid,
            proposed_licence:{},
            licence:{
                activity_type:[],
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
        hasAssessorMode(){
            // reload the table
        }
    },
    
    computed:{
        hasAssessorMode(){
            return this.application.assessor_mode.has_assessor_mode;
        },
        isIdCheckAccepted: function(){
            console.log(this.application.id_check_status)
            return this.application.id_check_status == 'Accepted';
        },
        isIdNotChecked: function(){
            console.log(this.application.id_check_status)
            return this.application.id_check_status == 'Not Checked';
        },
        isCharacterCheckAccepted: function(){
            console.log(this.application.id_check_status)
            return this.application.character_check_status == 'Accepted';
        },
        isCharacterNotChecked: function(){
            console.log(this.application.id_check_status)
            return this.application.character_check_status == 'Not Checked';
        },
    },
    methods:{
        ok:function () {
            let vm = this;
            let licence = JSON.parse(JSON.stringify(vm.licence));
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/final_decision'),JSON.stringify(licence),{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                             'Issue activity type',
                             'The activity type is successfully issued',
                             'success'
                        );
                        vm.close();
                        vm.$parent.refreshFromResponse(response)
                        // vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
        },
        initialiseLicenceDetails(){
            let vm=this;
            var final_status=null
            console.log('from fetch licence')
            console.log(vm.application.id_check_status)
            for(var i=0, len=vm.proposed_licence.length; i<len; i++){
                if (vm.proposed_licence[i].proposed_action =='Propose Issue'){
                    final_status="Issue"
                }
                if (vm.proposed_licence[i].proposed_action =='Propose Decline'){
                    final_status="Decline"
                }
                vm.licence.activity_type.push({
                                        id:         vm.proposed_licence[i].licence_activity_type.id,
                                        name:       vm.proposed_licence[i].licence_activity_type.name,
                                        start_date: vm.proposed_licence[i].proposed_start_date,
                                        end_date: vm.proposed_licence[i].proposed_end_date,
                                        final_status:final_status
                                    })
            }
            if(vm.application.id_check_status == 'Accepted'){
                vm.licence.id_check=true
            }
            if(vm.application.id_check_status == 'Not Checked'){
                vm.licence.id_check=false
            }
            if(vm.application.character_check_status == 'Accepted'){
                vm.licence.character_check=true
            }
            if(vm.application.character_check_status == 'Not Checked'){
                vm.licence.character_check=false
            }
        },
        
        fetchProposeIssue(){
            let vm = this;
            
           vm.$http.get(helpers.add_endpoint_join(api_endpoints.applications,(vm.application.id+'/get_proposed_decisions/')))
            .then((response) => {
                vm.proposed_licence = response.body;
                // console.log(vm.proposed_licence)
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
            let vm = this;
            // Initialise Date Picker
            // console.log('printing end date refs')
            // console.log(vm.$refs)
            // console.log(vm.$refs.end_date)
            
            //     console.log('inside if application issue')
            //     for (var i=0; i < vm.$refs.end_date.length; i++) {
            //     $(vm.$refs.end_date[i]).datetimepicker(vm.datepickerOptions);
            //     $(vm.$refs.end_date[i]).on('dp.change', function(e){
            //         if ($(vm.$refs.end_date[i]).data('DateTimePicker').date()) {
            //             vm.licence.activity_type[i].expiry_date=  e.date.format('DD/MM/YYYY');
            //         }
                    
            //      });
            // }
        
            // $(vm.$refs.start_date).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.start_date).on('dp.change', function(e){
            //     if ($(vm.$refs.start_date).data('DateTimePicker').date()) {
            //         vm.propose_issue.start_date =  e.date.format('DD/MM/YYYY');
            //     }
            //     else if ($(vm.$refs.start_date).data('date') === "") {
            //         vm.propose_issue.start_date = "";
            //     }
            //  });
            
        },
    },
    mounted: function(){
        let vm = this;
        this.fetchProposeIssue();

        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    
}
</script>
<style scoped>
</style>