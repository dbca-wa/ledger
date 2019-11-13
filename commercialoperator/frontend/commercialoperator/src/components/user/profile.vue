<template>
    <div :class="classCompute" id="userInfo">
      <div class="col-sm-12">
        <div v-if="showCompletion" class="row">
            <div class="col-sm-12">
                <div class="well well-sm">
                    <div class="row">
                        <div class="col-sm-12">
                            <p>
                                We have detected that this is the first time you have logged into the system.Please take a moment to provide us with your details
                                (personal details, address details, contact details, and whether you are managing licences for an organisation).
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
                        <alert v-if="showPersonalError" type="danger" style="color:red"><div v-for="item in errorListPersonal"><strong>{{item}}</strong></div></alert>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Given name(s)</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" id="first_name" name="Given name" placeholder="" v-model="profile.first_name" required="">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Surname</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" id="surname" name="Surname" placeholder="" v-model="profile.last_name">
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
<!-- 
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
                                output order in reverse due to pull-right at runtime -->
                                <!---<button v-if="!uploadingID" class="pull-right btn btn-primary" @click.prevent="uploadID()">Upload</button>
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
        </div> -->

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
                        <alert v-if="showAddressError" type="danger" style="color:red"><div v-for="item in errorListAddress"><strong>{{item}}</strong></div></alert>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Street</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" id="line1" name="Street" placeholder="" v-model="profile.residential_address.line1">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" id="locality" name="Town/Suburb" placeholder="" v-model="profile.residential_address.locality">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">State</label>
                            <div class="col-sm-3">
                                <input type="text" class="form-control" id="state" name="State" placeholder="" v-model="profile.residential_address.state">
                            </div>
                            <label for="" class="col-sm-1 control-label">Postcode</label>
                            <div class="col-sm-2">
                                <input type="text" class="form-control" id="postcode" name="Postcode" placeholder="" v-model="profile.residential_address.postcode">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Country</label>
                            <div class="col-sm-4">
                                <select class="form-control" id="country" name="Country" v-model="profile.residential_address.country">
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
                        <alert v-if="showContactError" type="danger" style="color:red"><div v-for="item in errorListContact"><strong>{{item}}</strong></div></alert>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Phone (work)</label>
                            <div v-if="profile.is_department_user" class="col-sm-6">
                               <input readonly="readonly" type="text" class="form-control" id="phone" name="Phone" placeholder="" v-model="profile.phone_number">           
                            </div>
                            <div v-else class="col-sm-6">
                                <input type="text" class="form-control" id="phone" name="Phone" placeholder="" v-model="profile.phone_number">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Mobile</label>
                            <div v-if="profile.is_department_user" class="col-sm-6">
                                <input readonly="readonly" type="text" class="form-control" id="mobile" name="Mobile" placeholder="" v-model="profile.mobile_number">
                            </div>
                            <div v-else class="col-sm-6">
                                <input type="text" class="form-control" id="mobile" name="Mobile" placeholder="" v-model="profile.mobile_number">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Email</label>
                            <div class="col-sm-6">
                                <input type="email" class="form-control" id="email" name="Email" placeholder="" v-model="profile.email">
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
        <div v-if="!isApplication" class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Organisation <small>Link to the organisations you are an employee of and for which you are managing licences</small>
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse" :id="oBody">
                      <form class="form-horizontal" name="orgForm" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-5 control-label">Do you manage licences on behalf of an organisation? <i class="fa fa-question-circle" data-toggle="tooltip" data-placement="bottom" style="color:blue" title="Answer with Yes if you are applying for a licence in an organisation or incorporated body name.">&nbsp;</i></label>
                            <div class="col-sm-4">
                                <label class="radio-inline">
                                  <input type="radio" name="behalf_of_org" v-model="managesOrg" value="Yes"> Yes
                                </label>
                                <label class="radio-inline">
                                  <input :disabled="hasOrgs" type="radio" name="behalf_of_org" v-model="managesOrg" value="No" > No
                                </label>
                                <label class="radio-inline">
                                  <input type="radio" name="behalf_of_org" v-model="managesOrg" value="Consultant"> Yes, as a consultant
                                </label>
                            </div>
                          </div>
                          <div class="form-group" v-if="managesOrg=='Yes'">
                            <div class="col-sm-12">
                                <button class="btn btn-primary pull-right" v-if="hasOrgs && !addingCompany" @click.prevent="addCompany()">Add Another Organisation</button>   
                            </div>
                          </div>

                          <div v-for="org in profile.commercialoperator_organisations">
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

                           <div v-if="managesOrg=='Consultant'">
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
                                      <!--<button @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>-->
                                      <button v-if="newOrg.detailsChecked" @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>
                                  </div>
                              </div>
                              <!--<div class="form-group" v-if="newOrg.detailsChecked">-->
                              <div class="form-group">
                                    <label class="col-sm-12" style="text-align:left;">
                                      Please upload a letter on organisation letter head stating that you are a consultant for the organisation.
                                        <span class="btn btn-info btn-file">
                                            Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
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


                          <div style="margin-top:15px;" v-if="addingCompany">
                              <h3> New Organisation</h3>
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >Organisation</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="organisation" v-model="newOrg.name" placeholder="">
                                </div>
                              </div>
                              <div class="form-group">
                                <label for="" class="col-sm-2 control-label" >ABN/ACN <i class="fa fa-question-circle" data-toggle="tooltip" data-placement="bottom" style="color:blue" title="If you are applying as a sole trader please supply your ABN.">&nbsp;</i></label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="abn" v-model.number="newOrg.abn" placeholder="" style="width: 40%">
                                </div>
                                <div class="col-sm-2">
                                    <button :disabled="!isNewOrgDetails" @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>
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
                                    <button v-if="!completedProfile && !validatingPins" disabled title="Please complete all the personal details." class="btn btn-primary pull-left">Validate</button>

                                    <button v-else-if="!validatingPins && completedProfile" @click.prevent="validatePins()" class="btn btn-primary pull-left">Validate</button>
                                    <button v-else class="btn btn-primary pull-left"><i class="fa fa-spin fa-spinner"></i>&nbsp;Validating Pins</button>
                                  </div>
                              </div>
                              <div class="form-group" v-else-if="!newOrg.exists && newOrg.detailsChecked">
                                  <label class="col-sm-12" style="text-align:left;">
                                    This organisation has not yet been registered with this system. Please upload a letter on organisation head stating that you are an employee of this origanisation.</br>
                                  </label>
                                  <div class="col-sm-12">
                                    <span class="btn btn-primary btn-file pull-left">
                                        Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                    </span>
                                    <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                  </div>
                                  <label for="" class="col-sm-10 control-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.</label>
                                  <div class="col-sm-12">
                                    <button v-if="!completedProfile" disabled title="Please complete details" class="btn btn-primary pull-right">Submit</button>
                                    <button v-else-if="!registeringOrg" :disabled="!isFileUploaded" @click.prevent="orgRequest()" class="btn btn-primary pull-right">Submit</button>
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
    </div>
</template>

<script>
import Vue from 'vue'
import $ from 'jquery'
import { api_endpoints, helpers } from '@/utils/hooks'
export default {
    name: 'Profile',
    props:{
      isApplication:{
                type: Boolean,
                default: false
            },
    },
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
            idBody: 'idBody'+vm._uid,
            profile: {
              first_name: '',
                last_name: '',
                commercialoperator_organisations:[],
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
            uploadedID: null,
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            registeringOrg: false,
            orgRequest_list: [],
            missing_fields: [],
            errorListPersonal:[],
            showPersonalError: false,
            errorListAddress:[],
            showAddressError: false,
            errorListContact:[],
            showContactError: false,
            role : null,
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
            } else {
                this.addCompany()
                this.addingCompany=false
            }
        },
    },
    computed: {
        classCompute:function(){
          return this.isApplication? 'row' : 'container';
        },
        hasOrgs: function() {
            return this.profile.commercialoperator_organisations && this.profile.commercialoperator_organisations.length > 0 ? true: false;
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        uploadedIDFileName: function() {
            return this.uploadedID != null ? this.uploadedID.name: '';
        },
        isFileUploaded: function() {
            return this.uploadedFile != null ? true: false;
        },
        isNewOrgDetails: function() {
            return this.newOrg && this.newOrg.name != '' && this.newOrg.abn != '' ? true: false;
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
        updatePersonal: function() {
            let vm = this;
            //console.log(vm.profile);
            vm.missing_fields = [];
            var required_fields=[];
            vm.errorListPersonal=[];
            required_fields = $('#first_name, #surname')
            vm.missing_fields = [];
            required_fields.each(function() {
            if (this.value == '') {
                    //var text = $('#'+id).text()
                    //console.log(this);
                    vm.errorListPersonal.push('Value not provided: ' + this.name)
                    vm.missing_fields.push({id: this.id});
                }
            });

            if (vm.missing_fields.length > 0)
            {
              vm.showPersonalError = true;
              //console.log(vm.showPersonalError)
            }
            else
            {
              vm.showPersonalError = false;
            vm.updatingPersonal = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
                emulateJSON:true
            }).then((response) => {
                //console.log(response);
                vm.updatingPersonal = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingPersonal = false;
            });
          }
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
        
        updateContact: function() {
            let vm = this;
            vm.missing_fields = [];
            var required_fields=[];
            vm.errorListContact=[];
            required_fields = $('#email')
            vm.missing_fields = [];
            required_fields.each(function() {
            if (this.value == '') {
                    //var text = $('#'+id).text()
                    console.log(this);
                    vm.errorListContact.push('Value not provided: ' + this.name)
                    vm.missing_fields.push({id: this.id});
                }
            });
            if (vm.profile.mobile_number == '' || vm.profile.phone_number ==''){
              vm.errorListContact.push('Value not provided: mobile/ Phone number')
              vm.missing_fields.push({id: $('#mobile').id});
            }
            if (vm.missing_fields.length > 0)
            {
              vm.showContactError = true;
            }
            else{
              vm.showContactError = false;
            vm.updatingContact = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_contact')),JSON.stringify(vm.profile),{
                emulateJSON:true
            }).then((response) => {
                //console.log(response);
                vm.updatingContact = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingContact = false;
            });
          }
        },
        updateAddress: function() {
            let vm = this;

            vm.missing_fields = [];
            var required_fields=[];
            vm.errorListAddress=[];
            required_fields = $('#postcode, #line1, #locality, #country, #state')
            vm.missing_fields = [];
            required_fields.each(function() {
            if (this.value == '') {
                    //var text = $('#'+id).text()
                    vm.errorListAddress.push('Value not provided: ' + this.name)
                    vm.missing_fields.push({id: this.id});
                }
            });

            if (vm.missing_fields.length > 0)
            {
              vm.showAddressError = true;
            }
            else{
              vm.showAddressError = false;
            

            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_address')),JSON.stringify(vm.profile.residential_address),{
                emulateJSON:true
            }).then((response) => {
                //console.log(response);
                vm.updatingAddress = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
          }
        },
        checkOrganisation: function() {
            let vm = this;
            //this.newOrg.abn = this.newOrg.abn.replace(/\s+/g,'');
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,'existance'),JSON.stringify(this.newOrg),{
                emulateJSON:true
            }).then((response) => {
                //console.log(response);
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
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_pending_requests')).then((response) => {
                
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
                        if ( vm.profile.commercialoperator_organisations && vm.profile.commercialoperator_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
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
            let data = new FormData();
            data.append('name', vm.newOrg.name);
            data.append('abn', vm.newOrg.abn);
            data.append('identification', vm.uploadedFile);
            data.append('role',vm.role);
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
            }

        },
        orgConsultRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData();
            let new_organisation = vm.newOrg;
            for (var organisation in vm.profile.commercialoperator_organisations) {
                if (new_organisation.abn && vm.profile.commercialoperator_organisations[organisation].abn == new_organisation.abn) {
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
            }
        },
        toggleSection: function (e) {
            let el = e.target;
            let chev = null;
            //console.log(el);
            $(el).on('click', function (event) {
                chev = $(this);
                //console.log(chev);
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
                //console.log(response);
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
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),JSON.stringify(vm.profile),{
                    emulateJSON:true
                }).then((response) => {
                    Vue.http.get(api_endpoints.profile).then((response) => {
                        vm.profile = response.body
                        if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                        if ( vm.profile.commercialoperator_organisations && vm.profile.commercialoperator_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
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
        },
        fetchProfile: function(){
          let vm=this;
          Vue.http.get(api_endpoints.profile).then((response) => {
                    vm.profile = response.body
                    if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                    if ( vm.profile.commercialoperator_organisations && vm.profile.commercialoperator_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
        },(error) => {
            console.log(error);
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
                    if ( vm.profile.commercialoperator_organisations && vm.profile.commercialoperator_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                });
            }
        },(error) => {
            console.log(error);
        })
    },

    mounted: function(){
        this.fetchCountries();
        this.fetchOrgRequestList();
        this.fetchProfile(); //beforeRouteEnter doesn't work when loading this component in Application.vue so adding an extra method to get profile details.
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
