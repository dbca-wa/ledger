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
                                                        <label>
                                                          <input type="radio"  name="NilYes" value="yes" v-model='returns.nil'> yes
                                                        </label>
                                                        <label>
                                                          <input type="radio"  name="NilNo" value="no" v-model='returns.nil'> no
                                                        </label>
                                                </div>
                                                <div class="row">
                                                    <label class="col-sm-4">Do you want to upload spreadsheet with Return data?</label>
                                                        <label>
                                                          <input type="radio"  name="SpreadsheetYes" value="yes" v-model='returns.spreadsheet'> yes
                                                        </label>
                                                        <label>
                                                          <input type="radio"  name="SpreadsheetNo" value="no" v-model='returns.spreadsheet'> no
                                                        </label>
                                                </div>
                                                <div v-if="returns.spreadsheet =='yes'" class="row">
                                                    <label class="col-sm-4">Do you want the data in spreadsheet added to or replace existing data?</label>
                                                        <label>
                                                          <input type="radio"  name="ReplaceYes" value="replace" v-model='returns.replace'> Replace
                                                        </label>
                                                        <label>
                                                          <input type="radio"  name="ReplaceNo" value="add" v-model='returns.replace'> Add to
                                                        </label>
                                                </div>
                                                <div v-if="returns.spreadsheet =='yes'" class="row">
                                                  
                                                  <table class="return-table table table-striped table-bordered dataTable">
                                                    <thead>
                                                      <tr>
                                                        <div v-for="(item,index) in returns.table">
                                                        <th v-f="item.headers" v-for="header in item.headers">{{header.title}}
                                                          </div>
                                                        <!-- <th v-for="header in returns.table.headers">{{header.title}} -->
                                                        </th>
                                                      </tr>
                                                    </thead>
                                                    <tbody>
                                                      <tr>
                                                        <div v-for="(item,index) in returns.table">
                                                        <td v-if="item.headers" v-for="header in item.headers">
                                                          
                                                          <input v-for="(title,key) in item.data" v-if="key == header.title" class="form-control returns" :name="`${item.name}::${header.title}`" :data-species="`${header.species}`" v-model="title.value">

                                                        </td>
                                                      </div>
                                                      </tr>
                                                    </tbody>
                                                  </table>
                                                  
                                                </div>
                                                <div class="margin-left-20">
                                                </div>
                                                
                                            </div>

                                    </div>
                                </div>

                            </div>
                          
                    </div>
                    <input type='hidden' name="table_name" :value="returns.table[0].name" />
                    <button type="submit" class="btn btn-primary pull-right" name="lodge">Lodge</button>
                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                    <button type="submit" class="btn btn-info pull-right" style="margin-right: 20px;" name="draft">Save Draft
                    </button>
                    
                </template>
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
        "returns":null,
        returnTab: 'returnTab'+vm._uid,
        form:null,
                    
    }
  },
  methods: {
    save: function(e) {
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

      // console.log("from save")
      // console.log(document.forms.enter_return)
      // console.log(vm.form)
      // console.log(data)

       // vm.$http.post('/api/returns.json',JSON.stringify(returns),{
        vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/update_details'),data,{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        swal(
                             'Sent',
                             'successful returns',
                             'success'
                        );
                        // vm.amendingApplication = true;
                        // vm.close();
                        // //vm.$emit('refreshFromResponse',response);
                        // Vue.http.get(`/api/application/${vm.application_id}/internal_application.json`).then((response)=>
                        // {
                        //     vm.$emit('refreshFromResponse',response);
                            
                        // },(error)=>{
                        //     console.log(error);
                        // });
                        // vm.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request
                     
                    },(error)=>{
                        console.log(error);
                        // vm.errors = true;
                        // vm.errorString = helpers.apiVueResourceError(error);
                        // vm.amendingApplication = true;
                        
                    });
    },
    getReturnData: function(title){
      let vm=this;
      console.log(title)
      console.log(vm.returns.table.data[title].value)
      return vm.returns.table.data[title].value
     
    },
  },
  beforeRouteEnter: function(to, from, next) {
    console.log(to.params)
     Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
          next(vm => {
            console.log('fetching returns')
            vm.returns = res.body;
            // vm.loading.splice('fetching application', 1);
            // vm.setdata(vm.application.readonly);
          });
        },
        err => {
          console.log(err);
        });
   },
   mounted: function(){
        let vm = this;

        vm.form = document.forms.enter_return;
        console.log("from mounted")
        console.log(vm.form)
            
    },

}
</script>