<template>
    <div class="container-fluid" id="internalUserInfo">
    <div class="row">
    <div class="col-md-10 col-md-offset-1">
        <div class="row">
            <h3>{{ user.first_name }} {{ user.last_name  }} - {{ user.dob }} ({{ user.email }})</h3>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :is_user_log="true" :disable_add_entry="false"/>
            </div>
            <div class="col-md-9">
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
                                    <h3 class="panel-title">Personal Details
                                        <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse in" :id="pdBody">
                                      <form class="form-horizontal" name="personal_form" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="first_name" placeholder="" v-model="user.first_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Last Name</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="last_name" placeholder="" v-model="user.last_name">
                                            </div>
                                          </div>                   
                                          <div class="form-group">
                                            <div class="col-sm-12">
                                                <button v-if="!updatingPersonal" class="pull-right btn btn-primary" @click.prevent="updatePersonal()">Update</button>
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
                                    <h3 class="panel-title">Identification
                                        <a class="panelClicker" :href="'#'+idBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="idBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse in" :id="idBody">
                                      <form class="form-horizontal" name="id_form" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Identification</label>
                                            <div class="col-sm-6">
                                                <img v-if="user.identification" width="100%" name="identification" v-bind:src="user.identification.file" />
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <div class="col-sm-12">
                                                <!-- output order in reverse due to pull-right at runtime -->
                                                <button v-if="!uploadingID" class="pull-right btn btn-primary" @click.prevent="uploadID()">Upload</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Uploading</button>
                                                <span class="pull-right" style="margin-left:10px;margin-top:10px;margin-right:10px">{{uploadedIDFileName}}</span>
                                                <span class="btn btn-primary btn-file pull-right">
                                                    Select ID to Upload<input type="file" ref="uploadedID" @change="readFileID()"/>
                                                </span>
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
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div v-if="loading.length == 0" class="panel-body collapse in" :id="adBody">
                                      <form class="form-horizontal" action="index.html" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="street" placeholder="" v-model="user.residential_address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="user.residential_address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="country" placeholder="" v-model="user.residential_address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="user.residential_address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <select class="form-control" name="country" v-model="user.residential_address.country">
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
                                    <h3 class="panel-title">Contact Details <small></small>
                                        <a class="panelClicker" :href="'#'+cdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="cdBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse in" :id="cdBody">
                                      <form class="form-horizontal" action="index.html" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="phone" placeholder="" v-model="user.phone_number">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Mobile</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="mobile" placeholder="" v-model="user.mobile_number">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Email</label>
                                            <div class="col-sm-6">
                                                <input type="email" class="form-control" disabled="disabled" name="email" placeholder="" v-model="user.email">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <div class="col-sm-12">
                                                <button v-if="!updatingContact" class="pull-right btn btn-primary" @click.prevent="updateContact()">Update</button>
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
                                    <h3 class="panel-title">Organisations <small></small>
                                        <a class="panelClicker" :href="'#'+odBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="odBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse in" :id="odBody">
                                      <div v-for="org in user.commercialoperator_organisations">
                                          <div class="form-group">
                                            <label for="" class="col-sm-2 control-label" >Organisation</label>
                                            <div class="col-sm-3">
                                                <input type="text" disabled class="form-control" name="organisation" v-model="org.name" placeholder="">
                                            </div>
                                            <label for="" class="col-sm-2 control-label" >ABN/ACN</label>
                                            <div class="col-sm-3">
                                                <input type="text" disabled class="form-control" name="organisation" v-model="org.abn" placeholder="">
                                            </div>
                                            <a style="cursor:pointer;text-decoration:none;" @click.prevent="unlinkUser(org)"><i class="fa fa-chain-broken fa-2x" ></i>&nbsp;Unlink</a>
                                          </div>
                                      </div>
                                      <div v-for="orgReq in orgRequest_pending">
                                          <div class="form-group">
                                            <label for="" class="col-sm-2 control-label" >Organisation</label>
                                            <div class="col-sm-3">
                                                <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.name" placeholder="">
                                            </div>
                                            <label for="" class="col-sm-2 control-label" >ABN/ACN</label>
                                            <div class="col-sm-3">
                                                <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.abn" placeholder="">
                                            </div>
                                            <label>Pending for Approval (#{{orgReq.id}})</label>
                                          </div>
                                      </div>
                                  </div>
                                </div>
                            </div>
                        </div>
                    </div> 
                    <div :id="oTab" class="tab-pane fade">
                        <ProposalDashTable ref="proposals_table" level='internal' :url='proposals_url'/>
                        <ApprovalDashTable ref="approvals_table" level='internal' :url='approvals_url'/>
                        <ComplianceDashTable ref="compliance_table" level='internal' :url='compliance_url'/>
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
import AddContact from '@common-utils/add_contact.vue'
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import utils from '../utils'
import api from '../api'
export default {
    name: 'User',
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            pdBody: 'pdBody'+vm._uid,
            cdBody: 'cdBody'+vm._uid,
            odBody: 'odBody'+vm._uid,
            idBody: 'idBody'+vm._uid,
            dTab: 'dTab'+vm._uid,
            oTab: 'oTab'+vm._uid,
            user: {
                residential_address: {},
                commercialoperatorcompliance_organisations: []
            },
            loading: [],
            countries: [],
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            uploadingID: false,
            uploadedID: null,
            empty_list: '/api/empty_list',
            logsTable: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/action_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/add_comms_log'),
            proposals_url: api_endpoints.proposals_paginated_external+'&submitter_id='+vm.$route.params.user_id,
            approvals_url: api_endpoints.approvals_paginated_external+'&submitter_id='+vm.$route.params.user_id,
            compliance_url: api_endpoints.compliances_paginated_external+'&submitter_id='+vm.$route.params.user_id,
            orgRequest_pending: [],
        }
    },
    components: {
        datatable,
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
        CommsLogs
    },
    computed: {
        isLoading: function () {
          return this.loading.length == 0;
        },
        uploadedIDFileName: function() {
            return this.uploadedID != null ? this.uploadedID.name: '';
        },
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchUser(to.params.user_id),
            utils.fetchOrgRequestPending(to.params.user_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.user = data[1];
                vm.user.residential_address = vm.user.residential_address != null ? vm.user.residential_address : {};
                vm.orgRequest_pending = data[2];
            });
        });
    },
    beforeRouteUpdate: function(to, from, next){
        let initialisers = [
            utils.fetchUser(to.params.user_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.user = data[0];
                vm.user.residential_address = vm.user.residential_address != null ? vm.user.residential_address : {};
            });
        });
    },
    methods: {
        eventListeners: function(){
            let vm = this;
            // Fix the table responsiveness when tab is shown
            $('a[href="#'+vm.oTab+'"]').on('shown.bs.tab', function (e) {
                vm.$refs.proposals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.approvals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.compliance_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
            });
        },
        updatePersonal: function() {
            let vm = this;
            vm.updatingPersonal = true;
            if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
            let params = '?';
            params += '&first_name=' + vm.user.first_name;
            params += '&last_name=' + vm.user.last_name;
            //params += '&dob=' + vm.user.dob;
            if (vm.user.first_name == '' || vm.user.last_name == '' ){
                let error_msg = 'Please ensure all fields are filled in.';
                swal({
                    title: 'Update Personal Details',
                    html: 'There was an error updating the user personal details.<br/>' + error_msg,
                    type: 'error'
                }).then(() => {
                    vm.updatingPersonal = false;
                });
                return;
            }
			vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.user.id+'/update_personal')),JSON.stringify(vm.user),{
				emulateJSON:true
			}).then((response) => {
				swal({
					title: 'Update Personal Details',
					html: 'User personal details has been successfully updated.',
					type: 'success',
				}).then(() => {
					vm.updatingPersonal = false;
				});
			}, (error) => {
				vm.updatingPersonal = false;
				let error_msg = '<br/>';
				for (var key in error.body) {
					if (key === 'dob') {
						error_msg += 'dob: Please enter a valid date.<br/>';
					} else {
						error_msg += key + ': ' + error.body[key] + '<br/>';
					}
				}
				swal({
					title: 'Update Personal Details',
					html: 'There was an error updating the user personal details.<br/>' + error_msg,
					type: 'error'
				})
			});
        },
        updateContact: function() {
            let vm = this;
            vm.updatingContact = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.user.id+'/update_contact')),JSON.stringify(vm.user),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingContact = false;
                vm.user = response.body;
                if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
                swal({
                    title: 'Update Contact Details',
                    html: 'User contact details has been successfully updated.',
                    type: 'success',
                })
            }, (error) => {
                vm.updatingContact = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    error_msg += key + ': ' + error.body[key] + '<br/>';
                }
                swal({
                    title: 'Update Contact Details',
                    html: 'There was an error updating the user contact details.<br/>' + error_msg,
                    type: 'error'
                })
            });
        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.user.id+'/update_address')),JSON.stringify(vm.user.residential_address),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingAddress = false;
                vm.user = response.body;
                if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
                swal({
                    title: 'Update Address Details',
                    html: 'User address details has been successfully updated.',
                    type: 'success',
                })
            }, (error) => {
                vm.updatingAddress = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    error_msg += key + ': ' + error.body[key] + '<br/>';
                }
                swal({
                    title: 'Update Address Details',
                    html: 'There was an error updating the user address details.<br/>' + error_msg,
                    type: 'error'
                })
            });
        },
        unlinkUser: function(org){
            let vm = this;
            let org_name = org.name;
            swal({
                title: "Unlink From Organisation",
                text: "Are you sure you want to unlink this user from "+org.name+" ?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),JSON.stringify(vm.user),{
                        emulateJSON:true
                    }).then((response) => {
                        vm.$http.get(helpers.add_endpoint_json(api_endpoints.users,vm.user.id)).then((response) => {
                            vm.user = response.body
                            if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
                            if (vm.user.commercialoperatorcompliance_organisations && vm.user.commercialoperatorcompliance_organisations.length > 0){
                              vm.managesOrg = 'Yes'
                            }
                            swal(
                                'Unlink',
                                'The user has been successfully unlinked from '+org_name+'.',
                                'success'
                            )
                        },(error) => {
                        })
                    }, (error) => {
                        swal(
                            'Unlink',
                            'There was an error unlinking the user from '+org_name+'.',
                            'error'
                        )
                    });
                }
            },(error) => {
            });
        },
        readFileID: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedID)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedID = _file;
        },
        uploadID: function() {
            let vm = this;
            console.log('uploading id');
            vm.uploadingID = true;
            let data = new FormData();
            data.append('identification', vm.uploadedID);
            console.log(data);
            if (vm.uploadedID == null){
                vm.uploadingID = false;
                swal({
                        title: 'Upload ID',
                        html: 'Please select a file to upload.',
                        type: 'error'
                });
            } else {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.user.id+'/upload_id')),data,{
                    emulateJSON:true
                }).then((response) => {
                    vm.uploadingID = false;
                    vm.uploadedID = null;
                    swal({
                        title: 'Upload ID',
                        html: 'The user ID has been successfully uploaded.',
                        type: 'success',
                    }).then(() => {
                        window.location.reload(true);
                    });
                }, (error) => {
                    console.log(error);
                    vm.uploadingID = false;
                    let error_msg = '<br/>';
                    for (var key in error.body) {
                        error_msg += key + ': ' + error.body[key] + '<br/>';
                    }
                    swal({
                        title: 'Upload ID',
                        html: 'There was an error uploading the user ID.<br/>' + error_msg,
                        type: 'error'
                    });
                });
            }
        },
        
    },
    mounted: function(){
        let vm = this;
        this.personal_form = document.forms.personal_form;
        this.eventListeners();
    },
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