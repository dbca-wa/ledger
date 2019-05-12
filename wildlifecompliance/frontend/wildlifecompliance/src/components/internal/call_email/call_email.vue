<template lang="html">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <h3>Call/Email: {{ call_email.number }}</h3>
        </div>
        <div class="col-md-3 pull-right">
          <input type="button" @click.prevent="duplicate" class="pull-right btn btn-primary" value="Create Duplicate Call/Email"/>  
        </div>
      </div>
          <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            
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
                             
                    </div>
                </div>
            </div>
          </div>
          <div class="col-md-1"/>        
          <div class="col-md-8">  
            <div class="row">

              <FormSection collapse="collapse in" label="Caller" Index="0">
                
                <div class="row"><div class="col-sm-8 form-group">
                  <label class="col-sm-12">Caller name</label>
                  <input class="form-control" v-model="call_email.caller"/>
                </div></div>
                <div class="col-sm-4 form-group"><div class="row">
                  <label class="col-sm-12">Caller contact number</label>
                <input class="form-control" v-model="call_email.caller_phone_number"/>
                </div></div>
                
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Anonymous call?</label>
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.anonymous_call" v-bind:value="true">
                    <label class="col-sm-1">No</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.anonymous_call" v-bind:value="false">
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Caller wishes to remain anonymous?</label>
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="true">
                    <label class="col-sm-1">No</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="false">
                </div></div>
              </FormSection>

              <FormSection collapse="collapse in" label="Location" Index="1">
                  <div v-if="call_email.location">
                    <MapLocation v-bind:key="call_email.location.id"/>
                  </div>
              </FormSection>

              <FormSection collapse="collapse" label="Details" Index="2">

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Use occurrence from/to</label>
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="true">
                    <label class="col-sm-1">No</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="false">
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                    <datepicker placeholder="DD/MM/YYYY" input-class="col-sm-3" v-model="call_email.occurrence_date_from" name="datefrom"/>
                    <div v-if="call_email.occurrence_from_to">
                      <label class="col-sm-3">Occurrence date to</label>
                      <datepicker placeholder="DD/MM/YYYY" input-class="col-sm-3" v-model="call_email.occurrence_date_to" name="dateto"/>
                    </div>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                  <input type="text" class="col-sm-2" v-model="call_email.occurrence_time_from"/>
                    <label v-if="call_email.occurrence_from_to" class="col-sm-3">Occurrence time to</label>
                    <input v-if="call_email.occurrence_from_to" type="text" class="col-sm-2" v-model="call_email.occurrence_time_to"/>
                </div></div>


                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Classification</label>
                  <select class="form-control" v-model="call_email.classification_id">
                        <option v-for="option in classification_types" :value="option.id" v-bind:key="option.id">
                          {{ option.name }} 
                        </option>
                    </select>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Report Type</label>
                  <select @click.prevent="loadSchema" class="form-control" v-model="call_email.report_type_id">
                          <option  v-for="option in report_types" :value="option.id" v-bind:key="option.id">
                            {{ option.report_type }} 
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

              <FormSection collapse="collapse" label="Outcome" Index="3">
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Referrer</label>
                  <select class="col-sm-6" v-model="call_email.referrer_id">
                          <option  v-for="option in referrers" :value="option.id" v-bind:key="option.id">
                            {{ option.name }} 
                          </option>
                  </select>
                </div></div>
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice given</label>
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="true">
                    <label class="col-sm-1">No</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="false">
                </div></div>
                <div v-if="call_email.advice_given" class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice details</label>
                  <textarea class="form-control" rows="5" v-model="call_email.advice_details"/>
                </div></div>
              </FormSection>
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
import Datepicker from 'vuejs-datepicker';

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
    MapLocation,
    Datepicker,
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
      classification_types: "classification_types",
      report_types: "report_types",
      referrers: "referrers",
    }),
    ...mapGetters({
      renderer_form_data: 'renderer_form_data',
    },
    ),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    occurrenceDateLabel: function() {
      if (this.call_email.occurrence_from_to) {
        return "Occurrence date from";
      } else {
        return "Occurrence date";
      }
    },
    occurrenceTimeLabel: function() {
      if (this.call_email.occurrence_from_to) {
        return "Occurrence time from";
      } else {
        return "Occurrence time";
      }
    },

  },
  
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },

  methods: {
    ...mapActions('callemailStore', {
      loadCallEmail: "loadCallEmail",
      loadClassification: "loadClassification",
      loadReportTypes: "loadReportTypes",
      saveCallEmail: 'saveCallEmail',
      updateSchema: "updateSchema",
      loadReferrers: "loadReferrers",
    }),
    ...mapActions({
      saveFormData: "saveFormData",
    }),
    save: async function() {
      if (this.call_email.id) {
        await this.saveCallEmail({ route: false, crud: 'save' });
      } else {
        await this.saveCallEmail({ route: false, crud: 'create'});
        this.$nextTick(function() {
          this.$router.push({name: 'view-call-email', params: {call_email_id: this.call_email.id}});
        });
      }
    },
    saveExit: async function() {
      if (this.call_email.id) {
        await this.saveCallEmail({ route: true, crud: 'save' });
      } else {
        await this.saveCallEmail({ route: true, crud: 'create'});
      }
    },
    loadSchema: function() {
      this.updateSchema();
    },
    duplicate: async function() {
      await this.saveCallEmail({ route: false, crud: 'duplicate'});
    },
  },

  created: function() {
    
    if (this.$route.params.call_email_id) {
      this.loadCallEmail({ call_email_id: this.$route.params.call_email_id });
    }
    this.loadClassification();
    this.loadReportTypes();
    this.loadReferrers();
    
  },
};
</script>

<style lang="css">
</style>
