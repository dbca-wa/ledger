<template lang="html">
    <div class="container" >
        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
            <div v-if="!proposal_readonly">
              <div v-if="hasAmendmentRequest" class="row" style="color:red;">
                  <div class="col-lg-12 pull-right">
                    <div class="panel panel-default">
                      <div class="panel-heading">
                        <h3 class="panel-title" style="color:red;">An amendment has been requested for this Application
                          <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                          </a>
                        </h3>
                      </div>
                      <div class="panel-body collapse in" :id="pBody">
                        <div v-for="a in amendment_request">
                          <p>Reason: {{a.reason}}</p>
                          <p>Details: <p v-for="t in splitText(a.text)">{{t}}</p></p>  
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>

            <div v-if="proposal" id="scrollspy-heading" class="col-lg-12" >
                <h4>Commercial Operator - {{proposal.application_type}} application: {{proposal.lodgement_number}}</h4>
            </div>

            <ProposalTClass v-if="proposal && proposal.application_type=='T Class'" :proposal="proposal" id="proposalStart"  :canEditActivities="canEditActivities" :is_external="true" ref="proposal_tclass"></ProposalTClass>
            <ProposalFilming v-else-if="proposal && proposal.application_type=='Filming'" :proposal="proposal" id="proposalStart"></ProposalFilming>
            <ProposalEvent v-else-if="proposal && proposal.application_type=='Event'" :proposal="proposal" id="proposalStart"></ProposalEvent>

            <div>
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                <input type='hidden' name="proposal_id" :value="1" />

                <div class="row" style="margin-bottom: 50px">
                        <div  class="container">
                          <div class="row" style="margin-bottom: 50px">
                              <div class="navbar navbar-fixed-bottom"  style="background-color: #f5f5f5;">
                                  <div class="navbar-inner">
                                    <div v-if="proposal && !proposal.readonly" class="container">
                                      <p class="pull-right" style="margin-top:5px">
                                        <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                                        <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                        <input type="button" @click.prevent="submit" class="btn btn-primary" :value="submit_text()"/>
                                        <!--<input type="button" @click.prevent="submit" class="btn btn-primary" :value="submit_text()" :disabled="!proposal.training_completed"/>-->
                                        <input id="save_and_continue_btn" type="hidden" @click.prevent="save_wo_confirm" class="btn btn-primary" value="Save Without Confirmation"/>
                                      </p>
                                    </div>
                                    <div v-else class="container">
                                      <p class="pull-right" style="margin-top:5px;">
                                        <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                                      </p>
                                    </div>
                                  </div>
                                </div>
                            </div>
                        </div>
                        <!-- <div v-else class="container">
                          <p class="pull-right" style="margin-top:5px;">
                            <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                          </p>
                        </div> -->
                </div>
            </div>

        </form>
    </div>
</template>
<script>
//import Proposal from '../form.vue'

import ProposalTClass from '../form_tclass.vue'
import ProposalFilming from '../form_filming.vue'
import ProposalEvent from '../form_event.vue'
import Vue from 'vue' 
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'ExternalProposal',
  data: function() {
    return {
      "proposal": null,
      "loading": [],
      form: null,
      amendment_request: [],
      //isDataSaved: false,
      proposal_readonly: true,
      hasAmendmentRequest: false,
      submitting: false,
      newText: "",
      pBody: 'pBody',
      missing_fields: [],
    }
  },
  components: {
      ProposalTClass,
      ProposalFilming,
      ProposalEvent
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
    proposal_form_url: function() {
      return (this.proposal) ? `/api/proposal/${this.proposal.id}/draft.json` : '';
    },
    application_fee_url: function() {
      return (this.proposal) ? `/application_fee/${this.proposal.id}/` : '';
    },
    proposal_submit_url: function() {
      return (this.proposal) ? `/api/proposal/${this.proposal.id}/submit.json` : '';
      //return this.submit();
    },
    canEditActivities: function(){
      return this.proposal ? this.proposal.can_user_edit: 'false';
    }

  },
  methods: {
    submit_text: function() {
      let vm = this;
      return vm.proposal.fee_paid ? 'Resubmit' : 'Pay and Submit';
    },
    save_applicant_data:function(){
      let vm=this;
      if(vm.proposal.applicant_type == 'SUB')
      {
        vm.$refs.proposal_tclass.$refs.profile.updatePersonal();
        vm.$refs.proposal_tclass.$refs.profile.updateAddress();
        vm.$refs.proposal_tclass.$refs.profile.updateContact();
      }
      if(vm.proposal.applicant_type == 'ORG'){
        vm.$refs.proposal_tclass.$refs.organisation.updateDetails();
        vm.$refs.proposal_tclass.$refs.organisation.updateAddress();
      }
    },
    set_formData: function(e) {
      let vm = this;
      //vm.form=document.forms.new_proposal;
      let formData = new FormData(vm.form);

      //console.log('land activities', vm.proposal.selected_parks_activities);
      formData.append('selected_parks_activities', JSON.stringify(vm.proposal.selected_parks_activities))
      formData.append('selected_trails_activities', JSON.stringify(vm.proposal.selected_trails_activities))
      formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))

      return formData;
    },
    save: function(e) {
      let vm = this;
      //vm.form=document.forms.new_proposal;
      vm.save_applicant_data();
      //await vm.save_applicant_data();

      let formData = vm.set_formData()
      //vm.save_applicant_data();

//      let formData = new FormData(vm.form);
      //console.log('land activities', vm.proposal.selected_parks_activities);
//      formData.append('selected_parks_activities', JSON.stringify(vm.proposal.selected_parks_activities))
//      formData.append('selected_trails_activities', JSON.stringify(vm.proposal.selected_trails_activities))
//      formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))

      vm.$http.post(vm.proposal_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your application has been saved',
            'success'
          );
      },err=>{
      });
    },
    save_exit: function(e) {
      let vm = this;
      this.submitting = true;
      this.save(e);

      // redirect back to dashboard
      vm.$router.push({
        name: 'external-proposals-dash'
      });
    },

    save_wo_confirm: function(e) {
      let vm = this;
      vm.save_applicant_data();
      let formData = vm.set_formData()
      //vm.save_applicant_data();

//      let formData = new FormData(vm.form);
//      formData.append('selected_parks_activities', JSON.stringify(vm.proposal.selected_parks_activities))
//      formData.append('selected_trails_activities', JSON.stringify(vm.proposal.selected_trails_activities))
//      formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))
      vm.$http.post(vm.proposal_form_url,formData);
    },

    save_and_redirect: function(e) {
      let vm = this;
      let formData = vm.set_formData()

//      let formData = new FormData(vm.form);
//      formData.append('selected_parks_activities', JSON.stringify(vm.proposal.selected_parks_activities))
//      formData.append('selected_trails_activities', JSON.stringify(vm.proposal.selected_trails_activities))
//      formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))
      vm.save_applicant_data();
      vm.$http.post(vm.proposal_form_url,formData).then(res=>{
          /* after the above save, redirect to the Django post() method in ApplicationFeeView */
          vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
      },err=>{
      });
    },

    setdata: function(readonly){
      this.proposal_readonly = readonly;
    },

    setAmendmentData: function(amendment_request){
      this.amendment_request = amendment_request;
      
      if (amendment_request.length > 0)
        this.hasAmendmentRequest = true;
        
    },

    splitText: function(aText){
      let newText = '';
      newText = aText.split("\n");
      return newText;

    },

    leaving: function(e) {
      let vm = this;
      var dialogText = 'You have some unsaved changes.';
      if (!vm.proposal_readonly && !vm.submitting){
        e.returnValue = dialogText;
        return dialogText;
      }
      else{
        return null;
      }
    },
    
    highlight_missing_fields: function(){
        let vm = this;
        for (var missing_field of vm.missing_fields) {
            $("#" + missing_field.id).css("color", 'red');
        }
    },

    validate: function(){
        let vm = this;

        // reset default colour
        for (var field of vm.missing_fields) {
            $("#" + field.id).css("color", '#515151');
        }
        vm.missing_fields = [];

        // get all required fields, that are not hidden in the DOM
        //var hidden_fields = $('input[type=text]:hidden, textarea:hidden, input[type=checkbox]:hidden, input[type=radio]:hidden, input[type=file]:hidden');
        //hidden_fields.prop('required', null);
        //var required_fields = $('select:required').not(':hidden');
        var required_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required').not(':hidden');

        // loop through all (non-hidden) required fields, and check data has been entered
        required_fields.each(function() {
            //console.log('type: ' + this.type + ' ' + this.name)
            var id = 'id_' + this.name
            if (this.type == 'radio') {
                //if (this.type == 'radio' && !$("input[name="+this.name+"]").is(':checked')) {
                if (!$("input[name="+this.name+"]").is(':checked')) {
                    var text = $('#'+id).text()
                    console.log('radio not checked: ' + this.type + ' ' + text)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'checkbox') {
                //if (this.type == 'radio' && !$("input[name="+this.name+"]").is(':checked')) {
                var id = 'id_' + this.classList['value']
                if ($("[class="+this.classList['value']+"]:checked").length == 0) {
                    var text = $('#'+id).text()
                    console.log('checkbox not checked: ' + this.type + ' ' + text)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'select-one') {
                if ($(this).val() == '') {
                    var text = $('#'+id).text()  // this is the (question) label
                    var id = 'id_' + $(this).prop('name'); // the label id
                    console.log('selector not selected: ' + this.type + ' ' + text)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'file') {
                var num_files = $('#'+id).attr('num_files')
                if (num_files == "0") {
                    var text = $('#'+id).text()
                    console.log('file not uploaded: ' + this.type + ' ' + this.name)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'text') {
                if (this.value == '') {
                    var text = $('#'+id).text()
                    console.log('text not provided: ' + this.type + ' ' + this.name)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'textarea') {
                if (this.value == '') {
                    var text = $('#'+id).text()
                    console.log('textarea not provided: ' + this.type + ' ' + this.name)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            /*
            if (this.type == 'select') {
                if (this.value == '') {
                    var text = $('#'+id).text()
                    console.log('select not provided: ' + this.type + ' ' + this.name)
                    vm.missing_fields.push({id: id, label: text});
                }
            }

            if (this.type == 'multi-select') {
                if (this.value == '') {
                    var text = $('#'+id).text()
                    console.log('multi-select not provided: ' + this.type + ' ' + this.name)
                    vm.missing_fields.push({id: id, label: text});
                }
            }
            */



        });

        return vm.missing_fields.length
    },

    can_submit: function(){
      let vm=this;
      let blank_fields=[]
      this.proposal.other_details.accreditation_type

      if (vm.$refs.proposal_tclass.$refs.other_details.selected_accreditations.length==0 ){
        blank_fields.push(' Level of Accreditation is required')
      }

      if (vm.proposal.other_details.preferred_licence_period=='' || vm.proposal.other_details.preferred_licence_period==null ){
        blank_fields.push(' Preferred Licence Period is required')
      }
      if (vm.proposal.other_details.nominated_start_date=='' || vm.proposal.other_details.nominated_start_date==null ){
        blank_fields.push(' Licence Nominated Start Date is required')
      }

      if(vm.$refs.proposal_tclass.$refs.other_details.$refs.deed_poll_doc.documents.length==0){
        blank_fields.push(' Deed poll document is missing')
      }

      if(vm.$refs.proposal_tclass.$refs.other_details.$refs.currency_doc.documents.length==0){
        blank_fields.push(' Certificate of currency document is missing')
      }
      if(vm.proposal.other_details.insurance_expiry=='' || vm.proposal.other_details.insurance_expiry==null){
        blank_fields.push(' Certificate of currency expiry date is missing')
      }

      if(blank_fields.length==0){
        return true;
      }
      else{
        return blank_fields;
      }

    },
    submit: function(){
        let vm = this;
        let formData = vm.set_formData()

/*
*/
        var missing_data= vm.can_submit();
        if(missing_data!=true){
          swal({
            title: "Please fix following errors before submitting",
            text: missing_data,
            type:'error'
          })
          return false;
        }

        // remove the confirm prompt when navigating away from window (on button 'Submit' click)
        vm.submitting = true;

        swal({
            title: vm.submit_text() + " Application",
            text: "Are you sure you want to " + vm.submit_text().toLowerCase()+ " this application?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: vm.submit_text()
        }).then(() => {
            if (!vm.proposal.fee_paid) {
                vm.save_and_redirect();

            } else {
                /* just save and submit - no payment required (probably application was pushed back by assessor for amendment */
                vm.save_wo_confirm()
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData).then(res=>{
                    vm.proposal = res.body;
                    vm.$router.push({
                        name: 'submit_proposal',
                        params: { proposal: vm.proposal}
                    });
                },err=>{
                    swal(
                        'Submit Error',
                        helpers.apiVueResourceError(err),
                        'error'
                    )
                });
            }
        },(error) => {
        });
    },

   _submit: function(){
        let vm = this;
        let formData = new FormData(vm.form);
        formData.append('selected_parks_activities', JSON.stringify(vm.proposal.selected_parks_activities))
        //formData.append('selected_land_access', JSON.stringify(vm.proposal.selected_land_access))
        //formData.append('selected_land_activities', JSON.stringify(vm.proposal.selected_land_activities))
        formData.append('selected_trails_activities', JSON.stringify(vm.proposal.selected_trails_activities))
        formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))

              vm.proposal.selected_access=vm.selected_access;
              vm.proposal.selected_activities=vm.selected_activities;

        var num_missing_fields = vm.validate()
        if (num_missing_fields > 0) {
            vm.highlight_missing_fields()
            var top = ($('#error').offset() || { "top": NaN }).top;
            $('html, body').animate({
                scrollTop: top
            }, 1);
            return false;
        }

        // remove the confirm prompt when navigating away from window (on button 'Submit' click)
        vm.submitting = true;

        swal({
            title: "Submit Application",
            text: "Are you sure you want to submit this proposal?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then(() => {
            //vm.$http.post(vm.application_fee_url, formData)
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData).then(res=>{
            //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposal_submit,vm.proposal.id+'/submit'),formData).then(res=>{
                vm.proposal = res.body;
                vm.$http.post(vm.application_fee_url, formData)
                //location.href="/external/"
                //location.href = vm.application_fee_url;
                //vm.$router.push({
                //    name: 'submit_proposal',
                //    params: { proposal: vm.proposal}
                //});
            //}.then(res=>{
            //    vm.$http.post(vm.application_fee_url, formData)
            },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
        },(error) => {
        });
    },

    post_and_redirect: function(url, postData) {
        /* http.post and ajax do not allow redirect from Django View (post method), 
           this function allows redirect by mimicking a form submit.

           usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
        */
        var postFormStr = "<form method='POST' action='" + url + "'>";

        for (var key in postData) {
            if (postData.hasOwnProperty(key)) {
                postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
            }
        }
        postFormStr += "</form>";
        var formElement = $(postFormStr);
        $('body').append(formElement);
        $(formElement).submit();
    },

  },

  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_proposal;
    window.addEventListener('beforeunload', vm.leaving);
    window.addEventListener('onblur', vm.leaving);
  },
  

  beforeRouteEnter: function(to, from, next) {
    if (to.params.proposal_id) {
      let vm = this;
      Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
          next(vm => {
            vm.loading.push('fetching proposal')
            vm.proposal = res.body;
            //used in activities_land for T Class licence
            vm.proposal.selected_trails_activities=[];
            vm.proposal.selected_parks_activities=[];
            vm.proposal.marine_parks_activities=[];
            vm.loading.splice('fetching proposal', 1);
            vm.setdata(vm.proposal.readonly);
          
            
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.proposals,to.params.proposal_id+'/amendment_request')).then((res) => {
                     
                      vm.setAmendmentData(res.body);
                  
                },
              err => { 
                        console.log(err);
                  });
              });
          },
        err => {
          console.log(err);
        });    
    }
    else {
      Vue.http.post('/api/proposal.json').then(res => {
          next(vm => {
            vm.loading.push('fetching proposal')
            vm.proposal = res.body;
            vm.loading.splice('fetching proposal', 1);
          });
        },
        err => {
          console.log(err);
        });
    }
  }
}
</script>

<style lang="css" scoped>
</style>
