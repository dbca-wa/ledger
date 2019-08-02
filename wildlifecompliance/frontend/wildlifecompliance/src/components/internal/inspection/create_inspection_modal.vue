<template lang="html">
    <div id="InspectionWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Create new Inspection" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Region</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control col-sm-9" @change.prevent="updateDistricts()" v-model="region_id">
                                <option  v-for="option in regions" :value="option.id" v-bind:key="option.id">
                                  {{ option.display_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>District</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" @change.prevent="updateAllocatedGroup()" v-model="district_id">
                                <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                  {{ option.display_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Allocate to</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="assigned_to_id">
                                <option  v-for="option in allocatedGroup" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Inspection Type</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="inspection_type_id">
                                <option  v-for="option in inspectionTypes" :value="option.id" v-bind:key="option.id">
                                  {{ option.description }}
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>

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
                                    <filefield ref="comms_log_file" name="comms-log-file" :isRepeatable="true" :createDocumentActionUrl="createDocumentActionUrl" />
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
            referrers: [],
            referrers_selected: [],
            //group_permission: '',
            workflowDetails: '',
            errorResponse: "",
            region_id: null,
            district_id: null,
            assigned_to_id: null,
            inspection_type_id: null,
            case_priority_id: null,
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
          parent_update_function: {
              type: Function,
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
    },
    filters: {
      formatDate: function(data) {
          return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
      }
    },
    methods: {
      ...mapActions('inspectionStore', {
          saveInspection: 'saveInspection'
      }),
      loadAllocatedGroup: async function() {
          let url = helpers.add_endpoint_join(
              api_endpoints.region_district,
              this.regionDistrictId + '/get_group_id_by_region_district/'
              );
          let returned = await Vue.http.post(
              url,
              { 'group_permission': 'officer'
              });
          return returned;
      },
      updateDistricts: function() {
        // this.district_id = null;
        this.availableDistricts = [];
        for (let record of this.regionDistricts) {
          if (this.region_id === record.id) {
            for (let district of record.districts) {
              for (let district_record of this.regionDistricts) {
                if (district_record.id === district) {
                  this.availableDistricts.push(district_record)
                }
              }
            }
          }
        }
        console.log(this.availableDistricts);
        this.availableDistricts.splice(0, 0, 
        {
          id: "", 
          display_name: "",
          district: "",
          districts: [],
          region: null,
        });
        // ensure security group members list is up to date
        this.updateAllocatedGroup();
      },
      updateAllocatedGroup: async function() {
          console.log("updateAllocatedGroup");
          this.errorResponse = "";
          if (this.regionDistrictId) {
              let allocatedGroupResponse = await this.loadAllocatedGroup();
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
              // For Inspection Dashboard
              if (this.$parent.$refs.inspection_table) {
                  this.$parent.$refs.inspection_table.vmDataTable.ajax.reload()
              }
              // For CallEmail related items table
              if (this.$parent.call_email) {
                  await this.parent_update_function({
                      call_email_id: this.$parent.call_email.id,
                  });
              }
              if (this.$parent.$refs.related_items_table) {
                  this.$parent.constructRelatedItemsTable();
              }
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
          let post_url = '';
          if (this.inspection && this.inspection.id) {
              post_url = '/api/inspection/' + this.inspection.id + '/add_workflow_log/'
          } else {
                post_url = '/api/inspection/'
          }
          let payload = new FormData(this.form);
          payload.append('details', this.workflowDetails);
          if (this.$refs.comms_log_file.commsLogId) {
              payload.append('inspection_comms_log_id', this.$refs.comms_log_file.commsLogId)
          }
          if (this.$parent.call_email) {
              payload.append('call_email_id', this.$parent.call_email.id)
          }

          //payload.append('email_subject', this.modalTitle);
          if (this.district_id) {
              payload.append('district_id', this.district_id);
          }
          if (this.assigned_to_id) {
              payload.append('assigned_to_id', this.assigned_to_id);
              //payload.append('inspection_team_lead_id', this.assigned_to_id);
          }
          if (this.inspection_type_id) {
              payload.append('inspection_type_id', this.inspection_type_id);
          }
          if (this.region_id) {
              payload.append('region_id', this.region_id);
          }
          if (this.allocated_group_id) {
              payload.append('allocated_group_id', this.allocated_group_id);
          }

          try {
              let res = await Vue.http.post(post_url, payload);
              console.log(res);
              if (res.ok) {
                return res
              }
          } catch(err) {
                  this.errorResponse = err.statusText;
              }
          
      },
      createDocumentActionUrl: async function() {
        // create inspection and get id
        let returned_inspection = await Vue.http.post(api_endpoints.inspection);
        this.inspection.id = returned_inspection.body.id;
    
        return helpers.add_endpoint_join(
            api_endpoints.inspection,
            this.inspection.id + "/create_modal_process_comms_log_document/"
            )
      },

    },
    created: async function() {
        // regions
        let returned_regions = await cache_helper.getSetCacheList('CallEmail_Regions', '/api/region_district/get_regions/');
        Object.assign(this.regions, returned_regions);
        // blank entry allows user to clear selection
        this.regions.splice(0, 0, 
            {
              id: "", 
              display_name: "",
              district: "",
              districts: [],
              region: null,
            });
        // regionDistricts
        let returned_region_districts = await cache_helper.getSetCacheList(
            'CallEmail_RegionDistricts', 
            api_endpoints.region_district
            );
        Object.assign(this.regionDistricts, returned_region_districts);

        await this.updateAllocatedGroup();

        // case_priorities
        let returned_case_priorities = await cache_helper.getSetCacheList(
            'CallEmail_CasePriorities', 
            api_endpoints.case_priorities
            );
        Object.assign(this.casePriorities, returned_case_priorities);
        // blank entry allows user to clear selection
        this.casePriorities.splice(0, 0, 
            {
              id: "", 
              description: "",
            });

        // inspection_types
        let returned_inspection_types = await cache_helper.getSetCacheList(
            'InspectionTypes',
            api_endpoints.inspection_types
            );
        Object.assign(this.inspectionTypes, returned_inspection_types);
        // blank entry allows user to clear selection
        this.inspectionTypes.splice(0, 0, 
            {
              id: "", 
              description: "",
            });

        // referrers
        let returned_referrers = await cache_helper.getSetCacheList('CallEmail_Referrers', '/api/referrers.json');
        Object.assign(this.referrers, returned_referrers);
        // blank entry allows user to clear selection
        this.referrers.splice(0, 0, 
            {
              id: "", 
              name: "",
            });
    },
    mounted: function() {
        this.form = document.forms.forwardForm;
      
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
