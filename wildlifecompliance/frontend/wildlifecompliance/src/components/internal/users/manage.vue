<template>
    <div class="container-fluid" id="internalUserInfo">
    <div class="row">
    <div class="col-md-10 col-md-offset-1">
        <div class="row">
            <h3>{{ user.first_name }} {{ user.last_name  }} - {{ user.dob }}</h3>
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
                                    <h3 class="panel-title">Person Details
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
                                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                                            <div class="col-sm-6">
                                                <input type="date" class="form-control" name="dob" placeholder="" v-model="user.dob">
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
    </div>
</template>

<script>
//import $ from 'jquery'
import Vue from 'vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import AddContact from '@common-utils/add_contact.vue'
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import LicenceDashTable from '@common-utils/licences_dashboard.vue'
import ReturnDashTable from '@common-utils/returns_dashboard.vue'
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
            dTab: 'dTab'+vm._uid,
            oTab: 'oTab'+vm._uid,
            user: {
                address: {}
            },
            loading: [],
            countries: [],
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            empty_list: '/api/empty_list',
            logsTable: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/action_log'),
            applications_url: helpers.add_endpoint_json(api_endpoints.users,vm.$route.params.user_id+'/applications'),
            licences_url: api_endpoints.licences+'?user_id='+vm.$route.params.user_id,
            returns_url: api_endpoints.returns+'?user_id='+vm.$route.params.user_id,
        }
    },
    components: {
        datatable,
        ApplicationDashTable,
        LicenceDashTable,
        ReturnDashTable,
        CommsLogs
    },
    computed: {
        isLoading: function () {
          return this.loading.length == 0;
        }
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchUser(to.params.user_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.user = data[1];
                vm.user.residential_address = vm.user.residential_address != null ? vm.user.residential_address : {};
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
                vm.$refs.applications_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.licences_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.returns_table.$refs.application_datatable.vmDataTable.columns.adjust().responsive.recalc();
            });
        },
        updateDetails: function() {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.user.id+'/update_personal')),JSON.stringify(vm.user),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingDetails = false;
                vm.user = response.body;
                if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
                swal(
                    'Saved',
                    'Person details have been saved',
                    'success'
                )
            }, (error) => {
                console.log(error);
                vm.updatingDetails = false;
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
                swal(
                    'Saved',
                    'Address details have been saved',
                    'success'
                )
                if (vm.user.residential_address == null){ vm.user.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
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
