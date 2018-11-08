<template>
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
                                        <form class="form-horizontal" name="personal_form" method="post">
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
                                                        <th v-for="header in returns.headers">{{header.title}}
                                                        </th>
                                                      </tr>
                                                    </thead>
                                                    <tbody>
                                                      <tr>
                                                        <td v-for="header in returns.headers">
                                                          <input>
                                                        </td>
                                                      </tr>
                                                    </tbody>
                                                  </table>
                                                </div>
                                                <div class="margin-left-20">
                                                </div>
                                            </div>
                                        </form>

                                    </div>
                                </div>

                            </div>
                    </div>
                </template>
            </div>
          </div>
    </div>
</div>

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

}
</script>