<template lang="html">
    <div class="container" >
        <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
          <div v-if="!application_readonly">
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
                          <p>Activity: {{a.licence_activity.name}}</p>
                          <p>Reason: {{a.reason.name}}</p>
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

              <Application v-if="application" :application="application">
            
            
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                <input type='hidden' name="application_id" :value="1" />
                <div v-if="!application.readonly" class="row" style="margin-bottom:50px;">
                    <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <span v-if="requiresCheckout" style="margin-right: 5px; font-size: 18px;">
                                        <strong>Estimated application fee: {{application.application_fee | toCurrency}}</strong>
                                        <strong>Estimated licence fee: {{application.licence_fee | toCurrency}}</strong>
                                    </span>
                                    <input type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                    <input v-if="!requiresCheckout" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                                    <input v-if="requiresCheckout" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit and Checkout"/>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="row" style="margin-bottom:50px;">
                    <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <router-link class="btn btn-primary" :to="{name: 'external-applications-dash'}">Back to Dashboard</router-link>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </Application>
        </form>
    </div>
</template>
<script>
import Application from '../form.vue'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  data: function() {
    return {
      "application": null,
      "loading": [],
      form: null,
      hasAmendmentRequest: false,
      amendment_request: [],
      amendment_request_id:[],
      application_readonly: true,
      selected_activity_tab_id: null,
      selected_activity_tab_name: null,
      pBody: 'pBody',
      application_customer_status_onload: {},
 	  missing_fields: [],
    }
  },
  components: {
    Application
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
    application_form_url: function() {
      return (this.application) ? `/api/application/${this.application.id}/draft.json` : '';
    },
    requiresCheckout: function() {
        return this.application.application_fee > 0 && this.application_customer_status_onload.id == 'draft'
    },
  },
  methods: {
    eventListeners: function(){
        let vm = this;
        $("ul#tabs-section").on("click", function (e) {
            vm.selected_activity_tab_id = e.target.href.split('#')[1];
            vm.selected_activity_tab_name = e.target.innerText;
        });
        $('#tabs-section li:first-child a').click();
    },
    saveExit: function(e) {
      let vm = this;
      let formData = new FormData(vm.form);
      vm.$http.post(vm.application_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your application has been saved',
            'success'
          ).then((result) => {
            window.location.href = "/";
          });
      },err=>{

      });
    },
    save: function(e) {
      let vm = this;
      let formData = new FormData(vm.form);
      vm.$http.post(vm.application_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your application has been saved',
            'success'
          )
      },err=>{

      });
    },
    setAmendmentData: function(amendment_request){
      let vm= this;
      vm.amendment_request = amendment_request;
      for(var i=0,_len=vm.amendment_request.length;i<_len;i++){
        vm.amendment_request_id.push(vm.amendment_request[i].licence_activity.id)
      }

      if (amendment_request.length > 0){
        vm.hasAmendmentRequest = true;
      }
        
    },
    setdata: function(readonly){
      this.application_readonly = readonly;
    },
    splitText: function(aText){
      let newText = '';
      newText = aText.split("\n");
      return newText;
    },
    highlight_missing_fields: function(){
        for (const missing_field of this.missing_fields) {
            $("#id_" + missing_field.name).css("color", 'red');
        }

        var top = ($('#error').offset() || { "top": NaN }).top;
        $('html, body').animate({
            scrollTop: top
        }, 1);
    },
    submit: function(){
        let vm = this;
        let formData = new FormData(vm.form);
        let swal_title = 'Submit Application'
        let swal_html = 'Are you sure you want to submit this application?'
        if (vm.requiresCheckout) {
            swal_title = 'Submit Application and Checkout'
            swal_html = 'Are you sure you want to submit this application and proceed to checkout?<br><br>' +
                'Upon proceeding, you agree that the system will charge the same credit card used to ' +
                'pay the application fee when your licence is issued.'
        }
        swal({
            title: swal_title,
            html: swal_html,
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then((result) => {
            if (result.value) {
                let formData = new FormData(vm.form);
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/submit'),formData).then(res=>{
                    vm.application = res.body;
                    
                    if (vm.requiresCheckout) {
                        vm.$http.post(helpers.add_endpoint_join(api_endpoints.applications,vm.application.id+'/application_fee_checkout/'), formData).then(res=>{
                            window.location.href = "/ledger/checkout/checkout/payment-details/";
                        },err=>{
                            swal(
                                'Submit Error',
                                helpers.apiVueResourceError(err),
                                'error'
                            )
                        });
                    } else {
                        vm.$router.push({
                            name: 'submit_application',
                            params: { application: vm.application}
                        });
                    }
                },err=>{
                    console.log(err);
                    if(err.body.missing) {
                      this.missing_fields = err.body.missing;
                      this.highlight_missing_fields();
                    }
                    else {
                      swal(
                          'Submit Error',
                          helpers.apiVueResourceError(err),
                          'error'
                      )
                    }
                });
            }
        },(error) => {
        });
    },
    fetchAmendmentRequest: function(){
      let vm= this
      Vue.http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/amendment_request')).then((res) => {
          vm.setAmendmentData(res.body);
      },err=>{
      });
    },
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    if (to.params.application_id) {
      let vm= this;
      Vue.http.get(`/api/application/${to.params.application_id}.json`).then(res => {
          next(vm => {
            vm.loading.push('fetching application')
            vm.application = res.body;
            vm.loading.splice('fetching application', 1);
            vm.setdata(vm.application.readonly);

            vm.fetchAmendmentRequest();
            vm.application_customer_status_onload = vm.application.customer_status;
          });
        },
        err => {
          console.log(err);
        });
      
    }
    else {
      Vue.http.post('/api/application.json').then(res => {
          next(vm => {
            vm.loading.push('fetching application')
            vm.application = res.body;
            vm.loading.splice('fetching application', 1);
          });
        },
        err => {
          console.log(err);
        });
    }
  },
  updated: function(){
    let vm = this;
    this.$nextTick(() => {
        vm.eventListeners();
    });
  },
}
</script>

<style lang="css">
</style>
