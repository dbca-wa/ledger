<template>
    <div class="container" id="userInfo">
        <div v-if="showCompletion" class="row">
            <div class="col-sm-12">
                <div class="well well-sm">
                    <div class="row">
                        <div class="col-sm-12">
                            <p>
                                We have detected that this is the first time you have logged into the system.Please take a moment to provide us with your details
                                (personal details, address details, contact details, and weather you are managing approvals for an organisation).
                                Once completed, click Continue to start using the system.
                            </p>
                            <a :disabled="!completedProfile" href="/" class="btn btn-primary pull-right">Continue</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <i v-if="showCompletion && profile.personal_details" class="fa fa-check fa-2x pull-left" style="color:green"></i>
                    <i v-else-if="showCompletion && !profile.personal_details" class="fa fa-times fa-2x pull-left" style="color:red"></i>
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
                    <i v-if="showCompletion && profile.address_details" class="fa fa-check fa-2x pull-left" style="color:green"></i>
                    <i v-else-if="showCompletion && !profile.address_details" class="fa fa-times fa-2x pull-left" style="color:red"></i>
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
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Organisation <small>Link to the Organisations you are an employee of and for which you are managing approvals</small>
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse" :id="oBody">
                      <form class="form-horizontal" name="orgForm" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-5 control-label">Do you manage approvals on behalf of an organisation?</label>
                            <div class="col-sm-4">
                                <label class="radio-inline">
                                  <input type="radio" name="behalf_of_org" v-model="managesOrg" value="Yes"> Yes
                                </label>
                                <label class="radio-inline">
                                  <input :disabled="hasOrgs" type="radio" name="behalf_of_org" v-model="managesOrg" value="No" > No
                                </label>
                            </div>
                          </div>
                          <div class="form-group" v-if="managesOrg=='Yes'">
                            <div class="col-sm-12">
                                <button class="btn btn-primary pull-right" v-if="hasOrgs && !addingCompany" @click.prevent="addCompany()">Add Another Organisation</button>   
                            </div>
                          </div>
                          <div v-for="org in profile.disturbance_organisations">
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

                          <div v-for="orgReq in orgRequest_list">
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >Organisation</label>
                                <div class="col-sm-3"> 
                                    <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.name" placeholder="">
                                </div>
                                <label for="" class="col-sm-2 control-label" >ABN/ACN</label>
                                <div class="col-sm-3"> 
                                    <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.abn" placeholder="">
                                </div>
                                <lable>&nbsp;Pending for approval</lable>
                              </div>
                          </div>

                          <div style="margin-top:15px;" v-if="addingCompany">
                              <h3> New Organisation</h3>
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >Organisation</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="organisation" v-model="newOrg.name" placeholder="">
                                </div>
                              </div>
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >ABN/ACN</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="abn" v-model="newOrg.abn" placeholder="">
                                </div>
                                <div class="col-sm-2">
                                    <button @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>
                                </div>
                              </div>
                              <div class="form-group" v-if="newOrg.exists && newOrg.detailsChecked">
                                  <label class="col-sm-12" style="text-align:left;margin-bottom:20px;">
                                    This organisation has already been  registered with the system.Please enter the two pin codes:</br>
                                    These pin codes can be retrieved from ({{newOrg.first_five}})
                                  </label>
                                  <label for="" class="col-sm-2 control-label" >Pin 1</label>
                                  <div class="col-sm-2">
                                    <input type="text" class="form-control" name="abn" v-model="newOrg.pin1" placeholder="">
                                  </div>
                                  <label for="" class="col-sm-2 control-label" >Pin 2</label>
                                  <div class="col-sm-2">
                                    <input type="text" class="form-control" name="abn" v-model="newOrg.pin2" placeholder="">
                                  </div>
                                  <div class="col-sm-2">
                                    <button v-if="!validatingPins" @click.prevent="validatePins()" class="btn btn-primary pull-left">Validate</button>
                                    <button v-else class="btn btn-primary pull-left"><i class="fa fa-spin fa-spinner"></i>&nbsp;Validating Pins</button>
                                  </div>
                              </div>
                              <div class="form-group" v-else-if="!newOrg.exists && newOrg.detailsChecked">
                                  <label class="col-sm-12" style="text-align:left;">
                                    This organisation has not yet been registered with this system. Please upload a letter on organisation head stating that you are an employee of this origanisation.</br>
                                  </label>
                                  <div class="col-sm-12">
                                    <span class="btn btn-primary btn-file pull-left">
                                        Atttach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                    </span>
                                    <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                  </div>
                                  <label for="" class="col-sm-10 control-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.</label>
                                  <div class="col-sm-12">
                                    <button v-if="!registeringOrg" :disabled="!isFileUploaded" @click.prevent="orgRequest()" class="btn btn-primary pull-right">Submit</button>
                                    <button v-else disabled class="btn btn-primary pull-right"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                  </div>
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
import $ from 'jquery'
import { api_endpoints, helpers } from '@/utils/hooks'
export default {
    name: 'Profile',
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
            profile: {
                disturbance_organisations:[],
                residential_address : {}
            },
            newOrg: {
                'detailsChecked': false,
                'exists': false
            },
            countries: [],
            loading: [],
            registeringOrg: false,
            validatingPins: false,
            checkingDetails: false,
            addingCompany: false,
            managesOrg: 'No',
            uploadedFile: null,
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            registeringOrg: false,
            orgRequest_list: [],
        }
    },
    watch: {
        managesOrg: function() {
            if (this.managesOrg  == 'Yes' && !this.hasOrgs && this.newOrg){
                 this.addCompany()
            } else if (this.managesOrg == 'No' && this.newOrg){
                this.resetNewOrg();
                this.uploadedFile = null;
                this.addingCompany = false;
            } 
        }
    },
    computed: {
        hasOrgs: function() {
            return this.profile.disturbance_organisations && this.profile.disturbance_organisations.length > 0 ? true: false;
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        isFileUploaded: function() {
            return this.uploadedFile != null ? true: false;
        },
        showCompletion: function() {
            return this.$route.name == 'first-time'
        },
        completedProfile: function(){
            return this.profile.contact_details && this.profile.personal_details && this.profile.address_details;
        }
    },
    methods: {
        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
        },
        addCompany: function (){
            this.newOrg.push = {
                'name': '',
                'abn': '',
            };
            this.addingCompany=true;
        },
        resetNewOrg: function(){
            this.newOrg = {
                'detailsChecked': false,
                'exists': false
            };
        },
        updatePersonal: function() {
            let vm = this;
            vm.updatingPersonal = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
                emulateJSON:true
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
                emulateJSON:true
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
                emulateJSON:true
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
        checkOrganisation: function() {
            let vm = this;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,'existance'),JSON.stringify(this.newOrg),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                this.newOrg.exists = response.body.exists;
                this.newOrg.detailsChecked = true;
                this.newOrg.id = response.body.id;
                if (response.body.first_five){this.newOrg.first_five = response.body.first_five }
            }, (error) => {
                console.log(error);
            });
        },

        fetchOrgRequestList: function() { //Fetch all the Organisation requests submitted by user which are pending for approval.
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'user_list')).then((response) => {
                
                vm.orgRequest_list=response.body; 
            }, (error) => {
                console.log(error);
            });
        },



        validatePins: function() {
            let vm = this;
            vm.validatingPins = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,(vm.newOrg.id+'/validate_pins')),JSON.stringify(this.newOrg),{
                emulateJSON:true
            }).then((response) => {
                if (response.body.valid){
                    swal(
                        'Validate Pins',
                        'The pins you entered have been validated and you have now been linked to this organisation.',
                        'success'
                    )
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    Vue.http.get(api_endpoints.profile).then((response) => {
                        vm.profile = response.body
                        if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                        if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                    },(error) => {
                        console.log(error);
                    })
                }else {
                    swal(
                        'Validate Pins',
                        'The pins you entered were incorrect', 
                        'error'
                    )
                }
                vm.validatingPins = false;
            }, (error) => {
                vm.validatingPins = false;
                console.log(error);
            });
        },
        orgRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData()
            data.append('name', vm.newOrg.name)
            data.append('abn', vm.newOrg.abn)
            data.append('identification', vm.uploadedFile)
            vm.$http.post(api_endpoints.organisation_requests,data,{
                emulateJSON:true
            }).then((response) => {
                vm.registeringOrg = false;
                vm.uploadedFile = null;
                vm.addingCompany = false;
                vm.resetNewOrg();
                swal(
                    'Sent',
                    'Your organisation request has been successfuly submited.',
                    'success'
                )
            }, (error) => {
                vm.registeringOrg = false;
                console.log(error);
            });

        },
        toggleSection: function (e) {
            let el = e.target;
            let chev = null;
            console.log(el);
            $(el).on('click', function (event) {
                chev = $(this);
                console.log(chev);
                $(chev).toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
            })
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
        unlinkUser: function(org){
            let vm = this;
            let org_name = org.name;
            swal({
                title: "Unlink From Organisation",
                text: "Are you sure you want to be unlinked from "+org.name+" ?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),{'user':vm.profile.id},{
                    emulateJSON:true
                }).then((response) => {
                    Vue.http.get(api_endpoints.profile).then((response) => {
                        vm.profile = response.body
                        if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                        if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                    },(error) => {
                        console.log(error);
                    })
                    swal(
                        'Unlink',
                        'You have been successfully unlinked from '+org_name+'.',
                        'success'
                    )
                }, (error) => {
                    swal(
                        'Unlink',
                        'There was an error unlinking you from '+org_name+'. '+error.body,
                        'error'
                    )
                });
            },(error) => {
            }); 
        }
    },
    beforeRouteEnter: function(to,from,next){
        Vue.http.get(api_endpoints.profile).then((response) => {
            if (response.body.address_details && response.body.personal_details && response.body.contact_details && to.name == 'first-time'){
                window.location.href='/';
            }
            else{
                next(vm => {
                    vm.profile = response.body
                    if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                    if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                });
            }
        },(error) => {
            console.log(error);
        })
    },
    mounted: function(){
        this.fetchCountries();
        this.fetchOrgRequestList();
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
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
</style>
