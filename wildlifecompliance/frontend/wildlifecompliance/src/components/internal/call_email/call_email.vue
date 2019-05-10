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
      classification_types: "classification_types",
      report_types: "report_types",
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
    saveExit: function() {
      if (this.call_email.id) {
        console.log("this.saveCallEmail");
        this.saveCallEmail({ route: true, crud: 'save' });
      } else {
        console.log("this.createCallEmail");
        this.saveCallEmail({ route: true, crud: 'create'});
      }
    },
  },

  created: function() {
    
    if (this.$route.params.call_email_id) {
      this.loadCallEmail({ call_email_id: this.$route.params.call_email_id });
    }
    this.loadClassification();
    this.loadReportTypes();
  },

  mounted: function() {
    this.$nextTick(function() {});
  }
};
</script>

<style lang="css">
</style>
