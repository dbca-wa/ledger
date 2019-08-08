<template lang="html">
    <div class="row">
        <div class="col-sm-12">
            <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Applicant
                                        <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="detailsBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3> 
                                </div>
                                <div v-if="applicantType == 'ORG'" class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Name</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.org_applicant.name" style="width: 100%">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Trading Name</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.org_applicant.trading_name" style="width: 100%">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="proposal.org_applicant.abn" style="width: 100%">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                                <div v-if="applicantType == 'SUB'" class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.submitter.first_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Surname</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.submitter.last_name">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Address Details
                                        <a class="panelClicker" :href="'#'+addressBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="addressBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3> 
                                </div>
                                <div v-if="applicantType == 'ORG' && proposal.org_applicant.address" class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="proposal.org_applicant.address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="proposal.org_applicant.address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="proposal.org_applicant.address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="proposal.org_applicant.address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="proposal.org_applicant.address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                                <div v-if="applicantType == 'SUB' && proposal.submitter.residential_address" class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="proposal.submitter.residential_address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="proposal.submitter.residential_address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="proposal.submitter.residential_address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="proposal.submitter.residential_address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="proposal.submitter.residential_address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Contact Details
                                        <a class="panelClicker" :href="'#'+contactsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="contactsBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div v-if="applicantType == 'ORG'" class="panel-body panel-collapse collapse" :id="contactsBody">
                                    <table ref="contacts_datatable" :id="contacts_table_id" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                                    </table>
                                </div>
                                <div v-if="applicantType == 'SUB'" class="panel-body panel-collapse collapse" :id="contactsBody">
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantPhoneNumber" placeholder="" v-model="proposal.submitter.phone_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantMobileNumber" placeholder="" v-model="proposal.submitter.mobile_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Email</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantEmail" placeholder="" v-model="proposal.submitter.email">
                                        </div>
                                      </div>
                                  </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
        <!-- <Assessment :proposal="proposal" :assessment="proposal.assessor_assessment" :hasAssessorMode="hasAssessorMode" :is_internal="is_internal" :is_referral="is_referral"></Assessment> -->
    </div>
</template>

<script>
import Assessment from './assessment.vue'
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            let vm=this;
            return{
                values:null,
                detailsBody: 'detailsBody'+vm._uid,
                addressBody: 'addressBody'+vm._uid,
                contactsBody: 'contactsBody'+vm._uid,
                panelClickersInitialised: false,
                contacts_table_id: vm._uid+'contacts-table',
                contacts_table_initialised: false,
                contacts_options:{
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    ajax: {
                        "url": vm.contactsURL,
                        "dataSrc": ''
                    },
                    columns: [
                        {
                            title: 'Name',
                            mRender:function (data,type,full) {
                                return full.first_name + " " + full.last_name;
                            }
                        },
                        {
                            title: 'Phone',
                            data:'phone_number'
                        },
                        {
                            title: 'Mobile',
                            data:'mobile_number'
                        },
                        {
                            title: 'Fax',
                            data:'fax_number'
                        },
                        {
                            title: 'Email',
                            data:'email'
                        },
                      ],
                      processing: true
                },
                contacts_table: null,
            }
        },
        components: {
          Assessment
        },
        computed:{
        contactsURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.proposal.org_applicant.id+'/contacts') : '';
        },
        applicantType: function(){
            return this.proposal.applicant_type;
        },
        // hasAssessorMode:function(){
        //     return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
        // },
        },
        methods:{
            initialiseOrgContactTable: function(){
                let vm = this;
                //console.log("i am here")
                if (vm.proposal && !vm.contacts_table_initialised){
                    vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.proposal.org_applicant.id+'/contacts');
                    vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                    vm.contacts_table_initialised = true;
                }
            },
        },
        mounted: function(){
            let vm=this;
            if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            }); 
            vm.panelClickersInitialised = true;
            }
            this.$nextTick(() => {
                vm.initialiseOrgContactTable();
                
            });
        }
    }
</script>

<style lang="css" scoped>
</style>

