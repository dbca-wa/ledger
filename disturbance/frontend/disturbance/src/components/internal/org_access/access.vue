<template>
<div class="container" id="internalOrgAccess">
    <div class="row">
        <h3>Organisation Access Request {{ access.id }}</h3>
        <div class="col-md-3">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Logs
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Communications</strong><br/>
                                <a @click.prevent="" class="actionBtn">Show</a>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Actions</strong><br/>
                                <a tabindex="2" ref="showActionBtn" class="actionBtn">Show</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ access.requester.full_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ access.lodgement_date | formatDate}}
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
                                {{ access.status }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="isFinalised" v-if="!isLoading" class="form-control" v-model="access.assigned_officer">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in members" :value="member.id">{{member.name}}</option>
                                    </select>
                                    <a v-if="!isFinalised" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary" v-if="!isFinalised" @click.prevent="acceptRequest()">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" v-if="!isFinalised" @click.prevent="">Decline</button>
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
                        <h3>Organisation Access Request</h3> 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="access_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="access.name">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="access.abn">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Letter</label>
                                        <div class="col-sm-6">
                                            <a target="_blank" :href="access.identification"><i class="fa fa-file-pdf-o"></i>&nbsp;Letter.PDF</a>
                                        </div>
                                    </div>   
                                    <div class="form-group" style="margin-top:50px;">
                                        <label for="" class="col-sm-3 control-label">Phone</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="phone" placeholder="" v-model="access.requester.phone_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="mobile" placeholder="" v-model="access.requester.mobile_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Email</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="email" placeholder="" v-model="access.requester.email">
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
</div>
</template>
<script>
import $ from 'jquery'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'OrganisationAccess',
  data() {
    let vm = this;
    return {
        loading: [],
        access: {
            requester: {}
        },
        members: [],
        // Filters
        dtOptions:{
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive: true,
            deferRender: true, 
            autowidth: true,
            order: [[2, 'desc']],
            dom:
                "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-5'i><'col-sm-7'p>>",
            processing:true,
            ajax: {
                "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/action_log'),
                "dataSrc": '',
            },
            columns:[
                {
                    data:"who",
                },
                {
                    data:"what",
                },
                {
                    data:"when",
                    mRender:function(data,type,full){
                        return moment(data).format('DD/MM/YYYY HH:mm:ss')
                    }
                },
            ]
        },
        dtHeaders:["Who","What","When"],
        actionsTable : null
    }
  },
  watch: {},
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
    }
  },
  beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,to.params.access_id)).then((response) => {
        next(vm => {
            vm.access = response.body
        })
    },(error) => {
        console.log(error);
    })
  },
  components: {
    datatable
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    isFinalised: function(){
        return this.access.status == 'With Assesor' || this.access.status == 'Approved';
    }
  },
  methods: {
    fetchAccessGroupMembers: function(){
        let vm = this;
        vm.loading.push('Loading Access Group Members');
        vm.$http.get(api_endpoints.organisation_access_group_members).then((response) => {
            vm.members = response.body
            vm.loading.splice('Loading Access Group Members',1);
        },(error) => {
            console.log(error);
            vm.loading.splice('Loading Access Group Members',1);
        })

    },
    assignMyself: function(){
        let vm = this;
        vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/assign_request_user')))
        .then((response) => {
            console.log(response);
            vm.access = response.body;
        }, (error) => {
            console.log(error);
        });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.access.assigned_officer != 'null'){
            let data = {'user_id': vm.access.assigned_officer};
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/assign_to')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.access = response.body;
            }, (error) => {
                console.log(error);
            });
            console.log('there');
        }
        else{
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/unassign')))
            .then((response) => {
                console.log(response);
                vm.access = response.body;
            }, (error) => {
                console.log(error);
            });
        }
    },
    acceptRequest: function() {
        let vm = this;
        swal({
            title: "Accept Organisation Request",
            text: "Are you sure you want to accept this organisation request?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/accept')))
            .then((response) => {
                console.log(response);
                vm.access = response.body;
            }, (error) => {
                console.log(error);
            });
        },(error) => {

        });

    },
    initialisePopovers: function(){
        let vm = this;
        let actionLogId = 'actions-log-table'+vm._uid;
        $(vm.$refs.showActionBtn).popover({
            content: function() {
                return ` 
                <table id="${actionLogId}" class="hover table table-striped table-bordered dt-responsive nowrap" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>Who</th>
                            <th>When</th>
                            <th>What</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>`
            },
            html: true,
            title: 'Action Log',
            container: 'body',
            placement: 'right',
            trigger: "click",
        }).on('inserted.bs.popover', function () {
            vm.actionsTable = $('#'+actionLogId).DataTable(vm.dtOptions);
        });
    }
  },
  mounted: function () {
    let vm = this;
    this.fetchAccessGroupMembers();
    vm.initialisePopovers();
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
