<template>
    <div class="container-fluid" v-if="org" id="internalOrgInfo">
    <div class="row">
    <div class="col-md-10 col-md-offset-1">
        <div class="row">
            <h3>{{ org.name }} - {{org.abn}}</h3>
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
                                    <a ref="showCommsBtn" class="actionBtn">Show</a>
                                </div>
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Actions</strong><br/>
                                    <a tabindex="2" ref="showActionBtn" class="actionBtn">Show</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-1">
            </div>
            <div class="col-md-8">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    <li><a data-toggle="tab" :href="'#'+oTab">Other</a></li>
                </ul>
                <div class="tab-content">
                    <div :id="dTab" class="tab-pane fade in active">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                  <div class="panel-heading">
                                    <h3 class="panel-title">Organisation Details
                                        <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse in" :id="pdBody">
                                      <form class="form-horizontal" name="personal_form" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Name</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="first_name" placeholder="" v-model="org.name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >ABN</label>
                                            <div class="col-sm-6">
                                                <input type="text" disabled class="form-control" name="last_name" placeholder="" v-model="org.abn">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <div class="col-sm-12">
                                                <button v-if="!updatingDetails" class="pull-right btn btn-primary" @click.prevent="updateDetails()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                            </div>
                                          </div>
                                       </form>
                                  </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                  <div class="panel-heading">
                                    <h3 class="panel-title">Address Details
                                        <a class="panelClicker" :href="'#'+adBody" data-toggle="collapse" expanded="false"  data-parent="#userInfo" :aria-controls="adBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div v-if="loading.length == 0" class="panel-body collapse" :id="adBody">
                                      <form class="form-horizontal" action="index.html" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="street" placeholder="" v-model="org.address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="country" placeholder="" v-model="org.address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <select class="form-control" name="country" v-model="org.address.country">
                                                    <option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option>
                                                </select>
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <div class="col-sm-12">
                                                <button v-if="!updatingAddress" class="pull-right btn btn-primary" @click.prevent="updateAddress()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                            </div>
                                          </div>
                                       </form>
                                  </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                  <div class="panel-heading">
                                    <h3 class="panel-title">Contact Details
                                        <a class="panelClicker" :href="'#'+cdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="cdBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse" :id="cdBody">
                                        <form class="form-horizontal" action="index.html" method="post">
                                            <div class="col-sm-12">
                                                <button @click.prevent="addContact()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Contact</button>
                                            </div>
                                            <datatable ref="contacts_datatable" id="organisation_contacts_datatable" :dtOptions="contacts_options" :dtHeaders="contacts_headers"/>
                                        </form>
                                  </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                  <div class="panel-heading">
                                    <h3 class="panel-title">Linked Persons<small> - Manage the user accounts linked to the organisation</small>
                                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse" :id="oBody">
                                    <div class="row">
                                        <div class="col-sm-8">
                                            <div class="row">
                                                <div class="col-sm-12">
                                                    <h4>Persons linked to this organisation:</h4>
                                                </div>
                                                <div v-for="d in org.delegates">
                                                    <div class="col-sm-6">
                                                        <h4>{{d.name}}</h4>
                                                    </div>
                                                </div>
                                                <div class="col-sm-12 top-buffer-s">
                                                    <strong>Persons linked to the organisation are controlled by the organisation. The Department cannot manage this list of people.</strong>
                                                </div>
                                            </div> 
                                        </div>
                                        <div class="col-sm-4">
                                          <form class="form-horizontal" action="index.html" method="post">
                                              <div class="form-group">
                                                <label for="" class="col-sm-3 control-label">Pin 1</label>
                                                <div class="col-sm-6">
                                                    <input type="text" disabled class="form-control" name="phone" placeholder="" v-model="org.pins.one">
                                                </div>
                                              </div>
                                              <div class="form-group">
                                                <label for="" class="col-sm-3 control-label" >Pin 2</label>
                                                <div class="col-sm-6">
                                                    <input type="text" disabled class="form-control" name="email" placeholder="" v-model="org.pins.two">
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
                    <div :id="oTab" class="tab-pane fade">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">Proposals
                                            <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                            </a>
                                        </h3>
                                    </div>
                                    <div class="panel-body collapse in" :id="pBody">
                                        <div class="row">
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Region</label>
                                                    <select v-show="isLoading" class="form-control">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterProposalRegion">
                                                        <option value="All">All</option>
                                                        <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Activity</label>
                                                    <select v-show="isLoading" class="form-control" name="">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterProposalActivity">
                                                        <option value="All">All</option>
                                                        <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Status</label>
                                                    <select class="form-control" v-model="filterProposalStatus">
                                                        <option value="All">All</option>
                                                        <option value="current">Current</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'apply_proposal' }">New Proposal</router-link>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-3">
                                                <label for="">Expiry From</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <label for="">Expiry To</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Submitter</label>
                                                    <select class="form-control" v-model="filterProposalSubmitter">
                                                        <option value="">Select Submitter</option>
                                                        <option value="current">Current</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-12">
                                                <datatable ref="proposal_datatable" id="proposal_datatable" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">Approvals
                                            <a class="panelClicker" :href="'#'+aBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="aBody">
                                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                            </a>
                                        </h3>
                                    </div>
                                    <div class="panel-body collapse in" :id="aBody">
                                        <div class="row">
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Region</label>
                                                    <select v-show="isLoading" class="form-control">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterApprovalRegion">
                                                        <option value="All">All</option>
                                                        <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Activity</label>
                                                    <select v-show="isLoading" class="form-control" name="">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterApprovalActivity">
                                                        <option value="All">All</option>
                                                        <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Status</label>
                                                    <select class="form-control" v-model="filterApprovalStatus">
                                                        <option value="All">All</option>
                                                        <option value="current">Current</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-3">
                                                <label for="">Expiry From</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApprovalExpiryFrom">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <label for="">Expiry To</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApprovalExpiryTo">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="panel panel-default">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">Compliance with requirements
                                            <a class="panelClicker" :href="'#'+cBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="cBody">
                                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                            </a>
                                        </h3>
                                    </div>
                                    <div class="panel-body collapse in" :id="cBody">
                                        <div class="row">
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Region</label>
                                                    <select v-show="isLoading" class="form-control">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterComplianceRegion">
                                                        <option value="All">All</option>
                                                        <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Activity</label>
                                                    <select v-show="isLoading" class="form-control" name="">
                                                        <option value="">Loading...</option>
                                                    </select>
                                                    <select v-if="!isLoading" class="form-control" v-model="filterComplianceActivity">
                                                        <option value="All">All</option>
                                                        <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group">
                                                    <label for="">Status</label>
                                                    <select class="form-control" v-model="filterComplianceStatus">
                                                        <option value="All">All</option>
                                                        <option value="current">Current</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-3">
                                                <label for="">Expiry From</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueFrom">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <label for="">Expiry To</label>
                                                <div class="input-group date" id="booking-date-from">
                                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueTo">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
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
//import $ from 'jquery'
import Vue from 'vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import utils from '../utils'
import api from '../api'
export default {
    name: 'Organisation',
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            aBody: 'aBody'+vm._uid,
            pdBody: 'pdBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cdBody: 'cdBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
            dTab: 'dTab'+vm._uid,
            oTab: 'oTab'+vm._uid,
            org: null,
            loading: [],
            countries: [],
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            logsTable: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            logsDtOptions:{
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
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/action_log'),
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
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/comms_log'),
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
            // Filters for Proposals
            filterProposalRegion: '',
            filterProposalActivity: '',
            filterProposalStatus: 'All',
            filterProposalLodgedFrom: '',
            filterProposalLodgedTo: '',
            filterProposalSubmitter: '',
            // Filters for Approvals
            filterApprovalRegion: '',
            filterApprovalActivity: '',
            filterApprovalStatus: 'All',
            filterApprovalExpiryFrom: '',
            filterApprovalExpiryTo: '',
            // Filters for Compliance
            filterComplianceRegion: '',
            filterComplianceActivity: '',
            filterComplianceStatus: 'All',
            filterComplianceDueFrom: '',
            filterComplianceDueTo: '',
            proposal_headers:["Number","Region","Activity","Title","Submiter","Proponent","Status","Logded on","Action"],
            proposal_options:{
                  language: {
                      processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                  },
                  responsive: true,
                  ajax: {
                      "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/proposals') ,
                      "dataSrc": ''
                  },
                  columns: [
                      {data: "id"},
                      {
                          data:'data',
                          mRender:function (data,type,full) {
                              if (data) {
                                  let region = (data[0].region)?data[0].region:'n/a';
                                  return `${region}`;
                              }
                             return ''
                          }
                      },
                      {
                          data:'data',
                          mRender:function (data,type,full) {
                              if (data) {
                                   return `${data[0].activity}`;
                              }
                             return ''
                          }
                      },
                      {
                          data:'data',
                          mRender:function (data,type,full) {
                              if (data) {
                                   return `${data[0].project_details[0].project_title}`;
                              }
                             return ''
                          }
                      },
                      {
                          data: "submitter",
                          mRender:function (data,type,full) {
                              if (data) {
                                   return `${data.first_name} ${data.last_name}`;
                              }
                             return ''
                          }
                      },
                      {data: "applicant"},
                      {data: "processing_status"},
                      {data: "lodgement_date"},
                      {
                          mRender:function (data,type,full) {
                              let links = '';
                              if (full.processing_status == 'draft') {
                                 links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                 links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                              }
                              if (full.processing_status == 'accepted' || full.processing_status == 'under review') {
                                 links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                              }
                              return links;
                          }
                      }
                  ],
                  processing: true
            },
            contacts_headers:["Name","Phone","Mobile","Fax","Email","Action"],
            contacts_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {data:'phone_number'},
                    {data:'mobile_number'},
                    {data:'fax_number'},
                    {data:'email'},
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links +=  `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        }
                    }
                  ],
                  processing: true
            }
        }
    },
    components: {
        datatable,
    },
    computed: {
        isLoading: function () {
          return this.loading.length == 0;
        }
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    beforeRouteUpdate: function(to, from, next){
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.org = data[0];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    methods: {
        addContact: function(){
            this.$refs.add_contact.isModalOpen = true;
        },
        eventListeners: function(){
            let vm = this;
            vm.$refs.contacts_datatable.vmDataTable.on('click','.remove-contact',(e) => {
                e.preventDefault();

                let name = $(e.target).data('name');
                let email = $(e.target).data('email');
                let id = $(e.target).data('id');
                swal({
                    title: "Delete Contact",
                    text: "Are you sure you want to remove "+ name + "("+ email + ") as a contact  ?",
                    type: "error",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'
                }).then(() => {
                    vm.deleteContact(id);
                },(error) => {
                });
            });
        },
        updateDetails: function() {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,(vm.org.id+'/update_details')),JSON.stringify(vm.org),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingDetails = false;
                vm.org = response.body;
                if (vm.org.address == null){ vm.org.address = {}; }
                swal(
                    'Saved',
                    'Organisation details have been saved',
                    'success'
                )
            }, (error) => {
                console.log(error);
                vm.updatingDetails = false;
            });
        },
        addedContact: function() {
            let vm = this;
            swal(
                'Added',
                'The contact has been successfully added.',
                'success'
            )
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function(id){
            let vm = this;
            
            vm.$http.delete(helpers.add_endpoint_json(api.organisation_contacts,id),{
                emulateJSON:true
            }).then((response) => {
                swal(
                    'Contact Deleted', 
                    'The contact was successfully deleted',
                    'success'
                )
                vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
            }, (error) => {
                console.log(error);
                swal(
                    'Contact Deleted', 
                    'The contact could not be deleted because of the following error '+error,
                    'error'
                )
            });
        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,(vm.org.id+'/update_address')),JSON.stringify(vm.org.address),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingAddress = false;
                vm.org = response.body;
                swal(
                    'Saved',
                    'Address details have been saved',
                    'success'
                )
                if (vm.org.address == null){ vm.org.address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
        },
    },
    mounted: function(){
        this.personal_form = document.forms.personal_form;
    },
    updated: function(){
        let vm = this;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        }); 
        this.$nextTick(() => {
            this.eventListeners();
            helpers.initialiseActionLogs(this._uid,vm.$refs.showActionBtn,vm.logsDtOptions,vm.logsTable);
            helpers.initialiseCommLogs(this._uid,vm.$refs.showCommsBtn,vm.commsDtOptions,vm.commsTable);
        });
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
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
