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

              <FormSection :formCollapse="false" label="Caller" Index="0">
                
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
                    <input class="col-sm-1" type="radio" v-model="call_email.anonymous_call" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.anonymous_call" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Caller wishes to remain anonymous?</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.caller_wishes_to_remain_anonymous" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>
              </FormSection>

              <FormSection :formCollapse="false" label="Location" Index="1">
                  <div v-if="call_email.location">
                    <MapLocation v-bind:key="call_email.location.id"/>
                  </div>
              </FormSection>

              <FormSection :formCollapse="true" label="Details" Index="2">

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Use occurrence from/to</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.occurrence_from_to" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                    <div class="col-sm-3">
                      <datepicker input-class="form-control col-sm-3" placeholder="DD/MM/YYYY" v-model="call_email.occurrence_date_from" name="datefrom"/>
                    </div>
                    <div v-if="call_email.occurrence_from_to">
                      <label class="col-sm-3">Occurrence date to</label>
                      <div class="col-sm-3">
                        <datepicker input-class="form-control" placeholder="DD/MM/YYYY" v-model="call_email.occurrence_date_to" name="dateto"/>
                      </div>
                    </div>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                  <div class="col-sm-3">
                    <input class="form-control" v-model="call_email.occurrence_time_from"/>
                  </div>
                  <div v-if="call_email.occurrence_from_to">
                      <label class="col-sm-3">Occurrence time to</label>
                      <div class="col-sm-3">
                        <input class="form-control" v-model="call_email.occurrence_time_to"/>
                      </div>
                  </div>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Classification</label>
                  <select class="form-control" v-model="classification_id">
                        <option v-for="option in classification_types" :value="option.id" v-bind:key="option.id">
                          {{ option.name }} 
                        </option>
                    </select>
                </div></div>

                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Report Type</label>
                  <select class="form-control" v-model="report_type_id">
                          <option v-for="option in report_types" :value="option.id" v-bind:key="option.id">
                            {{ option.report_type }} 
                          </option>
                  </select>
                </div></div>
                
                <div v-for="(item, index) in current_schema">
                  <compliance-renderer-block
                    :component="item"
                    v-bind:key="`compliance_renderer_block_${report_type_id}`"
                    />
                </div>
              </FormSection>

              <FormSection :formCollapse="true" label="Outcome" Index="3">
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Referrer</label>
                  <select class="form-control" v-model="call_email.referrer_id">
                          <option  v-for="option in referrers" :value="option.id" v-bind:key="option.id">
                            {{ option.name }} 
                          </option>
                  </select>
                </div></div>
                <div class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice given</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="true">
                    <label class="col-sm-1">Yes</label>
                    <input class="col-sm-1" type="radio" v-model="call_email.advice_given" v-bind:value="false">
                    <label class="col-sm-1">No</label>
                </div></div>
                <div v-if="call_email.advice_given" class="col-sm-12 form-group"><div class="row">
                  <label class="col-sm-4">Advice details</label>
                  <textarea class="form-control" rows="5" v-model="call_email.advice_details"/>
                </div></div>
              </FormSection>
              
              <div class="col-sm-12 form-group"><div class="row">
              <h3></h3>
              </div></div>
            
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
import FormSection from "@/components/compliance_forms/section_toggle.vue";

import CommsLogs from "@common-components/comms_logs.vue";
import MapLocation from "./map_location.vue";
import { api_endpoints, helpers } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import Datepicker from 'vuejs-datepicker';
import moment from 'moment';
import localforage from "localforage";

let CallEmail_ReportType_Schema = localforage.createInstance({
    name: "WildlifeCompliance",
    storeName: 'CallEmail_ReportType_Schema',
  });

export default {
  name: "ViewCallEmail",
  data: function() {
    return {
      current_schema: [],
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
    }),
    classification_id: {
        get: function() {
          return this.call_email.classification ? this.call_email.classification.id : "";
        },
        set: function(value) {
          let classification = null;
          this.classification_types.forEach(function(element) {
            if (element.id === value) {
              classification = element;
            }
          }); 
          this.setClassification(classification);
        }, 
    },
    report_type_id: {
        get: function() {
          return this.call_email.report_type ? this.call_email.report_type.id : "";
        },
        set: async function(value) {
          let report_type = null;
          this.report_types.forEach(function(element) {
            if (element.id === value) {
              report_type = element;
            }
          }); 
          await this.loadSchema(value);
          await this.setReportType(report_type);
        }, 
    },
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
      setClassification: "setClassification",
      setReportType: "setReportType",
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
    duplicate: async function() {
      await this.saveCallEmail({ route: false, crud: 'duplicate'});
    },
    loadSchema: async function(new_report_type_id) {
            console.log("loadSchema");
            if (this.report_type_id || new_report_type_id) {
              try {
                  let new_schema = [];
                  let retrieved_val = null;
                  let report_type_id_str = "";
                  if (new_report_type_id) {
                    report_type_id_str = new_report_type_id.toString();
                  } else {
                    report_type_id_str = this.report_type_id.toString();
                  }
                  // check local cache to see if key exists
                  try {
                    retrieved_val = await CallEmail_ReportType_Schema.getItem(
                      report_type_id_str)
                  } catch(err) {
                    console.log(err);
                  }
                  
                  let timeDiff = 0;
                  if (retrieved_val) {
                    const timeNow = Date.now();
                    timeDiff = timeNow - retrieved_val[0];
                    console.log("timeDiff");
                    console.log(timeDiff);
                    Object.assign(new_schema, retrieved_val[1]);
                  }

                  // if no schema retrieved or expired cached value, fetch new schema from db
                  if (!(new_schema.length > 0) || timeDiff > 86400000) {
                    let payload = new Object();
                    payload.id = this.call_email.id;
                    payload.report_type_id = report_type_id_str;

                    const updatedCallEmail = await Vue.http.post(
                        helpers.add_endpoint_join(
                            api_endpoints.call_email, 
                            this.call_email.id + "/update_schema/"),
                        payload
                        );
                    
                    const insertTimeNow = Date.now()
                    const value_to_cache = [insertTimeNow, updatedCallEmail.body.schema];
                    
                    try {
                      await CallEmail_ReportType_Schema.setItem(
                        report_type_id_str, 
                        value_to_cache)
                      console.log("keyvalue stored");  
                    } catch(err) {
                      console.log(err);
                    }
                    try {
                      retrieved_val = await CallEmail_ReportType_Schema.getItem(
                        report_type_id_str)
                    } catch(err) {
                      console.error(err);
                    }
                    if (retrieved_val) {
                      Object.assign(this.current_schema, retrieved_val[1]);
                    }
                  } else {
                      console.log("cached keyvalue");  
                      Object.assign(this.current_schema, new_schema);
                  }
              } catch (err) {
                  console.error(err);
              }
            }
    },
  },

  created: async function() {
    
    if (this.$route.params.call_email_id) {
      await this.loadCallEmail({ call_email_id: this.$route.params.call_email_id });
    }
    // load current CallEmail renderer schema
    await this.loadSchema(this.call_email.report_type_id);
    
    // load drop-down select lists
    await this.loadClassification();
    await this.loadReportTypes();
    await this.loadReferrers();
    
  },
  mounted: function() {
        console.log(this);
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
  }
};
</script>

<style lang="css">
</style>
