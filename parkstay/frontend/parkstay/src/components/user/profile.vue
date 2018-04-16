<template>
    <div class="container" id="userInfo">
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Personal Details <small>Provide your personal details</small>
                        <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse in" :id="pBody">
                      <form class="form-horizontal" name="personal_form" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Given name(s)</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="first_name" placeholder="" v-model="profile.first_name">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Surname</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="last_name" placeholder="" v-model="profile.last_name">
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
                    <h3 class="panel-title">Address Details <small>Provide your address details</small>
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
                                <input type="text" class="form-control" name="street" placeholder="" v-model="profile.residential_address.line1">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="profile.residential_address.locality">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">State</label>
                            <div class="col-sm-3">
                                <input type="text" class="form-control" name="country" placeholder="" v-model="profile.residential_address.state">
                            </div>
                            <label for="" class="col-sm-1 control-label">Postcode</label>
                            <div class="col-sm-2">
                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="profile.residential_address.postcode">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Country</label>
                            <div class="col-sm-4">
                                <select class="form-control" name="country" v-model="profile.residential_address.country">
                                    <option v-for="c in countries" :value="c.iso_3166_1_a2">{{ c.printable_name }}</option>
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
                    <i v-if="showCompletion && profile.contact_details" class="fa fa-check fa-2x pull-left" style="color:green"></i>
                    <i v-else-if="showCompletion && !profile.contact_details" class="fa fa-times fa-2x pull-left" style="color:red"></i>
                    <h3 class="panel-title">Contact Details <small>Provide your contact details</small>
                        <a class="panelClicker" :href="'#'+cBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="cBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse" :id="cBody">
                      <form class="form-horizontal" action="index.html" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Phone (work)</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="phone" placeholder="" v-model="profile.phone_number">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Mobile</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="mobile" placeholder="" v-model="profile.mobile_number">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Email</label>
                            <div class="col-sm-6">
                                <input type="email" class="form-control" name="email" placeholder="" v-model="profile.email">
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
    </div>
</template>

<script>
import Vue from 'vue'
import {$,api_endpoints,helpers,swal} from "../../hooks.js"
export default {
    name: 'Profile',
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            profile: {
                residential_address : {}
            },
            countries: [],
            loading: [],
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
        }
    },
    watch: {
    },
    computed: {
    },
    methods: {
        updatePersonal: function() {
            let vm = this;
            vm.updatingPersonal = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
                emulateJSON:true,
                headers: {
                    'X-CSRFToken': helpers.getCookie('csrftoken')
                }
            }).then((response) => {
                console.log(response);
                vm.updatingPersonal = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingPersonal = false;
            });
        },
        updateContact: function() {
            let vm = this;
            vm.updatingContact = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_contact')),JSON.stringify(vm.profile),{
                emulateJSON:true,
                headers: {
                    'X-CSRFToken': helpers.getCookie('csrftoken')
                }
            }).then((response) => {
                console.log(response);
                vm.updatingContact = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingContact = false;
            });
        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_address')),JSON.stringify(vm.profile.residential_address),{
                emulateJSON:true,
                headers: {
                    'X-CSRFToken': helpers.getCookie('csrftoken')
                }
            }).then((response) => {
                console.log(response);
                vm.updatingAddress = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
        },
        fetchCountries:function (){
            let vm =this;
            vm.loading.push('fetching countries');
            vm.$http.get(api_endpoints.countries).then((response)=>{
                vm.countries = response.body;
                vm.loading.splice('fetching countries',1);
            },(response)=>{
                console.log(response);
                vm.loading.splice('fetching countries',1);
            });
        },
    },
    beforeRouteEnter: function(to,from,next){
        Vue.http.get(api_endpoints.profile,{
            headers: {
                'X-CSRFToken': helpers.getCookie('csrftoken')
            },
        }).then((response) => {
            next(vm => {
                vm.profile = response.body
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            });
        },(error) => {
            console.log(error);
        })
    },
    mounted: function(){
        this.fetchCountries();
        this.personal_form = document.forms.personal_form;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        }); 
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
