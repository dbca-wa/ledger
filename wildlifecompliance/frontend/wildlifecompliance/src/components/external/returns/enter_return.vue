<template>
<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">Return
            <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
            </a>
        </h3>
    </div>
    <div class="panel-body panel-collapse in" :id="pdBody">
        <div class="col-sm-12">
            <div class="row">
                <label style="width:70%;" class="col-sm-4">Do you want to Lodge a nil Return?</label>
                <input type="radio" id="nilYes" name="nilYes" value="yes" v-model='nilReturn' :disabled='isReadOnly'>
                <label style="width:10%;" for="nilYes">Yes</label>
                <input type="radio" id="nilNo" name="nilNo" value="no" v-model='nilReturn' :disabled='isReadOnly'>
                <label style="width:10%;" for="nilNo">No</label>
            </div>
            <div v-if="nilReturn === 'yes'" class="row">
                <label style="width:70%;" class="col-sm-4">Reason for providing a Nil return.</label>
                <input type="textarea" name="nilReason" v-model="returns.nilReason">
            </div>
            <div v-if="nilReturn === 'no'" class="row">
                <label style="width:70%;" class="col-sm-4">Do you want to upload spreadsheet with Return data?<br>(Download <a v-bind:href="returns.template">spreadsheet template</a>)</label>
                <input type="radio" name="SpreadsheetYes" value="yes" v-model='spreadsheetReturn' :disabled='isReadOnly'>
                <label style="width:10%;" for="SpreadsheetYes">Yes</label>
                <input type="radio" name="SpreadsheetNo" value="no" v-model='spreadsheetReturn' :disabled='isReadOnly' >
                <label style="width:10%;" for="SpreadsheetNo">No</label>
            </div>
            <div v-if="nilReturn === 'no' && spreadsheetReturn === 'yes'" class="row">
                <label style="width:70%;" class="col-sm-4">Do you want to add to existing data or replace existing data?</label>
                <input type="radio" name="ReplaceYes" value="yes" v-model='replaceReturn' :disabled='isReadOnly'>
                <label style="width:10%;" for="ReplaceYes">Replace</label>
                <input type="radio" name="ReplaceNo" value="no" v-model='replaceReturn' :disabled='isReadOnly'>
                <label style="width:10%;" for="ReplaceNo">Add to</label>
            </div>
            <div v-if="nilReturn === 'no' && spreadsheetReturn === 'yes'" class="row">
                <span class="btn btn-primary btn-file pull-left">Upload File
                    <input type="file" ref="spreadsheet" @change="uploadFile()"/>
                </span>
                <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
            </div>
            <div class="row"></div>
            <div v-if="nilReturn === 'no'" class="row">
                <renderer-block v-for="(data, key) in returns.table"
                          :component="data"
                          v-bind:key="returns-grid-data"
                />
            </div>
            <div class="margin-left-20"></div>
            <!-- End of Spreadsheet Return -->
        </div>
    </div>
    <input type='hidden' name="table_name" :value="returns.table[0].name" />
</div>
</template>

<script>
import Vue from 'vue'
import { mapActions, mapGetters } from 'vuex'
import CommsLogs from '@common-components/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturn',
  props:["table", "data", "grid"],
  data() {
    let vm = this;
    return {
        pdBody: 'pdBody' + vm._uid,
        form: null,
        spreadsheet: null,
        returnBtn: 'Submit',
        nilReturn: 'yes',
        spreadsheetReturn: 'no',
        replaceReturn: 'no',
        readonly: false,
    }
  },
  computed: {
     ...mapGetters([
        'isReturnsLoaded',
        'returns',
        'is_external',
    ]),
    uploadedFileName: function() {
      return this.spreadsheet != null ? this.spreadsheet.name: '';
    },
    isReadOnly: function() {
      return this.readonly;
    },
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
    ]),
    uploadFile: function(e) {
      let _file = null;
      var input = $(this.$refs.spreadsheet)[0];
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.readAsDataURL(input.files[0]);
        reader.onload = function(e) {
          _file = e.target.result;
        };
        _file = input.files[0];
      }
      this.spreadsheet = _file;
      this.validate_upload()
    },
    validate_upload(e) {
      let _data = new FormData(this.form);
      _data.append('spreadsheet', this.spreadsheet)
      this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/upload_details'),_data,{
                    emulateJSON:true,
        }).then((response)=>{
            if (this.replaceReturn === 'no') {
              let idx1 = this.returns.table[0]['data'].length
              for (let idx2=0; idx2 < response.body[0]['data'].length; idx2++) {
                this.returns.table[0]['data'][idx1++] = response.body[0]['data'][idx2]
              }
            }
            if (this.replaceReturn === 'yes') {
              this.returns.table[0]['data'] = response.body[0]['data']
              this.replaceReturn = 'no'
            }
            this.nilReturn = 'no'
            this.spreadsheetReturn = 'no'
        },exception=>{
		        swal('Error Uploading', exception.body.error, 'error');
        });
    },
  },
  mounted: function(){
    var vm = this;
    vm.form = document.forms.enter_return;
    vm.readonly = !vm.is_external;
    
    if (vm.returns.table[0]) {
        vm.nilReturn = 'no'
        vm.spreadsheetReturn = 'no'
        vm.replaceReturn = 'no'
    }
  },
}
</script>
