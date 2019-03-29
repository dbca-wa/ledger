<template lang="html">
    <div class="container" >
        <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>

              <Application v-if="isApplicationLoaded">
            
            
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
                                    <input v-if="canDiscardActivity" type="button" @click.prevent="discardActivity" class="btn btn-danger" value="Discard Activity"/>
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
import { mapActions, mapGetters } from 'vuex'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks';
export default {
  data: function() {
    return {
      form: null,
      application_customer_status_onload: {},
 	  missing_fields: [],
    }
  },
  components: {
    Application,
  },
  computed: {
    ...mapGetters([
        'application',
        'application_readonly',
        'amendment_requests',
        'selected_activity_tab_id',
        'selected_activity_tab_name',
        'isApplicationLoaded',
    ]),
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
    activity_discard_url: function() {
      return (this.application) ? `/api/application/${this.application.id}/discard_activity/` : '';
    },
    application_form_url: function() {
      return (this.application) ? `/api/application/${this.application.id}/draft.json` : '';
    },
    requiresCheckout: function() {
        return this.application.application_fee > 0 && this.application_customer_status_onload.id == 'draft'
    },
    canDiscardActivity: function() {
      return this.application.activities.find(
              activity => activity.licence_activity == this.selected_activity_tab_id &&
              activity.processing_status == 'draft'
            );
    }
  },
  methods: {
    ...mapActions({
      load: 'loadApplication',
    }),
    ...mapActions([
        'setApplication',
        'setActivityTab',
    ]),
    eventListeners: function(){
        let vm = this;
        $("ul#tabs-section").on("click", function (e) {
          if(!e.target.href) {
            return;
          }
          const tab_id = e.target.href.split('#')[1];
          vm.setActivityTab({id: tab_id, name: e.target.innerHTML});
        });
        $('#tabs-section li:first-child a').click();
    },
    discardActivity: function(e) {
      let swal_title = 'Discard Selected Activity';
      let swal_html = `Are you sure you want to discard activity: ${this.selected_activity_tab_name}?`;
      swal({
          title: swal_title,
          html: swal_html,
          type: "question",
          showCancelButton: true,
          confirmButtonText: 'Discard',
          confirmButtonColor: '#d9534f',
      }).then((result) => {
        this.$http.delete(this.activity_discard_url, {params: {'activity_id': this.selected_activity_tab_id}}).then(res=>{
            swal(
              'Activity Discarded',
              `${this.selected_activity_tab_name} has been discarded from this application.`,
              'success'
            );

            // No activities left? Redirect out of the application screen.
            if(res.body.processing_status === 'discarded') {
              this.$router.push({
                  name:"external-applications-dash",
              });
            }
            else {
              this.load({ url: `/api/application/${this.application.id}.json` }).then(() => {
                window.location.reload(true);  //TODO: Remove this once the activity headers / tabs are fully reactive
              });
            }
        },err=>{
          swal(
            'Error',
            helpers.apiVueResourceError(err),
            'error'
          )
        });
      },(error) => {
      });
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
                    this.setApplication(res.body);
                    
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
  },
  mounted: function() {
    this.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
      if (to.params.application_id) {
        vm.load({ url: `/api/application/${to.params.application_id}.json` }).then(() => {
            vm.application_customer_status_onload = vm.application.customer_status;
        });
      }
      else {
        vm.load({ url: '/api/application.json' });
      }
    });
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
