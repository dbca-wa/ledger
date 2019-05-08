<template lang="html">
    <div class="container">
    
        <div class="row">
          <h3>Call/Email: {{ call_email.number }}</h3>

          <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ call_email.caller }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ call_email.lodgement_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ call_email.name }}<br/>
                                <div class ="col-sm-12" v-for="item in call_email.schema">
                                    
                                    <div v-for="item1 in item">
                                        <div v-if="item1.name">
                                            <strong>{{item1.name}}: </strong>{{item1.label}}
                                        </div>
                                    </div>
                                </div>
                            </div>
                             
                          </div>
                          <button @click.prevent="save"
                            class="btn btn-primary pull-right">Save</button>
                      </div>
                  </div>
              </div>
        </div>
        <div class="col-md-1"></div>
          <div class="col-md-8">  
            <div class="row">
              <FormSection :label="`Contact`" :Index="`0`">
                
                <template>
                    <select class="form-control" v-model="call_email.classification_id">
                        <option v-for="option in classification_types" :value="option.id" v-bind:key="option.id">
                          {{ option.name }} 
                        </option>
                    </select>
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Caller</label>
                  <input class="form-control" v-model="call_email.caller"/>
                </div></div>
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Assigned To</label>
                <input class="form-control" v-model="call_email.assigned_to"/>
                </div></div>
                </template>

              </FormSection>
              <FormSection :label="`Location`" :Index="`1`">
                  
                  <div v-if="call_email.location">
                    <MapLocation v-bind:key="call_email.location.id"/>
                  </div>

              </FormSection>
              <FormSection :label="`Details`" :Index="`2`">
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Report Type</label>
                
                  <select class="form-control" v-model="call_email.report_type_id">
                          <option v-for="option in report_types" :value="option.id" v-bind:key="option.id">
                            {{ option.report_type }} v{{ option.version }} 
                          </option>
                  </select>
                </div></div>
                
                <div v-for="(item, index) in call_email.schema">
                  <compliance-renderer-block
                    :component="item"
                    v-bind:key="`compliance_renderer_block_${index}`"
                    />
                </div>
              </FormSection>
            </div>          
              
          </div>
        </div>  
        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    <!--
                                    <span v-if="requiresCheckout" style="margin-right: 5px; font-size: 18px; display: block;">
                                        <strong>Estimated application fee: {{application.application_fee | toCurrency}}</strong>
                                        <strong>Estimated licence fee: {{application.licence_fee | toCurrency}}</strong>
                                    </span>
                                    -->
                                    
                                    <input type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                    
                                    
                                </p>
                            </div>
                        </div>
                    </div>          
    </div>
</template>
<script>
import Vue from "vue";
import FormSection from "@/components/compliance_forms/section.vue";
import CommsLogs from "@common-components/comms_logs.vue";
import MapLocation from "./map_location.vue";
import { api_endpoints, helpers } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";

export default {
  name: "ViewCallEmail",
  data: function() {
    return {
      sectionLabel: "Details",
      sectionIndex: 1,

      pBody: "pBody" + this._uid,
      loading: [],
      renderer_form: null,
      callemailTab: "callemailTab" + this._uid,
      comms_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/comms_log"
      ),
      comms_add_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/add_comms_log"
      ),
      logs_url: helpers.add_endpoint_json(
        api_endpoints.call_email,
        this.$route.params.call_email_id + "/action_log"
      ),
      
    };
  },

  components: {
    CommsLogs,
    FormSection,
    MapLocation
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
      //call_id: "callemailStore/call_id",
      classification_types: "classification_types",
      report_types: "report_types",
      //location: "callemailStore/location",
      //report_type: "report_type",
      call_email_form_url: "call_email_form_url",
    }),
    ...mapGetters({
      renderer_form_data: 'renderer_form_data',
    },
    ),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    isLoading: function() {
      return this.loading.length > 0;
    },
    /*
    call_email_form_url: function() {
      return this.call_email
        ? `/api/call_email/${this.call_email.id}/form_data.json`
        : "";
    },
    */

  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ...mapActions('callemailStore', {
      setCallEmail: 'setCallEmail',
      loadCallEmail: "loadCallEmail",
      loadClassification: "loadClassification",
      loadReportTypes: "loadReportTypes",
      setLocation: 'setLocation',
      setLocationPoint: 'setLocationPoint',
      saveCallEmail: 'saveCallEmail',
      createCallEmail: "createCallEmail",
    }),
    ...mapActions({
      saveFormData: "saveFormData",
    }),
    /*
    createCallEmail: function(e) {
      let formData = new FormData(this.renderer_form);
      this.$http
        .post(
          helpers.add_endpoint_join(
            api_endpoints.call_email,
            this.call_email.id + "/update_renderer_form/"
          ),
          formData
        )
        .then(
          res => {
            swal("Saved", "Your Call/Email has been saved", "success");
          },
          err => {}
        );

    },
    */
    /*
    save: function() {
      if (this.call_email.id) {
      console.log("this.saveCallEmail");
      this.saveCallEmail({location: this.call_email.location, renderer: this.call_email.schema});
      } else {
        if (this.call_email.location.geometry.coordinates > 0 && this.call_email.schema.length > 0) {
          console.log("there is location and schema");
          this.createCallEmail({location: this.call_email.location, renderer: this.call_email.schema});
        } else if (this.call_email.location.geometry.coordinates > 0) {
            console.log("just location");
            this.createCallEmail({location: this.call_email.location});
        } else if (this.call_email.schema.length > 0) {
          console.log("just schema");
          this.createCallEmail({renderer: this.call_email.schema});
        } else {
          console.log("bare call/email");
          this.createCallEmail({location: null, renderer: null, route: null});
        }
      }
          
    },
    */
    save: async function() {
      if (this.call_email.id) {
        //console.log("this.saveCallEmail");
        await this.saveCallEmail({ route: false, crud: 'save' });
      } else {
        //console.log("this.createCallEmail");
        await this.saveCallEmail({ route: false, crud: 'create'});
        this.$nextTick(function() {
          this.$router.push({name: 'view-call-email', params: {call_email_id: this.call_email.id}});
        });
      }
    },
  
  
  /*
    save: function() {
      this.saveCallEmail({location: true, renderer: true})
      .then(res => {
        swal("Saved", "The record has been saved", "success");
      },
      err => {
        swal("Error", "There was an error saving the record", "error");
        console.log(err);
      });
    
    },
*/
    saveExit: function() {
      if (this.call_email.id) {
        console.log("this.saveCallEmail");
        this.saveCallEmail({ route: true, crud: 'save' });
      } else {
        console.log("this.createCallEmail");
        this.saveCallEmail({ route: true, crud: 'create'});
      }
    },
    /*
    save: function(e) {
      this.isProcessing = true;
      this.$http
        .post(
          helpers.add_endpoint_join(
            api_endpoints.call_email,
            this.call_email.id + "/call_email_save/"
          ),
          this.call_email
        )
        .then(
          resOne => {
            console.log(resOne);
            this.saveFormData({ url: this.call_email_form_url }).then(
              resTwo => {
                this.isProcessing = false;
              },
              errTwo => {
                swal(
                  "Error",
                  "There was an error saving the record",
                  "error"
                ).then(errTwoRes => {
                  this.isProcessing = false;
                });
              }
            );
            swal("Saved", "The record has been saved", "success").then(
              result => {
                this.isProcessing = false;
              }
            );
          },
          errOne => {
            swal("Error", "There was an error saving the record", "error").then(
              result => {
                this.isProcessing = false;
              }
            );
          }
        );
    }
    */
  },
  created: function() {
    
    if (this.$route.params.call_email_id) {
      this.loadCallEmail({ call_email_id: this.$route.params.call_email_id });
    }
    this.loadClassification();
    this.loadReportTypes();
  },
  
  /*
  beforeRouteEnter: function(to, from, next) {
    console.log("before route enter");
    let initialisers = [];
    next(vm => {
      console.log("before route enter - next");
      vm.loadCallEmail({ call_email_id: to.params.call_email_id });
      console.log("call_email loaded"); 
      vm.loadClassification();
      console.log("vuex loaded");
    });
  },
*/
  mounted: function() {
    this.$nextTick(function() {});
  }
};
</script>

<style lang="css">
</style>
