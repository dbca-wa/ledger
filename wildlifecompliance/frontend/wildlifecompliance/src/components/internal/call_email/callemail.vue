<template>
<div class="container" id="internalCallEmail">
    <div class="row">
        <h3>Licence {{ licence.id }}</h3>
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
                                {{ licence.requester.full_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ licence.lodgement_date | formatDate}}
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
                                {{ licence.status.name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="isFinalised" v-if="!isLoading" class="form-control" v-model="licence.assigned_officer">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in members" :value="member.id">{{member.name}}</option>
                                    </select>
                                    <a v-if="!isFinalised" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary" @click.prevent="acceptRequest()">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" @click.prevent="">Decline</button>
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
                        <h3>Organisation licence Request</h3> 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="licence_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="licence.name">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="licence.abn">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Letter</label>
                                        <div class="col-sm-6">
                                            <a target="_blank" :href="licence.identification"><i class="fa fa-file-pdf-o"></i>&nbsp;Letter.PDF</a>
                                        </div>
                                    </div>   
                                    <div class="form-group" style="margin-top:50px;">
                                        <label for="" class="col-sm-3 control-label">Phone</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="phone" placeholder="" v-model="licence.requester.phone_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="mobile" placeholder="" v-model="licence.requester.mobile_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Email</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="email" placeholder="" v-model="licence.requester.email">
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
import CommsLogs from '@common-utils/comms_logs.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'CallEmail',
  data() {
    let vm = this;
    return {
        loading: [],
        call_email: {
            requester: {}
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.licence_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.licence_id+'/comms_log'),
        actionDtOptions:{
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
                "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.licence_id+'/action_log'),
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
                        return moment(data).format(vm.DATE_TIME_FORMAT)
                    }
                },
            ]
        },
        dtHeaders:["Who","What","When"],
        actionsTable : null,
        commsDtOptions:{
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive: true,
            deferRender: true, 
            autowidth: true,
            order: [[0, 'desc']],
            processing:true,
            ajax: {
                "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.licence_id+'/comms_log'),
                "dataSrc": '',
            },
            columns:[
                {
                    title: 'Date',
                    data: 'created',
                    render: function (date) {
                        return moment(date).format(vm.DATE_TIME_FORMAT);
                    }
                },
                {
                    title: 'Type',
                    data: 'type'
                },
                {
                    title: 'Reference',
                    data: 'reference'
                },
                {
                    title: 'To',
                    data: 'to',
                    render: vm.commaToNewline
                },
                {
                    title: 'CC',
                    data: 'cc',
                    render: vm.commaToNewline
                },
                {
                    title: 'From',
                    data: 'fromm',
                    render: vm.commaToNewline
                },
                {
                    title: 'Subject/Desc.',
                    data: 'subject'
                },
                {
                    title: 'Text',
                    data: 'text',
                    'render': function (value) {
                        var ellipsis = '...',
                            truncated = _.truncate(value, {
                                length: 100,
                                omission: ellipsis,
                                separator: ' '
                            }),
                            result = '<span>' + truncated + '</span>',
                            popTemplate = _.template('<a href="#" ' +
                                'role="button" ' +
                                'data-toggle="popover" ' +
                                'data-trigger="click" ' +
                                'data-placement="top auto"' +
                                'data-html="true" ' +
                                'data-content="<%= text %>" ' +
                                '>more</a>');
                        if (_.endsWith(truncated, ellipsis)) {
                            result += popTemplate({
                                text: value
                            });
                        }

                        return result;
                    },
                    'createdCell': function (cell) {
                        //TODO why this is not working?
                        // the call to popover is done in the 'draw' event
                        $(cell).popover();
                    }
                },
                {
                    title: 'Documents',
                    data: 'documents',
                    'render': function (values) {
                        var result = '';
                        _.forEach(values, function (value) {
                            // We expect an array [docName, url]
                            // if it's a string it is the url
                            var docName = '',
                                url = '';
                            if (_.isArray(value) && value.length > 1){
                                docName = value[0];
                                url = value[1];
                            }
                            if (typeof s === 'string'){
                                url = value;
                                // display the first  chars of the filename
                                docName = _.last(value.split('/'));
                                docName = _.truncate(docName, {
                                    length: 18,
                                    omission: '...',
                                    separator: ' '
                                });
                            }
                            result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                        });
                        return result;
                    }
                }
            ]
        },
        commsTable : null,
    }
  },
  watch: {},
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
    }
  },
  beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,to.params.licence_id)).then((response) => {
        next(vm => {
            vm.licence = response.body
        })
    },(error) => {
        console.log(error);
    })
  },
  components: {
    datatable,
    CommsLogs
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    isFinalised: function(){
        return this.licence.status.id == 'with_assesor' || this.licence.status.id == 'approved';
    }
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    fetchlicenceGroupMembers: function(){
        let vm = this;
        vm.loading.push('Loading licence Group Members');
        vm.$http.get(api_endpoints.organisation_licence_group_members).then((response) => {
            vm.members = response.body
            vm.loading.splice('Loading licence Group Members',1);
        },(error) => {
            console.log(error);
            vm.loading.splice('Loading licence Group Members',1);
        })

    },
    assignMyself: function(){
        let vm = this;
        vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.licence.id+'/assign_request_user')))
        .then((response) => {
            console.log(response);
            vm.licence = response.body;
        }, (error) => {
            console.log(error);
        });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.licence.assigned_officer != 'null'){
            let data = {'user_id': vm.licence.assigned_officer};
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.licence.id+'/assign_to')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.licence = response.body;
            }, (error) => {
                console.log(error);
            });
            console.log('there');
        }
        else{
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.licence.id+'/unassign')))
            .then((response) => {
                console.log(response);
                vm.licence = response.body;
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
        }).then((result) => {
            if (result.value) {
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.licence.id+'/accept')))
                .then((response) => {
                    console.log(response);
                    vm.licence = response.body;
                }, (error) => {
                    console.log(error);
                });
            }
        },(error) => {

        });

    },
  },
  mounted: function () {
    let vm = this;
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
