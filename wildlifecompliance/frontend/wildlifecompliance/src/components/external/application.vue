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
                          <p>Activity Type:{{a.licence_activity_type.name}}</p>
                          <p>Reason: {{a.reason}}</p>
                          <p>Details: <p v-for="t in splitText(a.text)">{{t}}</p></p>  
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
              <div class="row">
            <div v-if="hasAmendmentRequest">
              <Application v-if="application" :application="application" :isAmendmentRequest="hasAmendmentRequest" :amendment_request_id="amendment_request_id">
            </div>
            <div v-else>
              <Application v-if="application" :application="application">
            </div>
            
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                <input type='hidden' name="application_id" :value="1" />
                <div v-if="!application.readonly" class="row" style="margin-bottom:50px;">
                    <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <span v-if="requiresCheckout"style="margin-right: 5px; font-size: 18px;">
                                        <strong>Estimated application fee: {{application.application_fee | toCurrency}}</strong>
                                        <strong>Estimated licence fee: {{application.licence_fee | toCurrency}}</strong>
                                    </span>
                                    <input type="submit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                    <input v-if="!requiresCheckout" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                                    <input v-else type="button" @click.prevent="submit" class="btn btn-primary" value="Submit and Checkout"/>
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
          </div>
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
      pBody: 'pBody',
      application_customer_status_onload: '',
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
        return this.application.application_fee > 0 && this.application_customer_status_onload == 'Draft'
    }
  },
  methods: {
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
        vm.amendment_request_id.push(vm.amendment_request[i].licence_activity_type.id)
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
    submit: function(){
        let vm = this;
        console.log('SUBMIT VM FORM and CHECKOUT');
        let formData = new FormData(vm.form);
        console.log(formData);
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
                        vm.$http.post(helpers.add_endpoint_join(api_endpoints.applications,vm.application.id+'/application_fee_checkout'), formData).then(res=>{
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
                    swal(
                        'Submit Error',
                        helpers.apiVueResourceError(err),
                        'error'
                    )
                });
            }
        },(error) => {
        });
    }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;

  },
  beforeRouteEnter: function(to, from, next) {
    if (to.params.application_id) {
      Vue.http.get(`/api/application/${to.params.application_id}.json`).then(res => {
          next(vm => {
            vm.loading.push('fetching application')
            // console.log("FROM APPLICATION FETCHING")
            vm.application = res.body;
            vm.loading.splice('fetching application', 1);
            // console.log("APPLICATION READONLY")
            vm.setdata(vm.application.readonly);

            Vue.http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/amendment_request')).then((res) => {
              // console.log("AMENDMENT REQUEST")
                console.log(res.body)
                vm.setAmendmentData(res.body);
            },
            err => {
                console.log(err);
            });

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
  }
}
</script>

<style lang="css">
</style>
