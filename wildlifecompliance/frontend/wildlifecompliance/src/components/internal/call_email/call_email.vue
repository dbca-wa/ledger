<template lang="html">
    <div class="container">
    
        <div class="row">
          <h3>Call/Email: {{ call_email.id }}</h3>

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
                <input class="form-control" v-model="call_email.number"/>
                <input class="form-control" v-model="call_email.caller"/>
                <input class="form-control" v-model="call_email.assigned_to"/>

                </template>


              </FormSection>
              <FormSection :label="`Location`" :Index="`1`">
                <MapLocation/>

              </FormSection>
              <FormSection :label="`Details`" :Index="`2`">
                <input readonly v-model="report_type"/>
                <div v-for="item in call_email.schema">
                  <compliance-renderer-block
                    :component="item" 
                    />
                </div>
              </FormSection>
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

import Map from "ol/Map.js";
import View from "ol/View.js";
import { defaults as defaultControls, ScaleLine } from "ol/control.js";
import { Tile as TileLayer, Vector as VectorLayer } from "ol/layer.js";
import { XYZ, OSM, WMTS } from "ol/source";
import {
  get,
  addProjection,
  addCoordinateTransforms,
  transform
} from "ol/proj.js";
import Feature from "ol/Feature.js";
import Overlay from "ol/Overlay";
import Point from "ol/geom/Point.js";
import VectorSource from "ol/source/Vector.js";
import { Icon, Style } from "ol/style.js";
import Geocoder from "ol-geocoder/dist/ol-geocoder.js";

export default {
  name: "ViewCallEmail",
  data: function() {
    //let vm = this;
    //console.log(classification);
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
      dummyGeoJSON: {
      "id": 1,
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [102.0, 0.5]
        },
        "properties": {
          "prop0": "value0"
        }
      },
      //panelClickersInitialised: false
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
      //location: "callemailStore/location",
      report_type: "report_type"
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    isLoading: function() {
      return this.loading.length > 0;
    },
    call_email_form_url: function() {
      return this.call_email
        ? `/api/call_email/${this.call_email.id}/form_data.json`
        : "";
    },
    dummyPoint: function() {
      return new Point(transform([-32, 119], "EPSG:4326", "EPSG:3857"))
    }, 
    GeoJSONData: {
      get: function() {
        if (this.call_email.GeoJSONData == null) {
          this.setGeoJSONData(this.dummyGeoJSON);
        }
        return this.call_email.GeoJSONData;
      },
      set: function(value) {
        this.setGeoJSONData(value);
      }
    },
    location: {
      get: function() {
        if (this.call_email.location.geometry == null) {
          this.setLocationPoint(this.dummyPoint);
        }
        return this.call_email.location;
      },
      set: function(value) {
        this.setLocation(value);
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
      //saveLocation: 'saveLocation',
      //setLocation: 'setLocation',
      setCallEmail: 'setCallEmail',
      //setGeoJSONData: 'setGeoJSONData',
      loadCallEmail: "loadCallEmail",
      loadClassification: "loadClassification",
      setGeoJSONData: 'setGeoJSONData',
      setLocation: 'setLocation',

      //saveLocation: "callemailStore/saveLocation"
    }),
    ...mapActions({
      saveFormData: "saveFormData",
    }),
    initLocation: function() {
      console.log("initLocation");
      console.log(this.dummyPoint);
      if (this.call_email.location.geometry == null) {
          this.setLocationPoint(this.dummyPoint);
        }
      if (this.call_email.GeoJSONData == null) {
          this.setGeoJSONData(this.dummyGeoJSON);
        }
    },
    /*
    updateLocation: function() {
      this.saveLocation({ call_email_id: this.call_id });
    },
    */
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
      /*
                this.$router.push({
                    name: 'internal-call-email-dash'
                });
                */
    },
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
  },
  beforeRouteEnter: function(to, from, next) {
    console.log("before route enter");
    let initialisers = [];
    next(vm => {
      console.log("before route enter - next");
      vm.loadCallEmail({ call_email_id: to.params.call_email_id });
      vm.loadClassification();
      vm.initLocation();
    });
  },

  mounted: function() {
    this.$nextTick(function() {});
  }
};
</script>

<style lang="css">
</style>
