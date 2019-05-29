<template lang="html">
    <div id="CallWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Forward to Wildlife Protection Branch" large>
          <div class="container-fluid">
            <div class="row">
              

                <div class="col-sm-12">
                    
                    <div class="form-group">
                        <div class="row">
                          <label class="col-sm-4">Region</label>
                          <select class="form-control" @change.prevent="updateDistricts" v-model="selectedRegion">
                            <option  v-for="option in regions" :value="option" v-bind:key="option.id">
                              {{ option.display_name }} 
                            </option>
                          </select>
                        </div>
                        <div class="row">
                          <label>District</label>
                          <select class="form-control" v-model="call_email.district">
                            <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                              {{ option.display_name }} 
                            </option>
                          </select>
                        </div>
                        
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-left" for="details">Details</label>
                            </div>
                            <div class="col-sm-4">
                                <textarea placeholder="write text" id="details" v-model="call_email.forward_details"/>
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
                                              Attach File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
                                          </span>
                                          <span v-else class="btn btn-info btn-file pull-left">
                                              Update File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
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
      isModalOpen: false,
      processingDetails: false,
      form: null,
      regions: [],
      regionDistricts: [],
      availableDistricts: [],
      selectedRegion: null,
      //files: [],
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
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    updateDistricts: function() {
      this.availableDistricts = [];
      for (let record of this.regionDistricts) {
        if (this.selectedRegion && this.selectedRegion.districts.includes(record.id)) {
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
    },
    ok: function() {
            // if($(this.form).valid()){
            //     vm.sendData();
            // }
        this.isModalOpen = false;
        this.close();
    },
    cancel: function() {
        // let vm = this;
        // vm.close();
        this.isModalOpen = false;
        this.close();
    },
    close: function () {
        let vm = this;
        this.isModalOpen = false;
        // this.comms = {};
        // this.errors = false;
        // $('.has-error').removeClass('has-error');
        // this.validation_form.resetForm();
        let file_length = vm.files.length;
        this.files = [];
        for (var i = 0; i < file_length;i++){
            vm.$nextTick(() => {
                $('.file-row-'+i).remove();
            });
        }
        this.attachAnother();
    },
    uploadFile(target,file_obj){
        let vm = this;
        let _file = null;
        var input = $('.'+target)[0];
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.readAsDataURL(input.files[0]); 
            reader.onload = function(e) {
                _file = e.target.result;
            };
            _file = input.files[0];
        }
        console.log(file_obj)
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
    // blank entry allows user to clear selection
    
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
