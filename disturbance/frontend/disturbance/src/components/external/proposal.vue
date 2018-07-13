<template lang="html">
    <div class="container" >
        <form :action="proposal_submit_url" method="post" name="new_proposal" enctype="multipart/form-data">
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
            <!--
            <label for="region-label">Region(*)</label>
            <input type="text" name="region-text"class="form-control" disabled="true">
            -->        
            <Proposal v-if="proposal" :proposal="proposal" id="proposalStart">
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                <input type='hidden' name="proposal_id" :value="1" />
                <div class="row" style="margin-bottom: 50px">
                  <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                  <div class="navbar-inner">
                    <div v-if="!proposal.readonly" class="container">
                      <p class="pull-right" style="margin-top:5px;">                       
                        <!-- <input type="submit" class="btn btn-primary" value="Save and Exit"/> -->
                        <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                        <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                        <!--<input type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/> -->
                        <input type="submit" class="btn btn-primary" value="Submit"/>
                        <!-- hidden 'save_and_continue_btn' used to allow File (file.vue component) to trigger save -->
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
    

    highlight_missing_fields: function(missing_fields){
        for (var i = 0; i < missing_fields.length; i++) {
            //$("#id_" + missing_fields[i].name).css("color", 'red');
            var name = missing_fields[i].name.split('.').slice(-1)[0];
            $("#id_" + name).css("color", 'red');
        }
    },

    submit: function(){
        let vm = this;
        vm.submitting = true;

        swal({
            title: "Submit Proposal",
            text: "Are you sure you want to submit this proposal?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then(() => {
            let formData = new FormData(vm.form);
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

<style lang="css">
</style>
