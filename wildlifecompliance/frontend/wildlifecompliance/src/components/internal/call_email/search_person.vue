<template lang="html">
    <div class="col-sm-12 form-group">
        <div class="row" v-if="isEditable">
            <label class="col-sm-3 control-label">Search Person</label>
            <div class="col-sm-6">
                <input :readonly="!isEditable" class="col-sm-5 form-control" id="search-person" />
            </div>
            <div class="col-sm-3">
                <input :readonly="!isEditable" type="button" class="pull-right btn btn-primary" value="Create New Person"@click.prevent="createNewPerson()" />
            </div>
        </div>
        <div class="col-md-12">
            <ul class="nav nav-tabs">
                <li class="active"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                <li><a data-toggle="tab" :href="'#'+oTab">Licensing</a></li>
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
                                    <div v-if="objectAlert" class="alert alert-danger">
                                        <p>test alert</p>
                                    </div>
                                    <form class="form-horizontal" name="personal_form" method="post">
                                        <div class="form-group" v-bind:class="{ 'has-error': errorGivenName }">
                                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                            <div class="col-sm-6">
                                                <div v-if="call_email.email_user">
                                                    <input :readonly="!isEditable" type="text" class="form-control" name="first_name" placeholder="" v-model="call_email.email_user.first_name" v-bind:key="call_email.email_user.id">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group" v-bind:class="{ 'has-error': errorLastName }">
                                            <label for="" class="col-sm-3 control-label">Last Name</label>
                                            <div class="col-sm-6">
                                                <div v-if="call_email.email_user">
                                                    <input :readonly="!isEditable" type="text" class="form-control" name="last_name" placeholder="" v-model="call_email.email_user.last_name" v-bind:key="call_email.email_user.id">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group" v-bind:class="{ 'has-error': errorDob }">
                                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                                            <div class="col-sm-6">
                                                <div v-if="call_email.email_user">
                                                    <input :readonly="!isEditable" type="date" class="form-control" name="dob" placeholder="" v-model="call_email.email_user.dob" v-bind:key="call_email.email_user.id">
                                                </div>
                                            </div>
                                        </div>
                                        <!-- <div class="form-group">
                                        <div class="col-sm-12">
                                                <button v-if="!updatingPersonal" class="pull-right btn btn-primary" @click.prevent="updatePersonal()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div> -->
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
                                            <div v-if="call_email.email_user"><div v-if="call_email.email_user.residential_address">
                                                <input type="text" class="form-control" name="street" placeholder="" v-model="call_email.email_user.residential_address.line1" v-bind:key="call_email.email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <div v-if="call_email.email_user"><div v-if="call_email.email_user.residential_address">
                                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="call_email.email_user.residential_address.locality" v-bind:key="call_email.email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <div v-if="call_email.email_user"><div v-if="call_email.email_user.residential_address">
                                                <input type="text" class="form-control" name="country" placeholder="" v-model="call_email.email_user.residential_address.state" v-bind:key="call_email.email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <div v-if="call_email.email_user"><div v-if="call_email.email_user.residential_address">
                                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="call_email.email_user.residential_address.postcode" v-bind:key="call_email.email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <div v-if="call_email.email_user"><div v-if="call_email.email_user.residential_address">
                                                <select class="form-control" name="country" v-model="call_email.email_user.residential_address.country" v-bind:key="call_email.email_user.residential_address.id">
                                                    <option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option>
                                                </select>
                                            </div></div>
                                        </div>
                                        </div>
                                        <!-- <div class="form-group">
                                        <div class="col-sm-12">
                                            <button v-if="!updatingAddress" class="pull-right btn btn-primary" @click.prevent="updateAddress()">Update</button>
                                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div>  -->
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
                                            <div v-if="call_email.email_user">
                                                <input :readonly="!isEditable" type="text" class="form-control" name="phone" placeholder="" v-model="call_email.email_user.phone_number" v-bind:key="call_email.email_user.id">
                                            </div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Mobile</label>
                                        <div class="col-sm-6">
                                            <div v-if="call_email.email_user">
                                                <input :readonly="!isEditable" type="text" class="form-control" name="mobile" placeholder="" v-model="call_email.email_user.mobile_number" v-bind:key="call_email.email_user.id">
                                            </div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Email</label>
                                        <div class="col-sm-6">
                                            <div v-if="call_email.email_user">
                                                <input :readonly="!isEditable" type="email" class="form-control" name="email" placeholder="" v-model="call_email.email_user.email" v-bind:key="call_email.email_user.id"> </div>
                                            </div>
                                        </div>
                                        <!-- <div class="form-group">
                                        <div class="col-sm-12">
                                            <button v-if="!updatingContact" class="pull-right btn btn-primary" @click.prevent="updateContact()">Update</button>
                                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div> -->
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row" v-if="isEditable">
                        <div class="col-sm-12">
                            <button v-if="!updatingContact" class="pull-right btn btn-primary" @click.prevent="save">Update</button>
                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                        </div>
                    </div>
                </div>
                <div :id="oTab" class="tab-pane fade">
                    <div v-if="call_email.email_user">
                        <ApplicationDashTable ref="applications_table" level='internal' :url='applications_url' v-bind:key="call_email.email_user.id"/>
                    </div>
                    <div v-if="call_email.email_user">
                        <LicenceDashTable ref="licences_table" level='internal' :url='licences_url' v-bind:key="call_email.email_user.id"/>
                    </div>
                    <div v-if="call_email.email_user">
                        <ReturnDashTable ref="returns_table" level='internal' :url='returns_url' v-bind:key="call_email.email_user.id"/>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
        
<script>
import Awesomplete from 'awesomplete';
import { api_endpoints, helpers } from '@/utils/hooks'
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import datatable from '@vue-utils/datatable.vue'
import ApplicationDashTable from '@common-components/applications_dashboard.vue'
import LicenceDashTable from '@common-components/licences_dashboard.vue'
import ReturnDashTable from '@common-components/returns_dashboard.vue'
import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';
import utils from '../utils'

export default {
    name: "search-person",
    data: function(){
        let vm = this;
        vm.max_items = 10;
        vm.ajax_for_person_search = null;

        return {
            awe: null,
            suggest_list: [],
            adBody: 'adBody'+vm._uid,
            pdBody: 'pdBody'+vm._uid,
            cdBody: 'cdBody'+vm._uid,
            odBody: 'odBody'+vm._uid,
            idBody: 'idBody'+vm._uid,
            dTab: 'dTab'+vm._uid,
            oTab: 'oTab'+vm._uid,
            user: {
                residential_address: {},
                wildlifecompliance_organisations: []
            },
            loading: [],
            countries: [],
            updatingAddress: false,
            updatingPersonal: false,
            updatingContact: false,
            errorGivenName: false,
            errorLastName: false,
            errorDob: false,
            objectAlert: false,

            forDemo: false,
        }
    },
    components: {
        datatable,
        ApplicationDashTable,
        LicenceDashTable,
        ReturnDashTable,
        //CommsLogs
    },
    computed: {
        ...mapGetters('callemailStore', {
            call_email: "call_email",
        }),
        ...mapGetters({
            // renderer_form_data: 'renderer_form_data',
            current_user: 'current_user',
        }),
        isReadonly: function() {
            if (this.call_email.status && this.call_email.status.id === 'draft') {
                return false;
            } else {
                return true;
            }
        },
        isEditable: function() {
            if (!this.forDemo){
                return true;
            }

            if (this.call_email.status && this.call_email.status.id === 'open' && this.current_user.is_officer) {
                return true;
            } else {
                return false;
            }
        },
        applications_url: function(){
            if (this.call_email.email_user && this.call_email.email_user.id){
                console.log('applications_url2: ' + this.call_email.email_user.id);
                return api_endpoints.applications_paginated+'internal_datatable_list?user_id=' + this.call_email.email_user.id;
            }
            console.log('applications_url');
            return api_endpoints.applications_paginated+'internal_datatable_list?user_id=-1';
        },
        licences_url: function(){
            console.log('licences_url');
            if (this.call_email.email_user && this.call_email.email_user.id){
                console.log('licences_url2: ' + this.call_email.email_user.id);
                return api_endpoints.licences_paginated+'internal_datatable_list?user_id=' + this.call_email.email_user.id;
            }
            return api_endpoints.licences_paginated+'internal_datatable_list?user_id=-1';
        },
        returns_url: function(){
            console.log('returns_url');
            if (this.call_email.email_user && this.call_email.email_user.id){
                console.log('returns_url2: ' + this.call_email.email_user.id);
                return api_endpoints.returns+'?user_id=' + this.call_email.email_user.id;
            }
            return api_endpoints.returns+'?user_id=-1';
        }
    },
    mounted: function(){
        this.$nextTick(function() {
            this.initAwesomplete();
            this.loadCountries();
        });
    },
    methods: {
        ...mapActions('callemailStore', {
            setEmailUserEmpty: "setEmailUserEmpty",
            saveCallEmail: 'saveCallEmail',
            saveCallEmailPerson: 'saveCallEmailPerson',
        }),
        save: async function() {
            await this.saveCallEmailPerson();
        },
        createNewPerson: function() {
            let vm = this;
            vm.setEmailUserEmpty();
        },
        updateContact: function() {
            console.log('aho');
            let vm = this;
            vm.updatingContact = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.call_email.email_user.id+'/update_contact')),JSON.stringify(vm.call_email.email_user),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingContact = false;
                // vm.user = response.body;
                if (vm.call_email.email_user.residential_address == null){ vm.call_email.email_user.residential_address = {}; }
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
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.call_email.email_user.id+'/update_address')),JSON.stringify(vm.call_email.email_user.residential_address),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingAddress = false;
                vm.call_email.email_user = response.body;
                if (vm.call_email.email_user.residential_address == null){ vm.call_email.email_user.residential_address = {}; }
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
        updatePersonal: function() {
            console.log('updatePersonal');
            let vm = this;
            vm.updatingPersonal = true;
            if (vm.call_email.email_user.residential_address == null){ vm.call_email.email_user.residential_address = {}; }
            let params = '?';
            params += '&first_name=' + vm.call_email.email_user.first_name;
            params += '&last_name=' + vm.call_email.email_user.last_name;
            params += '&dob=' + vm.call_email.email_user.dob;
            // if (vm.call_email.email_user.first_name == '' || vm.call_email.email_user.last_name == '' || (vm.call_email.email_user.dob == null || vm.call_email.email_user.dob == '')){
            if (vm.call_email.email_user.first_name == '' || vm.call_email.email_user.last_name == ''){
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
			vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.call_email.email_user.id+'/update_personal')),JSON.stringify(vm.call_email.email_user),{
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
        loadCountries: function(){
            let vm = this;
            let initialisers = [
                utils.fetchCountries(),
            ]
            Promise.all(initialisers).then(data => {
                vm.countries = data[0];
            });
        },
        loadEmailUser: function(id){
            let vm = this;
            let initialisers = [
                utils.fetchUser(id),
            ]
            Promise.all(initialisers).then(data => {
                vm.call_email.email_user = data[0];
                if(vm.call_email.email_user.residential_address == null){
                    vm.call_email.email_user.residential_address = {
                        line1: '',
                        locality: '',
                        state: 'WA',
                        postcode: '',
                        country: 'AU'
                    }
                }
                vm.call_email.email_user.residential_address = vm.call_email.email_user.residential_address != null ? vm.call_email.email_user.residential_address : {};
            });
        },
        search: function(searchTerm){
            var vm = this;
            vm.suggest_list = [];
            vm.suggest_list.length = 0;
            vm.awe.list = [];

            /* Cancel all the previous requests */
            if (vm.ajax_for_person_search != null){
                vm.ajax_for_person_search.abort();
                vm.ajax_for_person_search = null;
            }

            vm.ajax_for_person_search = $.ajax({
                type: 'GET',
                url: '/api/search_user/?search=' + searchTerm,
                success: function(data){
                    if (data && data.results) {
                        let persons = data.results;
                        let limit = Math.min(vm.max_items, persons.length);
                        for (var i = 0; i < limit; i++){
                            vm.suggest_list.push(persons[i])
                        }
                    }
                    vm.awe.list = vm.suggest_list;
                    vm.awe.evaluate();
                    console.log(vm.suggest_list);
                },
                error: function (e){
                    console.log(e);
                }
            });
        },
        initAwesomplete: function(){
            var self = this;

            var element_search = document.getElementById('search-person');
            self.awe = new Awesomplete(element_search, { 
                maxItems: self.max_items, 
                sort: false, 
                filter: ()=>{ return true; }, // Display all the items in the list without filtering.
                data: function(item, input){
                    let f_name = item.first_name?item.first_name:'';
                    let l_name = item.last_name?item.last_name:'';

                    let full_name = [f_name, l_name].filter(Boolean).join(' ');
                    let email = item.email?'E:' + item.email:'';
                    let p_number = item.phone_number?'P:' + item.phone_number:'';
                    let m_number = item.mobile_number?'M:' + item.mobile_number:'';
                    let dob = item.dob?'DOB:' + item.dob:'DOB: ---';
                    let myLabel = ['<span class="full_name">' + full_name + '</span>', email, p_number, m_number, dob].filter(Boolean).join('<br />');

                    return { 
                        label: myLabel,   // Displayed in the list below the search box
                        value: [full_name, dob].filter(Boolean).join(', '), // Inserted into the search box once selected
                        id: item.id
                    };
                }
            });
            $(element_search).on('keyup', function(ev){
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105) || (keyCode == 8) || (keyCode == 46)){
                    self.search(ev.target.value);
                    return false;
                }
            }).on('awesomplete-selectcomplete', function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                return false;
            }).on('awesomplete-select', function(ev){
                /* Retrieve element id of the selected item from the list
                 * By parsing it, we can get the order-number of the item in the list
                 */
                console.log("origin");
                console.log(ev.originalEvent.origin);
                let origin = $(ev.originalEvent.origin)
                let originTagName = origin[0].tagName;
                if (originTagName == "SPAN"){
                    origin = origin.parent();
                }
                let elem_id = origin[0].id;
                let reg = /^.+(\d+)$/gi;
                let result = reg.exec(elem_id)
                if(result[1]){
                    let idx = result[1];
                    self.loadEmailUser(self.suggest_list[idx].id);
                }else{
                    console.log("result");
                    console.log(result);
                }
            });
        },
    }
}
</script>        

<style scoped>
.awesomplete {
    z-index: 1050 !important;
}
.awesomplete > ul {
    z-index: 2001;
    top: 30px;
}
.awesomplete > ul > li {
    border-bottom: 1px solid lightgray;
    margin: 5px 10px 5px 10px;
}
.full_name {
    color: green;
}
.tab-content {
    padding: 10px;
    border: solid 1px lightgray;
}
.nav-tabs {
    border-bottom: none !important;
}
#search-person {
    z-index: 1000;
    /* width: 400px; */
}
.awesomplete {
    display: inherit !important;
}
</style>
