<template>
    <div class="container" v-if="org" id="userInfo">
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Organisation Details <small> - View and update the organisation's details</small>
                        <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse in" :id="pBody">
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
                    <h3 class="panel-title">Address Details <small> - View and update the organisation's address details</small>
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
                            <div class="col-sm-3">
                                <input type="text" class="form-control" name="country" placeholder="" v-model="org.address.state">
                            </div>
                            <label for="" class="col-sm-1 control-label">Postcode</label>
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
                    <h3 class="panel-title">Contact Details <small> - View and update the organisation's contact details</small>
                        <a class="panelClicker" :href="'#'+cBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="cBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse" :id="cBody">
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
                                    <div class="col-sm-6">
                                        <h4><a @click.prevent="unlinkUser(d)" href="#" :data-id="d.id"><i class="fa fa-chain-broken"></i>&nbsp;Unlink</a></h4>
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
                                <label for="" class="col-sm-3 control-label">Pin 1:</label>
                                <div class="col-sm-6">
                                    <label class="control-label">{{org.pins.one}}</label>
                                </div>
                              </div>
                              <div class="form-group">
                                <label for="" class="col-sm-3 control-label" >Pin 2:</label>
                                <div class="col-sm-6">
                                    <label class="control-label">{{org.pins.two}}</label>
                                </div>
                              </div>
                            </form>
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
import utils from '../utils'
import api from '../api'
import AddContact from '@common-utils/add_contact.vue'
export default {
    name: 'Organisation',
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
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
        AddContact
    },
    computed: {
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
        unlinkUser: function(d){
            let vm = this;
            let org = vm.org;
            let org_name = org.name;
            let person = helpers.copyObject(d);
            swal({
                title: "Unlink From Organisation",
                text: "Are you sure you want to unlink "+person.name+" "+person.id+" from "+org.name+" ?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),{'user':person.id},{
                    emulateJSON:true
                }).then((response) => {
                    vm.org = response.body;
                    if (vm.org.address == null){ vm.org.address = {}; }
                    swal(
                        'Unlink',
                        'You have successfully unlinked '+person.name+' from '+org_name+'.',
                        'success'
                    )
                }, (error) => {
                    swal(
                        'Unlink',
                        'There was an error unlinking '+person.name+' from '+org_name+'. '+error.body,
                        'error'
                    )
                });
            },(error) => {
            }); 
        }
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
        });
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.top-buffer-s {
    margin-top: 25px;
}
</style>
