<template lang="html">
    <div class="container" >
        <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
            <Application v-if="application" :application="application">
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                <input type='hidden' name="application_id" :value="1" />
                <div v-if="!application.readonly" class="row" style="margin-bottom:50px;">
                    <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <span style="margin-right: 5px;"><strong>Estimated application fee: {{application.application_fee | toCurrency}}</strong></span>
                                    <input type="submit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                    <input v-if="application.application_fee == 0" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
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
    submit: function(){
        let vm = this;
        let form = document.forms.new_application;
        console.log(' SUBMIT VM FORM and CHECKOUT ');
        let formData = new FormData(vm.form);
        console.log(formData);

        let swal_title = 'Submit Application'
        let swal_text = 'Are you sure you want to submit this application?'
        if (vm.application.application_fee > 0) {
            swal_title = 'Submit Application and Checkout'
            swal_text = 'Are you sure you want to submit this application and proceed to checkout?'
        }

        swal({
            title: swal_title,
            text: swal_text,
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then((result) => {
            if (result.value) {
                let formData = new FormData(vm.form);
                form.submit();
//                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/submit'),formData).then(res=>{
//                    vm.application = res.body;
//                    console.log(res.body);
//                    console.log(res);
//                    vm.$router.push('/ledger/checkout/checkout/payment-details/');
//                    vm.$router.push({
//                        name: 'submit_application',
//                        params: { application: vm.application}
//                    });
//                },err=>{
//                    swal(
//                        'Submit Error',
//                        helpers.apiVueResourceError(err),
//                        'error'
//                    )
//                });
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
            vm.application = res.body;
            vm.loading.splice('fetching application', 1);
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
