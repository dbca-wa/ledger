<template lang="html">
    <div id="CallWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div v-if="regionVisibility" class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Region</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control col-sm-9" @change.prevent="updateDistrictsAndOfficers('triage_call_email')" v-model="call_email.region">
                                <option  v-for="option in regions" :value="option" v-bind:key="option.id">
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
                              <select class="form-control" v-model="call_email.district_id" >
                                <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                  {{ option.display_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <!--

                        <div v-if="assignedToVisibility" class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Assign to</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="call_email.assigned_to">
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
                              <select class="form-control" v-model="call_email.district_id">
                                <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
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
                              <select class="form-control" v-model="call_email.district_id">
                                <option v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div v-if="workflow_type === 'close'" class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Complaint forwarded to external party for follow-up</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="call_email.district_id">
                                <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        -->

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
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
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
//import $ from 'jquery'

export default {
  name: "CallEmailWorking",
  data: function() {
    return {
      // forwardToRegions: false,
      // workflowType: '',
      officers: [],
      allocatedGroup: [],
      isModalOpen: false,
      processingDetails: false,
      form: null,
      regions: [],
      regionDistricts: [],
      availableDistricts: [],
      compliance_permission_groups: [],
      // call_email.region: null,
      // call_email.district_id: null,
      workflowDetails: '',
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
      if (this.workflow_type === 'forward_to_regions') {
        return true;
      } else {
        return false;
      }
    },
    assignedToVisibility: function() {
      if (this.workflow_type.includes('allocate')) {
        return true;
      } else {
        return false;
      }
    },
    region: function() {
      return this.call_email.region ? this.call_email.region.id : '';
    }, 
    district: function() {
      return this.call_email.district_id ? this.call_email.district_id : '';
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

  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ...mapActions('callemailStore', {
      setAllocatedTo: "setAllocatedTo",
    }),
    updateDistrictsAndOfficers: function(group_permission) {
      this.call_email.district_id = null;
      this.availableDistricts = [];
      for (let record of this.regionDistricts) {
        if (this.call_email.region && this.call_email.region.districts.includes(record.id)) {
          this.availableDistricts.push(record)
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
      this.setAllocatedGroup(group_permission);
    },
    setAllocatedGroup: function(group_permission) {
      this.allocatedGroup = [];
      let member_ids = [];
      for (let group of this.compliance_permission_groups) {
        if (group.region_district.length > 0 && 
        group.members.length > 0 && 
        this.call_email.region.id &&
        // parent or child Region/District
        (group.region_district[0].region == this.call_email.region.id ||
        group.region_district[0].id == this.call_email.region.id) &&
        // filter by group permission
        group.permissions_list &&
        group.permissions_list.includes(group_permission)
        ) {
          console.log(group)
          console.log(group.permissions_list)
          console.log(group_permission)
          for (let member of group.members) {
            this.allocatedGroup.push(member);
            member_ids.push(member.id);  
          }
        }
      }
      this.setAllocatedTo(member_ids);
      // blank entry allows user to clear selection
      this.allocatedGroup.splice(0, 0, 
      {
        id: "", 
        full_name: "",
      });
    },

    ok: async function () {
        await this.sendData();
        this.close();
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
        this.call_email.region = null;
        this.call_email.district_id = null;
        this.workflowDetails = '';
    },
    sendData: async function(){        
        let post_url = '/api/call_email/' + this.call_email.id + '/add_workflow_log/'
        let payload = new FormData(this.form);
        payload.append('call_email_id', this.call_email.id);
        if (this.call_email.region) {
          payload.append('region_id', this.call_email.region.id);
        }
        if (this.call_email.district_id) {
          payload.append('district_id', this.call_email.district_id);
        }
        if (this.call_email.allocated_to) {
          payload.append('allocated_to_group', this.call_email.allocated_to);
        }
        if (this.call_email.assigned_to) {
          payload.append('assigned_to', this.call_email.assigned_to);
        }
        
        payload.append('details', this.workflowDetails);
        payload.append('workflow_type', this.workflow_type);
        
        let res = await this.$http.post(post_url, payload);
        console.log(this);
        if (res.ok) {
          // this.$parent.save();
          this.$router.push({ name: 'internal-call-email-dash' });

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
    let returned_region_districts = await cache_helper.getSetCacheList('CallEmail_RegionDistricts', '/api/region_district/');
    Object.assign(this.regionDistricts, returned_region_districts);

    // CompliancePermissionGroups
    let returned_compliance_permission_groups = await cache_helper.getSetCacheList('CallEmail_CompliancePermissionGroup_Members', '/api/compliancepermissiongroup/get_detailed_list/');
    Object.assign(this.compliance_permission_groups, returned_compliance_permission_groups);

    // CompliancePermissionGroups - officers
    let returned_officers = await cache_helper.getSetCacheList('CallEmail_CompliancePermissionGroup_Officers', '/api/compliancepermissiongroup/get_officers/');
    Object.assign(this.officers, returned_officers);
    // blank entry allows user to clear selection
    this.officers.splice(0, 0, 
      {
        id: "", 
        full_name: "",
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
