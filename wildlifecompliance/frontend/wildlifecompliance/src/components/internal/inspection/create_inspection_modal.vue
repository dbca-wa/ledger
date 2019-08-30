<template lang="html">
    <div id="InspectionWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Create New Inspection" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div class="form-group" v-if="!this.workflow_type">
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
                        <div class="form-group" v-if="!this.workflow_type">
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
                                  {{ option.inspection_type }}
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
                                    <filefield ref="comms_log_file" name="comms-log-file" :isRepeatable="true" :documentActionUrl="inspection.createInspectionProcessCommsLogsDocumentUrl" @create-parent="createDocumentActionUrl"/>
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
                            <strong>
                                <span style="white-space: pre;">{{ errorResponse }}</span>
                            </strong>
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
import { required, minLength, between } from 'vuelidate/lib/validators'

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
    validations: {
        region_id: {
            required,
        },
        assigned_to_id: {
            required,
        },
        inspection_type_id: {
            required,
        },
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
      ...mapGetters('callemailStore', {
        call_email: "call_email",
      }),
      parent_call_email: function() {
          if (this.call_email && this.call_email.id) {
              return true;
          }
      },
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
          saveInspection: 'saveInspection',
          loadInspection: 'loadInspection',
          setInspection: 'setInspection',
      }),
      ...mapActions({
          loadAllocatedGroup: 'loadAllocatedGroup',
      }),
      ...mapActions('callemailStore', {
          loadCallEmail: 'loadCallEmail',
      }),
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
              let allocatedGroupResponse = await this.loadAllocatedGroup({
              region_district_id: this.regionDistrictId,
              group_permission: 'officer',
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
          } else {
              this.allocatedGroup = [];
          }
      },

      ok: async function () {
          let is_valid_form = this.isValidForm();
          if (is_valid_form) {
              const response = await this.sendData();
              console.log(response);
              if (response.ok) {
                  // For Inspection Dashboard
                  if (this.$parent.$refs.inspection_table) {
                      this.$parent.$refs.inspection_table.vmDataTable.ajax.reload()
                  }
                  // For CallEmail related items table
                  if (this.parent_call_email) {
                      //await this.parent_update_function({
                      await this.loadCallEmail({
                          call_email_id: this.call_email.id,
                      });
                  }
                  if (this.$parent.$refs.related_items_table) {
                      this.$parent.constructRelatedItemsTable();
                  }
                  this.close();
                  //this.$router.push({ name: 'internal-inspection-dash' });
              }
          }
      },
      isValidForm: function() {
          console.log("performValidation");
          this.$v.$touch();
          if (this.$v.$invalid) {
              this.errorResponse = 'Invalid form:\n';
              if (this.$v.region_id.$invalid) {
                  this.errorResponse += 'Region is required\n';
              }
              if (this.$v.assigned_to_id.$invalid) {
                  this.errorResponse += 'Officer must be assigned\n';
              }
              if (this.$v.inspection_type_id.$invalid) {
                  this.errorResponse += 'Choose Inspection Type\n';
              }
              return false;
          } else {
              return true;
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
              post_url = '/api/inspection/' + this.inspection.id + '/workflow_action/'
          } else {
                post_url = '/api/inspection/'
          }
          let payload = new FormData();
          payload.append('details', this.workflowDetails);
          this.$refs.comms_log_file.commsLogId ? payload.append('inspection_comms_log_id', this.$refs.comms_log_file.commsLogId) : null;
          this.parent_call_email ? payload.append('call_email_id', this.call_email.id) : null;
          this.district_id ? payload.append('district_id', this.district_id) : null;
          this.assigned_to_id ? payload.append('assigned_to_id', this.assigned_to_id) : null;
          this.inspection_type_id ? payload.append('inspection_type_id', this.inspection_type_id) : null;
          this.region_id ? payload.append('region_id', this.region_id) : null;
          this.allocated_group_id ? payload.append('allocated_group_id', this.allocated_group_id) : null;
          this.workflow_type ? payload.append('workflow_type', this.workflow_type) : null;
          //!payload.has('allocated_group') ? payload.append('allocated_group', this.allocatedGroup) : null;

          try {
              let res = await Vue.http.post(post_url, payload);
              console.log(res);
              if (res.ok) {
                  return res
              }
          } catch(err) {
                  this.errorResponse = 'Error:' + err.statusText;
              }
          
      },
      createDocumentActionUrl: async function(done) {
        if (!this.inspection.id) {
            // create inspection and update vuex
            let returned_inspection = await this.saveInspection({ route: false, crud: 'create', internal: true })
            await this.loadInspection({inspection_id: returned_inspection.body.id});
        }
        // populate filefield document_action_url
        this.$refs.comms_log_file.document_action_url = this.inspection.createInspectionProcessCommsLogsDocumentUrl;
        return done(true);
      },

    },
    created: async function() {
        // regions
        let returned_regions = await cache_helper.getSetCacheList('Regions', '/api/region_district/get_regions/');
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
            'RegionDistricts', 
            api_endpoints.region_district
            );
        Object.assign(this.regionDistricts, returned_region_districts);

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
        // If exists, get parent component details from vuex
        if (this.parent_call_email) {
            this.region_id = this.call_email.region_id;
            this.district_id = this.call_email.district_id;
        }

        // If no Region/District selected, initialise region as Kensington
        if (!this.regionDistrictId) {
            for (let record of this.regionDistricts) {
                if (record.district === 'KENSINGTON') {
                    this.district_id = null;
                    this.region_id = record.id;
                }
            }
        }
        // ensure availableDistricts and allocated group is current
        this.updateDistricts();
        await this.updateAllocatedGroup();
    },
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
