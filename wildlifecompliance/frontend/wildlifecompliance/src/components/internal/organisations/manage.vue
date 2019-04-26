<template>
    <div class="container-fluid" id="internalOrgInfo">
    <div class="row">
    <div class="col-md-10 col-md-offset-1">
        <div class="row">
            <h3>{{ org.name }} - {{org.abn}}</h3>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" comms_add_url="test"/>
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
                                    <h3 class="panel-title">Identification<small> Upload organisation ID</small>
                                        <a class="panelClicker" :href="'#'+idBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="idBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                  </div>
                                  <div class="panel-body collapse" :id="idBody">
                                      <form class="form-horizontal" name="id_form" method="post">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Identification</label>
                                            <div class="col-sm-6">
                                                <img v-if="org.organisation.identification" width="100%" name="identification" v-bind:src="org.organisation.identification" />
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
                                    <div class ="row">
                                        <form class="form-horizontal" action="index.html" method="post">
                                            <div class="col-sm-6">

                                                <div class="form-group">
                                                    <label for="" class="col-sm-6 control-label"> Organisation User Pin Code 1:</label>
                                                    <div class="col-sm-6">
                                                        <label class="control-label">{{org.pins.three}}</label>
                                                    </div>
                                                </div>
                                                <div class="form-group">
                                                    <label for="" class="col-sm-6 control-label" >Organisation User Pin Code 2:</label>
                                                    <div class="col-sm-6">
                                                        <label class="control-label">{{org.pins.four}}</label>
                                                    </div>
                                                </div>
                                       
                              
                                             </div>
                                             <div class="col-sm-6">
                                  
                                                <div class="form-group" :disabled ='!myorgperms.is_admin'>
                                                    <label for="" class="col-sm-6 control-label"> Organisation Administrator Pin Code 1:</label>
                                                    <div class="col-sm-6">
                                                        <label class="control-label">{{org.pins.one}}</label>
                                                    </div>
                                                </div>
                                                <div class="form-group" :disabled ='!myorgperms.is_admin'>
                                                    <label for="" class="col-sm-6 control-label" >Organisation Administrator Pin Code 2:</label>
                                                    <div class="col-sm-6">
                                                        <label class="control-label">{{org.pins.two}}</label>
                                                    </div>
                                                </div>
                                            </div>
                                        </form>
                                    </div>

                                    <div class="row">
                                        <div class="col-sm-8">
                                            <div class="row">
                                                <div class="col-sm-12 top-buffer-s">
                                                    <strong>Persons linked to the organisation are controlled by the organisation. The Department cannot manage this list of people.</strong>
                                                </div>
                                            </div> 
                                        </div>
                       
                                    </div>
                                    <div>
                                        <datatable ref="contacts_datatable_user" id="organisation_contacts_datatable_ref" :dtOptions="contacts_options_ref" :dtHeaders="contacts_headers_ref" v-model="filterOrgContactStatus"/>
                                        <!-- <datatable ref="contacts_datatable_user" id="organisation_contacts_datatable_ref" :dtOptions="contacts_options_ref" :dtHeaders="contacts_headers_ref"/> -->
                                    </div>




                                    
                                  </div>
                                </div>
                            </div>
                        </div>
                    </div> 
                    <div :id="oTab" class="tab-pane fade">
                        <ApplicationDashTable ref="applications_table" level='internal' :url='applications_url'/>
                        <LicenceDashTable ref="licences_table" level='internal' :url='licences_url'/>
                        <ReturnDashTable ref="returns_table" level='internal' :url='returns_url'/>
                    </div>
                </div>
            </div>
        </div>
        </div>
        </div>
        <AddContact ref="add_contact" :org_id="org.id" />
    </div>
</template>

<script>
//import $ from 'jquery'
import Vue from 'vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import AddContact from '@common-components/add_contact.vue'
import ApplicationDashTable from '@common-components/applications_dashboard.vue'
import LicenceDashTable from '@common-components/licences_dashboard.vue'
import ReturnDashTable from '@common-components/returns_dashboard.vue'
import CommsLogs from '@common-components/comms_logs.vue'
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
            idBody: 'idBody'+vm._uid,
            org: {
                address: {}
            },
            myorgperms: null,
            loading: [],
            countries: [],
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            uploadingID: false,
            uploadedID: null,
            empty_list: '/api/empty_list',
            logsTable: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/action_log'),
            contacts_headers:["Name","Phone","Mobile","Fax","Email","Action"],
            contacts_headers_ref:["Name","Role","Email","Status"],
            applications_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/applications'),
            licences_url: api_endpoints.licences+'?org_id='+vm.$route.params.org_id,
            returns_url: api_endpoints.returns+'?org_id='+vm.$route.params.org_id,
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
                            if (full.user_status.id == 'draft' ){
                                links +=  `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            }
                            return links;
                        }
                    }
                ],
                processing: true
            },

            contacts_options_ref:{
               language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts_exclude'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {data:'user_role'},
                    {data:'email'},
                    {data:'user_status'},
                  ],
                  processing: true
                  
                
            }



        }
    },
    components: {
        datatable,
        ApplicationDashTable,
        LicenceDashTable,
        ReturnDashTable,
        AddContact,
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
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.myorgperms = data[2];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    beforeRouteUpdate: function(to, from, next){
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.org = data[0];
                vm.myorgperms = data[1];
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
                }).then((result) => {
                    if (result.value) {
                        vm.deleteContact(id);
                    }
                },(error) => {
                });
            });
            // Fix the table responsiveness when tab is shown
            $('a[href="#'+vm.oTab+'"]').on('shown.bs.tab', function (e) {
                vm.$refs.applications_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.licences_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.returns_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
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
            
            vm.$http.delete(helpers.add_endpoint_json(api_endpoints.organisation_contacts,id),{
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
            vm.uploadingID = true;
            let data = new FormData();
            data.append('identification', vm.uploadedID);
            if (vm.uploadedID == null){
                vm.uploadingID = false;
                swal({
                        title: 'Upload ID',
                        html: 'Please select a file to upload.',
                        type: 'error'
                });
            } else {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,(vm.org.id+'/upload_id')),data,{
                    emulateJSON:true
                }).then((response) => {
                    vm.uploadingID = false;
                    vm.uploadedID = null;
                    swal({
                        title: 'Upload ID',
                        html: 'The organisation ID has been successfully uploaded.',
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
                        html: 'There was an error uploading the organisation ID.<br/>' + error_msg,
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
