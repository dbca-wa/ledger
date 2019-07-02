<template lang="html">
    <div id="CallWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div v-if="regionVisibility" class="form-group">
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
                        <div v-if="regionVisibility" class="form-group">
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
                        <div v-if="regionVisibility" class="form-group">
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

                        <div v-if="workflow_type === 'allocate_for_inspection'" class="form-group">
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

                        <div v-if="workflow_type === 'allocate_for_case'" class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Priority</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="case_priority_id">
                                <option  v-for="option in casePriorities" :value="option.id" v-bind:key="option.id">
                                  {{ option.description }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div v-if="workflow_type === 'close'" class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Referred To</label>
                            </div>
                            <div class="col-sm-9">
                              <select multiple class="form-control" v-model="referrers_selected">
                                <option  v-for="option in referrers" :value="option.id" v-bind:key="option.id">
                                  {{ option.name }} 
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
				  <textarea v-if="workflow_type === 'close'" class="form-control" placeholder="add details" id="details" v-model="advice_details"/>
                                  <textarea v-else class="form-control" placeholder="add details" id="details" v-model="workflowDetails"/>
                              </div>
                          </div>
                        </div>
                  <form class="form-horizontal" name="forwardForm">
                    <div class="form-group">
                      <div class="row">
                          <div class="col-sm-3">
                              <label class="control-label pull-left"  for="Name">Attachments</label>
                          </div>
                          <div class="col-sm-9">
                              <template v-for="(f,i) in files">
                                  <div :class="'row top-buffer file-row-'+i">
                                      <div class="col-sm-4">
                                          <span v-if="f.file == null" class="btn btn-info btn-file pull-left">
                                              Attach File <input type="file" :id="'workflow-file-upload-'+i" :name="'workflow-file-upload-'+i" :class="'workflow-file-upload-'+i" @change="uploadFile('workflow-file-upload-'+i,f)"/>
                                          </span>
                                          <span v-else class="btn btn-info btn-file pull-left">
                                              Update File <input type="file" :id="'workflow-file-upload-'+i" :name="'workflow-file-upload-'+i" :class="'workflow-file-upload-'+i" @change="uploadFile('workflow-file-upload-'+i,f)"/>
                                          </span>
                                      </div>
                                      <div class="col-sm-4">
                                          <span>{{f.name}}</span>
                                      </div>
                                      <div class="col-sm-4">
                                          <button @click="removeFile(i)" class="btn btn-danger">Remove</button>
                                      </div>
                                  </div>
                              </template>
                              <a href="" @click.prevent="attachAnother"><i class="fa fa-lg fa-plus top-buffer-2x"></i></a>
                          </div>
                        </div>
                    </div>
                  </form>

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

export default {
    name: "CallEmailWorking",
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
            files: [
                    {
                        'file': null,
                        'name': ''
                    }
                ]
      }
    },
    components: {
      modal,
    },
    props:{
          workflow_type: {
              type: String,
              default: '',
          },
      },
    computed: {
      ...mapGetters('callemailStore', {
        call_email: "call_email",
      }),
      regionVisibility: function() {
        if (!(this.workflow_type === 'forward_to_wildlife_protection_branch' || 
          this.workflow_type === 'close')
        ) {
              return true;
        } else {
              return false;
        }
      },
      groupPermission: function() {
        if (this.workflow_type === 'forward_to_regions') {
            return 'triage_call_email';
        } else if (this.workflow_type === 'forward_to_wildlife_protection_branch') {
              return 'triage_call_email';
        } else if (this.workflow_type === 'allocate_for_follow_up') {
              return 'officer';
        } else if (this.workflow_type === 'allocate_for_inspection') {
              return 'officer';
        } else if (this.workflow_type === 'allocate_for_case') {
              return 'officer';
        } else if (this.workflow_type === 'close') {
              return "";
        }
      },
      modalTitle: function() {
        if (this.workflow_type === 'forward_to_regions') {
            return "Forward to Regions";
        } else if (this.workflow_type === 'forward_to_wildlife_protection_branch') {
              return "Forward to Wildlife Protection Branch";
        } else if (this.workflow_type === 'allocate_for_follow_up') {
              return "Allocate for Follow Up";
        } else if (this.workflow_type === 'allocate_for_inspection') {
              return "Allocate for Inspection";
        } else if (this.workflow_type === 'allocate_for_case') {
              return "Allocate for Case";
        } else if (this.workflow_type === 'close') {
              return "Close complaint";
        }
      },
      regionDistrictId: function() {
          if (this.district_id || this.region_id) {
              console.log("local var");
              return this.district_id ? this.district_id : this.region_id;
          } else {
                console.log("vuex");
                return this.call_email.district_id ? this.call_email.district_id : this.call_email.region_id;
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
          saveCallEmail: 'saveCallEmail'
      }),
      loadAllocatedGroup: async function() {
          let url = helpers.add_endpoint_join(
              api_endpoints.region_district,
              this.regionDistrictId + '/get_group_id_by_region_district/'
              );
          let returned = await Vue.http.post(
              url,
              { 'group_permission': this.groupPermission
              });
          return returned;
      },
      updateDistricts: function() {
        this.district_id = null;
        this.availableDistricts = [];
        for (let record of this.regionDistricts) {
          if (this.region_id === (record.id)) {
            for (let district of record.districts) {
              for (let district_record of this.regionDistricts) {
                if (district_record.id === district) {
                  this.availableDistricts.push(district_record)
                }
              }
            }
          }
        }
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
          //this.allocatedGrouplength = 0;
          
          if (this.workflow_type === 'forward_to_wildlife_protection_branch') {
              for (let record of this.regionDistricts) {
                  if (record.district === 'KENSINGTON') {
                      this.district_id = null;
                      this.region_id = record.id;
                  }
              }
          }
          if (this.groupPermission && this.regionDistrictId) {
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
          if (response === 'ok') {
              this.close();
          }
      },
      cancel: function() {
          this.isModalOpen = false;
          this.close();
      },
      close: function () {
          let vm = this;
          this.isModalOpen = false;
          let file_length = vm.files.length;
          this.files = [];
          for (var i = 0; i < file_length;i++){
              vm.$nextTick(() => {
                  $('.file-row-'+i).remove();
              });
          }
          this.attachAnother();
      },
      sendData: async function(){        
          let post_url = '/api/call_email/' + this.call_email.id + '/add_workflow_log/'
          let payload = new FormData(this.form);
          payload.append('call_email_id', this.call_email.id);
          payload.append('details', this.workflowDetails);

          payload.append('workflow_type', this.workflow_type);
          payload.append('email_subject', this.modalTitle);
          payload.append('referrers_selected', this.referrers_selected);
          payload.append('district_id', this.district_id);
          payload.append('assigned_to_id', this.assigned_to_id);
          payload.append('inspection_type_id', this.inspection_type_id);
          payload.append('case_priority_id', this.case_priority_id);
          payload.append('region_id', this.region_id);
          payload.append('allocated_group_id', this.allocated_group_id);

          let callEmailRes = await this.saveCallEmail({ route: false, crud: 'save', 'internal': true });
          console.log(callEmailRes);
          if (callEmailRes.ok) {
              try {
                  let res = await Vue.http.post(post_url, payload);
                  if (res.ok) {    
                      this.$router.push({ name: 'internal-call-email-dash' });
                  }
              } catch(err) {
                  this.errorResponse = err.statusText;
              } 
          } else {
              this.errorResponse = callEmailRes.statusText;
          }
      },
      
      uploadFile(target,file_obj){
          let vm = this;
          let _file = null;
          var file_input = $('.'+target)[0];

          if (file_input.files && file_input.files[0]) {
              var reader = new FileReader();
              reader.readAsDataURL(file_input.files[0]); 
              reader.onload = function(e) {
                  _file = e.target.result;
              };
              _file = file_input.files[0];
          }
          file_obj.file = _file;
          file_obj.name = _file.name;
      },
      removeFile(index){
          let length = this.files.length;
          $('.file-row-'+index).remove();
          this.files.splice(index,1);
          this.$nextTick(() => {
              length == 1 ? this.attachAnother() : '';
          });
      },
      attachAnother(){
          this.files.push({
              'file': null,
              'name': ''
          })
      },
      
    },
    created: async function() {
        
        //await this.$parent.updateAssignedToId('blank');
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
        await this.updateDistricts();

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
            'CallEmail_InspectionTypes', 
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
