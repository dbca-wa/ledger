<template lang="html">
    <div id="InspectionWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">

                        <div class="form-group">
                          <div class="row">
                              <div class="col-sm-3">
                                  <label class="control-label pull-left" for="details">Details</label>
                              </div>
            			      <div class="col-sm-6">
                                  <textarea class="form-control" placeholder="add details" id="details" v-model="workflowDetails"/>
                              </div>
                          </div>
                        </div>
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Attachments</label>
                                </div>
            			        <div class="col-sm-9">
                                    <filefield ref="comms_log_file" name="comms-log-file" :isRepeatable="true" :documentActionUrl="inspection.commsLogsDocumentUrl"/>
                                </div>
                            </div>
                        </div>

                </div>
              
            </div>
          </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>Error: {{ errorResponse }}</strong>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>
<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import filefield from '@/components/common/compliance_file.vue';

export default {
    name: "InspectionWorking",
    data: function() {
      return {
            officers: [],
            isModalOpen: false,
            processingDetails: false,
            form: null,
            regions: [],
            regionDistricts: [],
            availableDistricts: [],
            casePriorities: [],
            inspectionTypes: [],
            externalOrganisations: [],
            workflowDetails: '',
            errorResponse: "",
            region_id: null,
            district_id: null,
            assigned_to_id: null,
            inspection_type_id: null,
            advice_details: "",
            allocatedGroup: [],
            allocated_group_id: null,
            documentActionUrl: '',
            // files: [
            //         {
            //             'file': null,
            //             'name': ''
            //         }
            //     ]
      }
    },
    components: {
      modal,
      filefield,
    },
    props:{
          workflow_type: {
              type: String,
              default: '',
          },
    },
    computed: {
      ...mapGetters('inspectionStore', {
        inspection: "inspection",
      }),
      regionDistrictId: function() {
          if (this.district_id || this.region_id) {
              return this.district_id ? this.district_id : this.region_id;
          } else {
              return null;
          }
      },
      modalTitle: function() {
          if (this.workflow_type === 'send_to_manager') {
              return "Send to Manager";
          } else if (this.workflow_type === 'request_amendment') {
              return "Request Amendment";
          } else if (this.workflow_type === 'close') {
              return "Close Inspection";
          }
      },
      groupPermission: function() {
          if (this.workflow_type === 'send_to_manager') {
              return "manager";
          } else if (this.workflow_type === 'request_amendment') {
              return "officer";
          }
      },
    },
    filters: {
      formatDate: function(data) {
          return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
      }
    },
    methods: {
      ...mapActions('inspectionStore', {
          saveInspection: 'saveInspection',
          loadInspection: 'loadInspection',
          setInspection: 'setInspection',
      }),
      ...mapActions({
          loadAllocatedGroup: 'loadAllocatedGroup',
      }),
      updateAllocatedGroup: async function() {
          console.log("updateAllocatedGroup");
          this.errorResponse = "";
          if (this.regionDistrictId) {
              let allocatedGroupResponse = await this.loadAllocatedGroup({
              region_district_id: this.regionDistrictId,
              group_permission: this.groupPermission,
              });
              if (allocatedGroupResponse.ok) {
                  console.log(allocatedGroupResponse.body.allocated_group);
                  //this.allocatedGroup = Object.assign({}, allocatedGroupResponse.body.allocated_group);
                  Vue.set(this, 'allocatedGroup', allocatedGroupResponse.body.allocated_group);
                  this.allocated_group_id = allocatedGroupResponse.body.group_id;
              } else {
                  // Display http error response on modal
                  this.errorResponse = allocatedGroupResponse.statusText;
              }
              // Display empty group error on modal
              if (!this.errorResponse &&
                  this.allocatedGroup &&
                  this.allocatedGroup.length <= 1) {
                  this.errorResponse = 'This group has no members';
              }
          }
      },

      ok: async function () {
          const response = await this.sendData();
          console.log(response);
          if (response.ok) {
              this.close();
              this.$router.push({ name: 'internal-inspection-dash' });
          }
      },
      cancel: async function() {
          await this.$refs.comms_log_file.cancel();
          this.isModalOpen = false;
          this.close();
      },
      close: function () {
          let vm = this;
          this.isModalOpen = false;
      },
      sendData: async function() {
          let post_url = '/api/inspection/' + this.inspection.id + '/workflow_action/'
          
          let payload = new FormData();
          payload.append('details', this.workflowDetails);
          this.$refs.comms_log_file.commsLogId ? payload.append('inspection_comms_log_id', this.$refs.comms_log_file.commsLogId) : null;
          this.workflow_type ? payload.append('workflow_type', this.workflow_type) : null;

          let inspectionRes = await this.saveInspection({internal: true })
          if (inspectionRes.ok) {
              try {
                  let res = await Vue.http.post(post_url, payload);
                  console.log(res);
                  if (res.ok) {
                      return res
                  }
              } catch(err) {
                      this.errorResponse = err.statusText;
                  }
          }
      },
      createDocumentActionUrl: async function(done) {
        if (!this.inspection.id) {
            // create inspection and update vuex
            let returned_inspection = await this.saveInspection({ create: true, internal: true })
            await this.loadInspection({inspection_id: returned_inspection.body.id});
        }
        // populate filefield document_action_url
        this.$refs.comms_log_file.document_action_url = this.inspection.createInspectionProcessCommsLogsDocumentUrl;
        return done(true);
      },

    },
    created: async function() {
        if (this.inspection && this.inspection.id) {
            this.inspection_type_id = this.inspection.inspection_type_id;
            this.region_id = this.inspection.region_id;
            this.district_id = this.inspection.district_id;
        }

        // ensure allocated group is current
        await this.updateAllocatedGroup();
    }
};
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
