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
                <div v-if="!application.readonly && userCanSubmit" class="row" style="margin-bottom:50px;">
                    <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <span v-if="requiresCheckout" style="margin-right: 5px; font-size: 18px; display: block;">
                                        <strong>Estimated application fee: {{application.application_fee | toCurrency}}</strong>
                                        <strong>Estimated licence fee: {{application.licence_fee | toCurrency}}</strong>
                                    </span>
                                    <input v-if="!isProcessing && canDiscardActivity" type="button" @click.prevent="discardActivity" class="btn btn-danger" value="Discard Activity"/>
                                    <input v-if="!isProcessing" type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input v-if="!isProcessing" type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                    <input v-if="!isProcessing && !requiresCheckout" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                                    <input v-if="!isProcessing && requiresCheckout" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit and Checkout"/>
                                    <button v-if="isProcessing" disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Processing</button>
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
      isProcessing: false,
      tabSelected: false,
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
        'renderer_form_data',
        'selected_activity_tab_id',
        'selected_activity_tab_name',
        'isApplicationLoaded',
        'unfinishedActivities',
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
    application_form_data_url: function() {
      return (this.application) ? `/api/application/${this.application.id}/form_data.json` : '';
    },
    requiresCheckout: function() {
      return this.application.application_fee > 0 && this.application_customer_status_onload.id == 'draft'
    },
    canDiscardActivity: function() {
      return this.application.activities.find(
              activity => activity.licence_activity == this.selected_activity_tab_id &&
              activity.processing_status == 'draft'
            );
    },
    userCanSubmit: function() {
      return this.application.can_current_user_edit
    }
  },
  methods: {
    ...mapActions({
      load: 'loadApplication',
    }),
    ...mapActions([
        'setApplication',
        'setActivityTab',
        'saveFormData',
    ]),
    eventListeners: function(){
      if(!this.tabSelected) {
        $('#tabs-section li:first-child a').click();
        this.tabSelected = true;
      }
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
                const newTab = this.unfinishedActivities[0];
                if(newTab == null) {
                  this.$router.push({
                    name:"external-applications-dash",
                  });
                }
                else {
                  this.setActivityTab({id: newTab.id, name: newTab.label});
                }
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
    reloadApplication: function(application_id) {
      if(!application_id && this.application) {
        application_id = this.application.id;
      }
      if (application_id) {
        this.load({ url: `/api/application/${application_id}.json` }).then(() => {
            this.application_customer_status_onload = this.application.customer_status;
        });
      }
      else {
        this.load({ url: '/api/application.json' });
      }
    },
    saveExit: function(e) {
      this.isProcessing = true;
      this.saveFormData({ url: this.application_form_data_url, draft: true }).then(res=>{
          swal(
            'Saved',
            'Your application has been saved',
            'success'
          ).then((result) => {
            this.isProcessing = false;
            window.location.href = "/";
          });
      },err=>{
        swal(
            'Error',
            'There was an error saving your application',
            'error'
        ).then((result) => {
            this.isProcessing = false;
        })
      });
    },
    save: function(e) {
      this.isProcessing = true;
      this.saveFormData({ url: this.application_form_data_url, draft: true }).then(res=>{
          swal(
            'Saved',
            'Your application has been saved',
            'success'
          ).then((result) => {
            this.isProcessing = false;
            this.reloadApplication();
          });
      },err=>{
        swal(
            'Error',
            'There was an error saving your application',
            'error'
        ).then((result) => {
            this.isProcessing = false;
        })
      });
    },
    highlight_missing_fields: function(){
      $('.missing-field').removeClass('missing-field');
      for (const missing_field of this.missing_fields) {
          $(`[name=${missing_field.name}`).addClass('missing-field');
      }

      var top = ($('#error').offset() || { "top": NaN }).top;
      $('html, body').animate({
          scrollTop: top
      }, 1);
    },
    submit: function(){
        let vm = this;
        this.isProcessing = true;
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
                this.saveFormData({ url: this.application_form_data_url }).then(res=>{
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/submit'),{}).then(res=>{
                      this.setApplication(res.body);
                      if (vm.requiresCheckout) {
                          vm.$http.post(helpers.add_endpoint_join(api_endpoints.applications,vm.application.id+'/application_fee_checkout/'), {}).then(res=>{
                              this.isProcessing = false;
                              window.location.href = "/ledger/checkout/checkout/payment-details/";
                          },err=>{
                              swal(
                                  'Submit Error',
                                  helpers.apiVueResourceError(err),
                                  'error'
                              ).then((result) => {
                                  this.isProcessing = false;
                              })
                          });
                      } else {
                          this.isProcessing = false;
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
                      ).then((result) => {
                          this.isProcessing = false;
                      });
                  });
                }, err=>{
                  console.log(err);
                  if(err.body.missing) {
                      this.missing_fields = err.body.missing;
                      this.highlight_missing_fields();
                      this.isProcessing = false;
                    }
                });
            } else {
                this.isProcessing = false;
            }
        },(error) => {
            swal(
                'Error',
                'There was an error submitting your application',
                'error'
            ).then((result) => {
                this.isProcessing = false;
            })
        });
    },
  },
  mounted: function() {
    this.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
      vm.reloadApplication(to.params.application_id);
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
