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
                          <p v-if="a.amendment_request_documents">Documents:<p v-for="d in a.amendment_request_documents"><a :href="d._file" target="_blank" class="control-label pull-left">{{d.name   }}</a><br></p></p>
                          <p>Details: <p v-for="t in splitText(a.text)">{{t}}</p></p>  
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!--
            <label for="region-label">Region(*)</label>
            <input type="text" name="region-text"class="form-control" disabled="true">
            -->

            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>

<!--             <NewApply v-if="proposal" :proposal="proposal"></NewApply>
 -->            <Proposal v-if="proposal" :proposal="proposal" id="proposalStart" :showSections="sectionShow">
                  <NewApply v-if="proposal" :proposal="proposal"></NewApply>

                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                <input type='hidden' name="proposal_id" :value="1" />
                <div class="row" style="margin-bottom: 50px">
                  <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                  <div class="navbar-inner">
                    <div v-if="!proposal.readonly" class="container">
                      <p class="pull-right" style="margin-top:5px;">
                        <!-- <input type="submit" class="btn btn-primary" value="Save and Exit"/> -->
                        <button id="sectionHide" @click.prevent="sectionHide" class="btn btn-primary">Show/Hide sections</button>
                        <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                        <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>

                        <input v-if="!isSubmitting" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                        <button v-else disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                        <!-- <input type="submit" class="btn btn-primary" value="Submit"/> -->

                        <!-- hidden 'save_and_continue_btn' used to allow File (file.vue component) to trigger save -->
                        <input id="save_and_continue_btn" type="hidden" @click.prevent="save_wo_confirm" class="btn btn-primary" value="Save Without Confirmation"/>
                        
                      </p>
                    </div>
                    <div v-else class="container">
                      <p class="pull-right" style="margin-top:5px;">
                        <button id="sectionHide" @click.prevent="sectionHide" class="btn btn-primary">Show/Hide sections</button>

                        <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                      </p>
                    </div>
                  </div>
                  </div>  
                </div>
            </Proposal>           
        </form>
    </div>
</template>
<script>
import Proposal from '../form.vue'
import NewApply from './proposal_apply_new.vue'
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
      submittingProposal: false,
      newText: "",
      pBody: 'pBody',
      missing_fields: [],
      sectionShow: true,
    }
  },
  components: {
      Proposal,
      NewApply,
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    isSubmitting: function() {
      return this.submittingProposal;
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

    sectionHide: function(e) {
      let vm = this;
      vm.sectionShow=!vm.sectionShow
      //console.log(vm.sectionShow);
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
                var id = 'id_' + this.className
                if ($("[class="+this.className+"]:checked").length == 0) {
                    try { var text = $('#'+id).text() } catch(error) { var text = $('#'+id).textContent }
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
    highlight_deficient_fields: function(deficient_fields){
      let vm = this;
      for (var deficient_field of deficient_fields) {
        $("#" + "id_"+deficient_field).css("color", 'red');
      }
    },
    deficientFields(){
      let vm=this;
      //console.log("I am here");
      let deficient_fields=[]
      $('.deficiency').each((i,d) => {
        if($(d).val() != ''){
          var name=$(d)[0].name
          var tmp=name.replace("-comment-field","")
          deficient_fields.push(tmp);
          //console.log('data', $("#"+"id_" + tmp))
        }
      }); 
      //console.log('deficient fields', deficient_fields);
      vm.highlight_deficient_fields(deficient_fields);
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
          vm.submittingProposal = true;
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
        //vm.submittingProposal= false;
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
    // this.$nextTick(() => {
    //   console.log("I am here1");
    //         if(vm.hasAmendmentRequest){
    //           console.log("I am here2");
    //             vm.deficientFields();
    //         }
    //     });
  },
  updated: function(){
    let vm=this;
      this.$nextTick(() => {
            if(vm.hasAmendmentRequest){
                vm.deficientFields();
            }
        });
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

<style lang="css">
</style>
