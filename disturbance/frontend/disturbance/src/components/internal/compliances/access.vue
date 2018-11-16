<template>
<div class="container" id="internalCompliance">
    <div class="row">
        <h3>Compliance with Requirements {{ compliance.reference }}</h3>
        <div class="col-md-3">
        <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ compliance.submitter}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ compliance.lodgement_date | formatDate}}
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
                                {{ compliance.processing_status }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="canViewonly || !check_assessor()" v-if="!isLoading" class="form-control" v-model="compliance.assigned_to">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in compliance.allowed_assessors" :value="member.id">{{member.first_name}} {{member.last_name}}</option>
                                    </select>
                                    <a v-if="!canViewonly && check_assessor()" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s" v-if="!canViewonly && check_assessor()">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary" @click.prevent="acceptCompliance()">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" @click.prevent="amendmentRequest()">Request Amendment</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3>Compliance with Requirements</h3> 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="compliance_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Requirement</label>
                                        <div class="col-sm-6">
                                            {{compliance.requirement}}
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Details</label>
                                        <div class="col-sm-6">
                                            <textarea disabled class="form-control" name="details" placeholder="" v-model="compliance.text"></textarea>
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Documents</label>
                                        <div class="col-sm-6">
                                            <div class="row" v-for="d in compliance.documents">
                                                    <a :href="d[1]" target="_blank" class="control-label pull-left">{{d[0]}}</a>
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
    </div>
    <ComplianceAmendmentRequest ref="amendment_request" :compliance_id="compliance.id"></ComplianceAmendmentRequest>
</div>
</template>
<script>
import $ from 'jquery'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ComplianceAmendmentRequest from './compliance_amendment_request.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'complianceAccess',
  data() {
    let vm = this;
    return {
        loading: [],
        profile:{},
        compliance: {
            requester: {}
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/add_comms_log'),
      
    }
  },
  watch: {},
  filters: {
    formatDate: function(data){
        return data ? moment(data).format('DD/MM/YYYY'): '';    }
  },
  beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id)).then((response) => {
        next(vm => {
            vm.compliance = response.body
            vm.members = vm.compliance.allowed_assessors
        })
    },(error) => {
        console.log(error);
    })
  },
  components: {
    datatable,
    CommsLogs,
    ComplianceAmendmentRequest,
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    canViewonly: function(){
        return this.compliance.processing_status == 'Due' || this.compliance.processing_status == 'Future' || this.compliance.processing_status == 'Approved';
    },
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
  
    assignMyself: function(){
        let vm = this;
        vm.$http.get(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_request_user')))
        .then((response) => {            
            vm.compliance = response.body;
        }, (error) => {
            console.log(error);
        });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.compliance.assigned_to != 'null'){
            let data = {'user_id': vm.compliance.assigned_to};
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_to')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {                
                vm.compliance = response.body;
            }, (error) => {
                console.log(error);
            });
            
        }
        else{
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/unassign')))
            .then((response) => {
                console.log(response);
                vm.compliance = response.body;
            }, (error) => {
                console.log(error);
            });
        }
    },
    acceptCompliance: function() {
        let vm = this;
        swal({
            title: "Accept Compliance with requirements",
            text: "Are you sure you want to accept this compliance with requirements?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/accept')))
            .then((response) => {
                console.log(response);
                vm.compliance = response.body;
            }, (error) => {
                console.log(error);
            });
        },(error) => {

        });

    },
    amendmentRequest: function(){   
            this.$refs.amendment_request.amendment.compliance = this.compliance.id;                     
            this.$refs.amendment_request.isModalOpen = true;
    },
    fetchProfile: function(){
        let vm = this;
        Vue.http.get(api_endpoints.profile).then((response) => {
            vm.profile = response.body
                              
         },(error) => {
            console.log(error);
                
        })
        },

    check_assessor: function(){
        let vm = this;
        //vm.members = vm.compliance.allowed_assessors
        
        var assessor = vm.members.filter(function(elem){
                    return(elem.id==vm.profile.id);
                });
                if (assessor.length > 0)
                    return true;
                else
                    return false;
     },
  },
  mounted: function () {
    let vm = this;
    
    this.fetchProfile();
    
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
</style>
