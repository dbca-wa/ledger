<template>
    <div class="container" id="userInfo">
        <div v-if="showCompletion" class="row">
            <div class="col-sm-12">
                <div class="well well-sm">
                    <div class="row">
                        <div class="col-sm-12">
                            <p>
                                We have detected that this may be the first time you have logged into the system.Please take a moment to provide us with your details
                                (personal details, address details, contact details, and whether you are managing licences for an organisation).
                                Once completed, click Continue to start using the system.
                            </p>
                            <button v-if="completedProfile" @click.prevent="userProfileCompleted()" class="btn btn-primary pull-right">Continue</button>
                            <button v-else disabled class="btn btn-primary pull-right">Complete profile to continue</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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
                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                            <div class="col-sm-6">
                                <input type="date" class="form-control" name="dob" placeholder="" max="2100-12-31" v-model="profile.dob">
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
                    <h3 class="panel-title">Identification <small>Upload your photo ID</small>
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
                                <img v-if="profile.identification" width="100%" name="identification" v-bind:src="profile.identification.file" />
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
                                <input disabled type="email" class="form-control" name="email" placeholder="" v-model="profile.email">
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
                    <h3 class="panel-title">Organisations <small>Link to the Organisations you are an employee of and for which you are managing licences</small>
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse" :id="oBody">
                      <form class="form-horizontal" name="orgForm" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-5 control-label">Do you manage licences on behalf of an organisation?</label>
                            <div class="col-sm-4">
                                 <label class="radio-inline">
                                  <input :disabled="hasOrgs" type="radio" name="behalf_of_org" v-model="managesOrg" value="No" > No
                                </label>
                                <label class="radio-inline">
                                  <input type="radio" name="behalf_of_org" v-model="managesOrg" value="Yes"> Yes
                                </label>
                                 <label class="radio-inline">
                                  <input type="radio" name="behalf_of_org" v-model="managesOrg" value="Consultant"> Yes, as a consultant
                                </label>
                            </div>
                            <div v-if="managesOrg=='Yes'">
                                <div class="col-sm-3">
                                    <button class="btn btn-primary" v-if="hasOrgs && !addingCompany" @click.prevent="addCompany()">Add Another Organisation</button>
                                </div>
                            </div>
                          </div>

                          



                          <div v-for="org in profile.wildlifecompliance_organisations">
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >Organisation</label>
                                <div class="col-sm-3"> 
                                    <input type="text" disabled class="form-control" name="organisation" v-model="org.name" placeholder="">
                                </div>
                                <label for="" class="col-sm-1 control-label" >ABN/ACN</label>
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
                                <label for="" class="col-sm-1 control-label" >ABN/ACN</label>
                                <div class="col-sm-3"> 
                                    <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.abn" placeholder="">
                                </div>
                                <label><i class="fa fa-hourglass-o fa-2x" ></i> Pending Approval</label>
                              </div>
                          </div>
                          <div v-for="orgReq in orgRequest_amendment_requested">
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >Organisation</label>
                                <div class="col-sm-3">
                                    <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.name" placeholder="">
                                </div>
                                <label for="" class="col-sm-1 control-label" >ABN/ACN</label>
                                <div class="col-sm-3">
                                    <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.abn" placeholder="">
                                </div>
                                    <span class="btn btn-info btn-file pull-left">
                                        Upload New File <input type="file" ref="uploadedFile" @change="uploadNewFileUpdateOrgRequest(orgReq)"/>
                                    </span>
                                    <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                              </div>
                          </div>

                          <div v-if="managesOrg=='Consultant' && addingCompany">
                              <h3>New Organisation (as consultant)</h3>
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
                                      <button v-if="newOrg.detailsChecked" @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>
                                  </div>
                              </div>
                              <div class="form-group">
                                    <label class="col-sm-12" style="text-align:left;">
                                      Please upload a letter on organisation letter head stating that you are a consultant for the organisation.
                                        <span class="btn btn-info btn-file">
                                            Atttach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                        </span>
                                        <span  style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                    </label>
                                    </br>

                                    <label for="" class="col-sm-10 control-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.
                                    </label>


                                    <div class="col-sm-12">
                                      <button v-if="!registeringOrg" @click.prevent="orgConsultRequest()" class="btn btn-primary pull-left">Submit</button>
                                      <button v-else disabled class="btn btn-primary pull-right"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                    </div>
                              </div>
                           </div>




                          <div style="margin-top:15px;" v-if="managesOrg=='Yes' && addingCompany">
                              <h3>New Organisation</h3>
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
                                    This organisation has already been registered with the system. Please enter the two pin codes below.</br>
                                    These pin codes can be retrieved from one of the following people:</br> {{newOrg.first_five}}
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
                                    This organisation has not yet been registered with this system. Please upload a letter on organisation head stating that you are an employee of this organisation.</br>
                                  </label>
                                  <div class="col-sm-12">
                                    <span class="btn btn-info btn-file pull-left">
                                        Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                    </span>
                                    <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                  </div>
                                  <label for="" class="col-sm-10 control-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.</label>
                                  <div class="col-sm-12">
                                    <button v-if="!registeringOrg" @click.prevent="orgRequest()" class="btn btn-primary pull-right">Submit</button>
                                    <button v-else disabled class="btn btn-primary pull-right"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                  </div>
                              </div>
                              <div class="form-group" v-else-if="newOrg.exists && !newOrg.detailsChecked">
                                  <label class="col-sm-12" style="text-align:left;">
                                    Please upload a letter on organisation head stating that you are an employee of this organisation.</br>
                                  </label>
                                  <div class="col-sm-12">
                                    <span class="btn btn-info btn-file pull-left">
                                        Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                    </span>
                                    <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                  </div>
                                  <label for="" class="col-sm-10 control-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.</label>
                                  <div class="col-sm-12">
                                    <button v-if="!registeringOrg" @click.prevent="orgRequest()" class="btn btn-primary pull-right">Submit</button>
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
            idBody: 'idBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
            profile: {
                first_name: '',
                last_name: '',
                dob: '',
                wildlifecompliance_organisations:[],
                residential_address : {}
            },
            
            newOrg: {
                'name': '',
                'abn': '',
                'detailsChecked': false,
                'exists': false
            },
            countries: [],
            loading: [],
            registeringOrg: false,
            validatingPins: false,
            uploadingID: false,
            checkingDetails: false,
            addingCompany: false,
            managesOrg: 'No',
            managesOrgConsultant: 'No',
            uploadedFile: null,
            uploadedID: null,
            updatingPersonal: false,
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            role:null,
            orgRequest_pending:[],
            orgRequest_amendment_requested:[],
            new_user: false
        }
    },
    watch: {
        managesOrg: function() {
            if (this.managesOrg == 'Yes'){
              this.newOrg.detailsChecked = false;
              this.role = 'employee'
            } else if (this.managesOrg == 'Consultant'){
              this.newOrg.detailsChecked = false;
              this.role ='consultant'
            }else{this.role = null
              this.newOrg.detailsChecked = false;
            }

            if (this.managesOrg  == 'Yes' && !this.hasOrgs && this.newOrg){
                this.addCompany()

            } else if (this.managesOrg == 'No' && this.newOrg){
                this.resetNewOrg();
                this.uploadedFile = null;
                this.addingCompany = false;
            } else if (this.managesOrg == 'Consultant' && this.newOrg) {
                this.addCompany();
            } else {
                this.addCompany()
                this.addingCompany=false
            }
        },
  
    },
    computed: {
        hasOrgs: function() {
            return this.profile.wildlifecompliance_organisations && this.profile.wildlifecompliance_organisations.length > 0 ? true: false;
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        uploadedIDFileName: function() {
            return this.uploadedID != null ? this.uploadedID.name: '';
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
        deleteUserLogout: function() {
            let vm = this;
            vm.$http.delete(helpers.add_endpoint_json(api_endpoints.users,vm.profile.id)).then((response) => {
                window.location.href='/ledger/logout';
            },(error) => {
            })
        },
        updatePersonal: function() {
            let vm = this;
            vm.updatingPersonal = true;
            if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            let params = '?';
            params += '&first_name=' + vm.profile.first_name;
            params += '&last_name=' + vm.profile.last_name;
            params += '&dob=' + vm.profile.dob;
            if (vm.profile.first_name == '' || vm.profile.last_name == '' || (vm.profile.dob == null || vm.profile.dob == '')){
                let error_msg = 'Please ensure all fields are filled in.';
                swal({
                    title: 'Update Personal Details',
                    html: 'There was an error updating your personal details.<br/>' + error_msg,
                    type: 'error'
                }).then(() => {
                    vm.updatingPersonal = false;
                    vm.profile.personal_details = false;
                });
                return;
            }
            if (vm.new_user == 'True') {
                swal({
                    title: "Update Personal Details",
                    html: 'If you already have a Parks and Wildlife customer account under another email address, please ' +
                        '<strong>log out and sign in again with that account</strong> and ' +
                        'instead add <strong>' + vm.profile.email + '</strong> as a new Profile.<br/><br/>If this is a new account, please proceed to update ' +
                        'your details.',
                    type: "question",
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    confirmButtonText: 'Okay',
                    showCancelButton: true,
                    cancelButtonText: 'Logout',
                    cancelButtonClass: 'btn btn-danger'
                }).then((result) => {
                    if (result.value) {
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
                            emulateJSON:true
                        }).then((response) => {
                            swal({
                                title: 'Update Personal Details',
                                html: 'Your personal details has been successfully updated.',
                                type: 'success',
                            }).then(() => {
                                vm.updatingPersonal = false;
                                vm.profile.personal_details = true;
                                if (vm.completedProfile) {
                                    vm.$http.get(api_endpoints.user_profile_completed).then((response) => {
                                    },(error) => {
                                    })
                                }
                            });
                        }, (error) => {
                            vm.updatingPersonal = false;
                            vm.profile.personal_details = false;
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
                                html: 'There was an error updating your personal details.<br/>' + error_msg,
                                type: 'error'
                            })
                        });
                    } else if (result.dismiss === swal.DismissReason.cancel) {
                        vm.updatingPersonal = false;
                        vm.deleteUserLogout();
                        return;
                    }
                }, (error) => {
                    vm.updatingPersonal = false;
                    vm.profile.personal_details = false;
                    swal({
                        title: 'Update Personal Details',
                        html: 'There was an error updating your personal details.',
                        type: 'error'
                    })
                });
            } else {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
                    emulateJSON:true
                }).then((response) => {
                    swal({
                        title: 'Update Personal Details',
                        html: 'Your personal details has been successfully updated.',
                        type: 'success',
                    }).then(() => {
                        vm.updatingPersonal = false;
                        vm.profile.personal_details = true;
                        if (vm.completedProfile) {
                            vm.$http.get(api_endpoints.user_profile_completed).then((response) => {
                            },(error) => {
                            })
                        }
                    });
                }, (error) => {
                    vm.updatingPersonal = false;
                    vm.profile.personal_details = false;
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
                        html: 'There was an error updating your personal details.<br/>' + error_msg,
                        type: 'error'
                    })
                });
            }
        },
        updateContact: function() {
            let vm = this;
            vm.updatingContact = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_contact')),JSON.stringify(vm.profile),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingContact = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                swal({
                    title: 'Update Contact Details',
                    html: 'Your contact details has been successfully updated.',
                    type: 'success',
                })
                if (vm.completedProfile) {
                    vm.$http.get(api_endpoints.user_profile_completed).then((response) => {
                    },(error) => {
                    })
                }
            }, (error) => {
                vm.updatingContact = false;
                vm.profile.contact_details = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    error_msg += key + ': ' + error.body[key] + '<br/>';
                }
                swal({
                    title: 'Update Contact Details',
                    html: 'There was an error updating your contact details.<br/>' + error_msg,
                    type: 'error'
                })
            });
        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_address')),JSON.stringify(vm.profile.residential_address),{
                emulateJSON:true
            }).then((response) => {
                vm.updatingAddress = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                swal({
                    title: 'Update Address Details',
                    html: 'Your address details has been successfully updated.',
                    type: 'success',
                })
            }, (error) => {
                vm.updatingAddress = false;
                vm.profile.address_details = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    error_msg += key + ': ' + error.body[key] + '<br/>';
                }
                swal({
                    title: 'Update Address Details',
                    html: 'There was an error updating your address details.<br/>' + error_msg,
                    type: 'error'
                })
                if (vm.completedProfile) {
                    vm.$http.get(api_endpoints.user_profile_completed).then((response) => {
                    },(error) => {
                    })
                }
            });
        },
        checkOrganisation: function() {
            console.log('Entered CheckOrg')
            let vm = this;
            let new_organisation = vm.newOrg;
            for (var organisation in vm.profile.wildlifecompliance_organisations) {
                if (new_organisation.abn && vm.profile.wildlifecompliance_organisations[organisation].abn == new_organisation.abn) {
                    swal({
                        title: 'Checking Organisation',
                        html: 'You are already associated with this organisation.',
                        type: 'info'
                    })
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    return;
                }
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,'existance'),JSON.stringify(this.newOrg),{
                emulateJSON:true
            }).then((response) => {
                this.newOrg.exists = response.body.exists;
                this.newOrg.id = response.body.id;
                this.newOrg.detailsChecked = false;
                if (response.body.first_five) {
                  this.newOrg.first_five = response.body.first_five;
                  this.newOrg.detailsChecked = true;
                }
                this.newOrg.detailsChecked = this.newOrg.exists ? this.newOrg.detailsChecked : true;
            }, (error) => {
                this.newOrg.detailsChecked = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    if (key==='non_field_errors'){
                        error_msg += error.body[key] + '<br/>';
                    } else {
                        error_msg += key + ': ' + error.body[key] + '<br/>';
                    }
                }
                swal({
                    title: 'Checking Organisation',
                    html: 'There was an error checking this organisation.<br/>' + error_msg,
                    type: 'error'
                })
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
                        'The pins you entered have been validated and your request will be processed by Organisation Administrator.',
                        'success'
                    )
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    Vue.http.get(api_endpoints.profile).then((response) => {
                        vm.profile = response.body
                        if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                        if ( vm.profile.wildlifecompliance_organisations && vm.profile.wildlifecompliance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                    },(error) => {
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
            });
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
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/upload_id')),data,{
                    emulateJSON:true
                }).then((response) => {
                    vm.uploadingID = false;
                    vm.uploadedID = null;
                    swal({
                        title: 'Upload ID',
                        html: 'Your ID has been successfully uploaded.',
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
                        html: 'There was an error uploading your ID.<br/>' + error_msg,
                        type: 'error'
                    });
                });
            }
        },
        orgRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData();
            data.append('name', vm.newOrg.name);
            data.append('abn', vm.newOrg.abn);
            data.append('identification', vm.uploadedFile);
            data.append('role',vm.role);
            vm.newOrg.name = vm.newOrg.name == null ? '' : vm.newOrg.name
            vm.newOrg.abn = vm.newOrg.abn == null ? '' : vm.newOrg.abn
            if (vm.newOrg.name == '' || vm.newOrg.abn == '' || vm.uploadedFile == null){
                vm.registeringOrg = false;
                swal(
                    'Error submitting organisation request',
                    'Please enter the organisation details and attach a file before submitting your request.',
                    'error'
                )
            } else {
                vm.$http.post(api_endpoints.organisation_requests,data,{
                    emulateJSON:true
                }).then((response) => {
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    swal({
                        title: 'Sent',
                        html: 'Your organisation request has been successfully submitted.',
                        type: 'success',
                    }).then(() => {
                        if (this.$route.name == 'account'){
                           window.location.reload(true);
                        }
                    });
                }, (error) => {
                    vm.registeringOrg = false;
                    let error_msg = '<br/>';
                    for (var key in error.body) {
                        if (key==='non_field_errors'){
                            error_msg += error.body[key] + '<br/>';
                        } else {
                            error_msg += key + ': ' + error.body[key] + '<br/>';
                        }
                    }
                    swal(
                        'Error submitting organisation request',
                        error_msg,
                        'error'
                    );
                });
            }
        },
        orgConsultRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData();
            let new_organisation = vm.newOrg;
            for (var organisation in vm.profile.wildlifecompliance_organisations) {
                if (new_organisation.abn && vm.profile.wildlifecompliance_organisations[organisation].abn == new_organisation.abn) {
                    swal({
                        title: 'Checking Organisation',
                        html: 'You are already associated with this organisation.',
                        type: 'info'
                    })
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    return;
                }
            }
            data.append('name', vm.newOrg.name);
            data.append('abn', vm.newOrg.abn);
            data.append('identification', vm.uploadedFile);
            data.append('role',vm.role);
            vm.newOrg.name = vm.newOrg.name == null ? '' : vm.newOrg.name
            vm.newOrg.abn = vm.newOrg.abn == null ? '' : vm.newOrg.abn
            if (vm.newOrg.name == '' || vm.newOrg.abn == '' || vm.uploadedFile == null){
                vm.registeringOrg = false;
                swal(
                    'Error submitting organisation request',
                    'Please enter the organisation details and attach a file before submitting your request.',
                    'error'
                )
            } else {
                vm.$http.post(api_endpoints.organisation_requests,data,{
                    emulateJSON:true
                }).then((response) => {
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    swal({
                        title: 'Sent',
                        html: 'Your organisation request has been successfully submitted.',
                        type: 'success',
                    }).then(() => {
                        if (this.$route.name == 'account'){
                           window.location.reload(true);
                        }
                    });
                }, (error) => {
                    vm.registeringOrg = false;
                    let error_msg = '<br/>';
                    for (var key in error.body) {
                        if (key==='non_field_errors'){
                            error_msg += error.body[key] + '<br/>';
                        } else {
                            error_msg += key + ': ' + error.body[key] + '<br/>';
                        }
                    }
                    swal(
                        'Error submitting organisation request',
                        error_msg,
                        'error'
                    );
                });
            }
        },
        uploadNewFileUpdateOrgRequest: function(orgReq) {
            let vm = this;
            vm.readFile();
            let data = new FormData();
            data.append('identification', vm.uploadedFile);
            vm.$http.put(helpers.add_endpoint_json(api_endpoints.organisation_requests,orgReq.id+'/reupload_identification_amendment_request'),data,{
                emulateJSON:true
            }).then((response) => {
                vm.uploadedFile = null;
                vm.resetNewOrg();
                swal({
                    title: 'Sent',
                    html: 'Your organisation request has been successfully submitted.',
                    type: 'success',
                }).then(() => {
                    window.location.reload(true);
                });
            }, (error) => {
                console.log(error);
                vm.registeringOrg = false;
                let error_msg = '<br/>';
                for (var key in error.body) {
                    error_msg += key + ': ' + error.body[key] + '<br/>';
                }
                swal(
                    'Error submitting organisation request',
                    error_msg,
                    'error'
                );
            });
        },
        toggleSection: function (e) {
            let el = e.target;
            let chev = null;
            $(el).on('click', function (event) {
                chev = $(this);
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
                vm.loading.splice('fetching countries',1);
            });
        },
        fetchOrgRequestPending:function (){
            let vm =this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_pending_requests')).then((response)=>{
                vm.orgRequest_pending = response.body;
                vm.loading.splice('fetching pending organisation requests',1);
            },(response)=>{
                vm.loading.splice('fetching pending organisation requests',1);
            });
        },
        fetchOrgRequestAmendmentRequested:function (){
            let vm =this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_amendment_requested_requests')).then((response)=>{
                vm.orgRequest_amendment_requested = response.body;
                vm.loading.splice('fetching amendment requested organisation requests',1);
            },(response)=>{
                vm.loading.splice('fetching amendment requested organisation requests',1);
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
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),JSON.stringify(vm.profile),{
                        emulateJSON:true
                    }).then((response) => {
                        Vue.http.get(api_endpoints.profile).then((response) => {
                            vm.profile = response.body
                            if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                            if ( vm.profile.wildlifecompliance_organisations && vm.profile.wildlifecompliance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                        },(error) => {
                        })
                        swal(
                            'Unlink',
                            'You have been successfully unlinked from '+org_name+'.',
                            'success'
                        )
                    }, (error) => {
                        let error_msg = '<br/>';
                        for (var key in error.body) {
                          if (error.body[key].indexOf('last_admin')>-1) {
                            error_msg += 'The Organisation will have no Administrator.<br/>';
                          }
                        }
                        swal(
                            'Unlink',
                            'There was an error unlinking you from '+org_name+'.' + error_msg,
                            'error'
                        )
                    });
                }
            },(error) => {
            }); 
        },
        userProfileCompleted: function(){
            let vm = this;
            vm.$http.get(api_endpoints.user_profile_completed).then((response) => {
                window.location.href='/';
            },(error) => {
            })
        },
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
                    if ( vm.profile.wildlifecompliance_organisations && vm.profile.wildlifecompliance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                });
            }
        },(error) => {
        })
    },
    mounted: function(){
        this.fetchCountries();
        this.fetchOrgRequestPending();
        this.fetchOrgRequestAmendmentRequested();
        this.personal_form = document.forms.personal_form;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        });
        Vue.http.get(api_endpoints.is_new_user).then((response) => {
            this.new_user = response.body;
        })
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
