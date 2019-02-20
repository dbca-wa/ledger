<template>
  <form method="POST" name="enter_return" enctype="multipart/form-data">
  <div class="container" id="externalCompliance">
    <div class="row">
      <div class="col-md-3">
        <h3>Return: {{ returns.id }}</h3>
      </div>
      <div class="col-md-1">
      </div>
      <div class="col-md-8">
        <div class="row">
          <template>
            <div >
              <ul class="nav nav-tabs">
                <li ><a data-toggle="tab" :href="returnTab">Return</a></li>
              </ul>
            </div>
            <div  class="tab-content">
              <div :id="returnTab" class="tab-pane fade active in">
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
                        <label class="col-sm-4">Do you want to Lodge a nil Return?</label>
                        <input type="radio" id="nilYes" name="nilYes" value="yes" v-model='returns.nil'>
                        <label style="width:10%;" for="nilYes">Yes</label>
                        <input type="radio" id="nilNo" name="nilNo" value="no" v-model='returns.nil'>
                        <label style="width:10%;" for="nilNo">No</label>
                      </div>
                      <div v-if="returns.nil =='no'" class="row">
                        <label class="col-sm-4">Do you want to add to existing data or replace existing data?</label>
                        <input type="radio" name="ReplaceYes" value="replace" v-model='returns.replace'>
                        <label style="width:10%;" for="ReplaceYes">Replace</label>
                        <input type="radio" name="ReplaceNo" value="add" v-model='returns.replace'>
                        <label style="width:10%;" for="ReplaceNo">Add to</label>
                      </div>
                      <div v-if="returns.nil == 'no'" class="row">
                        <label class="col-sm-4">Do you want to upload spreadsheet with Return data?</label>
                        <input type="radio" name="SpreadsheetYes" value="yes" v-model='returns.spreadsheet'>
                        <label style="width:10%;" for="SpreadsheetYes">Yes</label>
                        <input type="radio" name="SpreadsheetNo" value="no" v-model='returns.spreadsheet'>
                        <label style="width:10%;" for="SpreadsheetNo">No</label>
                      </div>
                      <div v-if="returns.nil == 'yes'" class="row">
                        <label class="col-sm-4">Reason for providing a Nil return.</label>
                        <input type="textarea" name="nilReason" v-model="returns.nilReason">
                      </div>
                      <div v-if="returns.spreadsheet =='no'" class="row">
                        <table class="return-table table table-striped table-bordered dataTable">
                        <thead>
                        <tr>
                          <div v-for="(item,index) in returns.table">
                            <th v-f="item.headers" v-for="header in item.headers">{{header.title}}</th>
                          </div>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                          <div v-for="(item,index) in returns.table">
                            <td v-if="item.headers" v-for="header in item.headers">
                              <div v-for ="item1 in item.data">
                                <input v-for="(title,key) in item1" v-if="key == header.title" class="form-control returns" :name="`${item.name}::${header.title}`" :data-species="`${header.species}`" v-model="title.value">
                              </div>
                            </td>
                          </div>
                        </tr>
                        </tbody>
                        </table>
                      </div>
                      <div v-if="returns.nil === 'no' && returns.spreadsheet === 'yes'" class="row">
                        <a v-bind:href="url" class="pull-right">Download (XLSX)</a>
                        <span class="btn btn-primary btn-file pull-left">Upload File
                          <input type="file" ref="spreadsheet" @change="uploadFile()"/>
                        </span>
                        <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                      </div>
                      <div class="margin-left-20"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <input type='hidden' name="table_name" :value="returns.table[0].name" />
            <!-- button type="submit" class="btn btn-primary pull-right" name="lodge">Save and Exit</button -->
            <!-- input type="button" @click.prevent="save" class="btn btn-primary" name="save_continue" Save and Continue -->
            <!-- button type="submit" class="btn btn-info pull-right" style="margin-right: 20px;" name="draft">Submit button -->
          </template>
          <!-- End template for Return Tab -->
          <div class="row" style="margin-bottom:50px;">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
              <div class="navbar-inner">
                <div class="container">
                  <p class="pull-right" style="margin-top:5px;">
                    <button class="btn btn-primary" name="save_exit">Save and Exit</button>
                    <button class="btn btn-primary" @click.prevent="save()" name="save_continue">Save and Continue</button>
                    <button class="btn btn-primary" name="draft">Submit</button>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </form>
</template>

<script>
import $ from 'jquery'
import Vue from 'vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturn',
  data() {
    let vm = this;
    return {
        returns: {
            table: [{
                data: null
            }],
        },
        returnTab: 'returnTab'+vm._uid,
        form: null,
        spreadsheet: null,
    }
    returns: null
  },
  methods: {
    save: function(e) {
      console.log('SAVE func()')
      let vm = this;
      vm.form=document.forms.enter_return
      let data = new FormData(vm.form);
      console.log(data)
      console.log(JSON.stringify(data))
      // console.log('printing table name')
      // console.log(vm.returns.table[0].name)
      // data.returns_name=vm.returns.table[0].name
      // data.id=vm.returns.id
      // data.application=vm.returns.application
      // data.table=vm.returns.table

      // $('.returns').each((i,d) => {
      //   console.log( $(d).data('species'))

      // })

       // vm.$http.post('/api/returns.json',JSON.stringify(returns),{
      console.log('TEST')
      console.log(vm.returns.spreadsheet)
      if (vm.returns.spreadsheet == 'no') {
        console.log('not entered spreadsheet')
        vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/update_details'),data,{
		emulateJSON:true,
	    }).then((response)=>{
		swal(
		     'Sent',
		     'successful returns',
		     'success'
		);

	    },(error)=>{
		console.log(error);
		swal(
		     'error',
		     'Enter data in correct format',
		     'error'
		);
	    });
      }
      if (vm.returns.spreadsheet == 'yes') {
        data.append('spreadsheet', vm.spreadsheet)
        vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/upload_details'),data,{
                    emulateJSON:true,
        }).then((res)=>{
                swal(
                  'Saved',
                  'Return details have been updated',
                 'success'
                )
        },err=>{
                console.log(err)
        });
      }
    },
    uploadFile: function(e) {
      console.log('uploadFile')
      let vm = this;
      let _file = null;
      var input = $(vm.$refs.spreadsheet)[0];
      console.log(input)
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.readAsDataURL(input.files[0]);
          reader.onload = function(e) {
            _file = e.target.result;
          };
          _file = input.files[0];
        }
        vm.spreadsheet = _file;
        console.log(vm.spreadsheet)
    },
    submit: function(e) {
      console.log('SUBMIT func()')
      let vm = this;
      vm.form=document.forms.enter_return
      let data = new FormData(vm.form);
      // console.log('printing table name')
      // console.log(vm.returns.table[0].name)
      // data.returns_name=vm.returns.table[0].name
      // data.id=vm.returns.id
      // data.application=vm.returns.application
      // data.table=vm.returns.table

      // $('.returns').each((i,d) => {
      //   console.log( $(d).data('species'))

      // })

      

       // vm.$http.post('/api/returns.json',JSON.stringify(returns),{
        vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/update_details'),data,{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                             'Sent',
                             'successful returns',
                             'success'
                        );
                    },(error)=>{
                        console.log(error);
                    });
    },
    
  },
  computed: {
    uploadedFileName: function() {
      return this.spreadsheet != null ? this.spreadsheet.name: '';
    },
  },
  beforeRouteEnter: function(to, from, next) {
    console.log('BEFORE-ROUTE func()')
    console.log(to.params)
     Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
          next(vm => {
            console.log('fetching returns')
            vm.returns = res.body;
            console.log(vm.returns)
            // vm.loading.splice('fetching application', 1);
            // vm.setdata(vm.application.readonly);
          });
        },
        err => {
          console.log(err);
        });
   },
   mounted: function(){
       console.log('MOUNTED func()')
        let vm = this;

        vm.form = document.forms.enter_return;
        console.log("from mounted")
        console.log(vm.form)
            
    },

}
</script>
