<template lang="html">
    <div class="container" >
        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
          <div v-if="!proposal_readonly">
            <div v-if="hasAmendmentRequest" class="row" style="color:red;">
                <div class="col-lg-12 pull-right">
                  <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title" style="color:red;">An amendment has been requested for this Proposal
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

			<div id="scrollspy-heading" class="col-lg-12" >
               	<h4>Commercial Operator - {{proposal.application_type}} application: {{proposal.lodgement_number}}</h4>
            </div>

			<div class="col-md-3" >
				<div class="panel panel-default fixed">
				  <div class="panel-heading">
					<h5>Sections</h5>
				  </div>
				  <div class="panel-body" style="padding:0">
					  <ul class="list-group" id="scrollspy-section" style="margin-bottom:0">

					  </ul>
				  </div>
				</div>
			</div>

            <div class="col-md-9">
				<ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
				  <li class="nav-item">
					<a class="nav-link active" id="pills-applicant-tab" data-toggle="pill" href="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
					  1. Applicant
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-activities-land-tab" data-toggle="pill" href="#pills-activities-land" role="tab" aria-controls="pills-activities-land" aria-selected="false">
					  2. Activities (land)
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-activities-marine-tab" data-toggle="pill" href="#pills-activities-marine" role="tab" aria-controls="pills-activities-marine" aria-selected="false">
					  3. Activities (marine)
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-other-details-tab" data-toggle="pill" href="#pills-other-details" role="tab" aria-controls="pills-other-details" aria-selected="false">
					  4. Other Details
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-online-training-tab" data-toggle="pill" href="#pills-online-training" role="tab" aria-controls="pills-online-training" aria-selected="false">
					  5. Online Training
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-payment-tab" data-toggle="pill" href="#pills-payment" role="tab" aria-controls="pills-payment" aria-selected="false">
					  6. Payment
					</a>
				  </li>
				  <li class="nav-item">
					<a class="nav-link" id="pills-confirm-tab" data-toggle="pill" href="#pills-confirm" role="tab" aria-controls="pills-confirm" aria-selected="false">
					  7. Confirmation
					</a>
				  </li>

				</ul>
				<div class="tab-content" id="pills-tabContent">
				  <div class="tab-pane fade show active" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">... Applicant </div>
				  <div class="tab-pane fade" id="pills-activities-land" role="tabpanel" aria-labelledby="pills-activities-land-tab">... Activities Land</div>
				  <div class="tab-pane fade" id="pills-activities-marine" role="tabpanel" aria-labelledby="pills-activities-marine-tab">... Activities Marine</div>
				  <div class="tab-pane fade" id="pills-other-details" role="tabpanel" aria-labelledby="pills-other-details-tab">... Other Details</div>
				  <div class="tab-pane fade" id="pills-online-training" role="tabpanel" aria-labelledby="pills-online-training-tab">... Online Training</div>
				  <div class="tab-pane fade" id="pills-payment" role="tabpanel" aria-labelledby="pills-payment-tab">... Payment</div>
				  <div class="tab-pane fade" id="pills-confirm" role="tabpanel" aria-labelledby="pills-confirm-tab">... Confirmation</div>
				</div>
            </div>


			<!--
            <Proposal v-if="proposal" :proposal="proposal" id="proposalStart">
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                <input type='hidden' name="proposal_id" :value="1" />
                <div class="row" style="margin-bottom: 50px">
                  <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                  <div class="navbar-inner">
                    <div v-if="!proposal.readonly" class="container">
                      <p class="pull-right" style="margin-top:5px;">
                        <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                        <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                        <input type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>

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
            </Proposal>           

			<nav class="nav nav-pills nav-fill">
			  <a class="nav-item nav-link active" href="#">Active</a>
			  <a class="nav-item nav-link" href="#">Link</a>
			  <a class="nav-item nav-link" href="#">Link</a>
			  <a class="nav-item nav-link disabled" href="#">Disabled</a>
			</nav>
			-->

        </form>
    </div>
</template>
<script>
import Proposal from '../form.vue'
import Vue from 'vue' 
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
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
      Proposal
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
    proposal_submit_url: function() {
      return (this.proposal) ? `/api/proposal/${this.proposal.id}/submit.json` : '';
      //return this.submit();
    },

  },
  methods: {
    save: function(e) {
      let vm = this;
      let formData = new FormData(vm.form);
      console.log(formData);
      vm.$http.post(vm.proposal_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your proposal has been saved',
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
      let formData = new FormData(vm.form);
      vm.$http.post(vm.proposal_form_url,formData);
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

        /*
        if (emptyFields === 0) {
            $('#form').submit();
        } else {
            $('#error').show();
            return false;
        }
        */
    },


    submit: function(){
        let vm = this;
        let formData = new FormData(vm.form);

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
            title: "Submit Proposal",
            text: "Are you sure you want to submit this proposal?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then(() => {
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
        },(error) => {
        });
    },

//    _submit: function(){
//        let vm = this;
//
//        swal({
//            title: "Submit Proposal",
//            text: "Are you sure you want to submit this proposal?",
//            type: "question",
//            showCancelButton: true,
//            confirmButtonText: 'Submit'
//        }).then(() => {
//            let formData = new FormData(vm.form);
//            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData).then(res=>{
//                vm.proposal = res.body;
//
//                if ('missing_fields' in vm.proposal) {
//                    var missing_text = '';
//                    for (var i = 0; i < vm.proposal.missing_fields.length; i++) {
//                        missing_text = missing_text + i + ". " + vm.proposal.missing_fields[i].label + '<br>'
//                    }
//                    //vm.proposal.missing_fields.forEach(function(field) {
//                        //missing_text = missing_text + field.label + '<br>'
//                    //});
//                    swal({
//                        title: "Required field(s) are missing",
//                        html: missing_text,
//                        confirmButtonText: 'Submit',
//                        type: 'warning',
//                    }).then(() => {
//                        //vm.form = document.forms.new_proposal;
//                        //vm.$router.go();
//                        this.highlight_missing_fields(vm.proposal.missing_fields);
//                        //this.proposal = vm.proposal;
//
//                        vm.$router.push({
//                            name: 'draft_proposal',
//                            params: { proposal_id:vm.proposal.id}
//                            //params: { proposal: vm.proposal} 
//                        });
//
//                    });
//                } else {
//
//                    vm.$router.push({
//                        name: 'submit_proposal',
//                        params: { proposal: vm.proposal} 
//                    });
//                }
//            },err=>{
//                swal(
//                    'Submit Error',
//                    helpers.apiVueResourceError(err),
//                    'error'
//                )
//            });
//        },(error) => {
//        });
//    }

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
.nav-item {
    background-color: rgb(200,200,200,0.8) !important;
}

.nav-item>li>a {
    background-color: yellow !important;
    color: #fff;
}

.nav-item>li.active>a, .nav-item>li.active>a:hover, .nav-item>li.active>a:focus {
  color: white;
  background-color: blue;
  border: 1px solid #888888;
}
</style>
