<template id="application_issuance">

                <div class="col-md-12">
                    <div class="row" v-for="item in proposed_licence">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Issue {{item.licence_activity_type.name}}
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
                                                    
                                                    <label class="control-label pull-left"  for="Name">Proposed Start Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="start_date" style="width: 70%;">
                                                        <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY">{{item.proposed_start_date}}
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left"  for="Name">Proposed Expiry Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="due_date" style="width: 70%;">
                                                        <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" >{{item.proposed_end_date}}
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left"  for="Fee">Fee</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="fee" style="width: 70%;">
                                                        <input type="text" class="form-control" name="fee">
                                                        
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    
                                                    <label class="control-label pull-left"  for="Fee">Reduced Fee</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" ref="fee" style="width: 70%;">
                                                        <input type="text" class="form-control" name="fee">
                                                        
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
                                            
                                            
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="details">Character Check</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cc_email" style="width: 70%;">
                                            
                                            
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="details">Returns Check</label>
                                    </div>
                                    
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
    name: 'InternalApplicationConditions',
    props: {
        application: Object,
        licence_activity_type_tab:Number
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "application-conditions-"+vm._uid,
            proposed_licence:{},
            licence:{
                activity_type:{
                    id:null,
                    issue_date:'',
                    start_date:'',
                    expiry_date:'',
                    fee:'',
                    reduced_fee:''

                },
                
                standard: true,
                recurrence: false,
                recurrence_pattern: '1',
                current_application: vm.application.id,
                licence_activity_type:null}
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
        }
    },
    methods:{
        
        fetchProposeIssue(){
            let vm = this;
            
           vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/get_proposed_licence')))
            .then((response) => {
                vm.proposed_licence = response.body;
                console.log(vm.proposed_licence)
                
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
    },
    mounted: function(){
        let vm = this;
        this.fetchProposeIssue();
        vm.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>
<style scoped>
</style>