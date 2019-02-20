<template>
  <form method="POST" name="enter_return_question" enctype="multipart/form-data">
  <div class="container" id="externalReturnQuestion">
    <div class="row">
      <div class="col-md-3">
        <h3>Question Return: {{ returns.id }}</h3>
      </div>
      <!-- div class="col-md-1" div -->
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
                        <label style="width:70%;" class="col-sm-4">Do you want to Lodge a nil Return?</label>
                        <input type="radio" id="nilYes" name="nilYes" value="yes" v-model='returns.nil'>
                        <label style="width:10%;" for="nilYes">Yes</label>
                        <input type="radio" id="nilNo" name="nilNo" value="no" v-model='returns.nil'>
                        <label style="width:10%;" for="nilNo">No</label>
                      </div>
                      <div v-if="returns.nil == 'yes'" class="row">
                        <label style="width:70%;" class="col-sm-4">Reason for providing a Nil return.</label>
                        <input type="textarea" name="nilReason" v-model="returns.nilReason">
                      </div>
                      <div v-if="returns.nil == 'no'">
                        <div v-for="(item,index) in returns.table">
                          <tr v-for="question in item.headers">
                            <div v-for="(answer,key) in item.data">
                              <td style="width:85%;">
                              <strong>{{ question.title }}</strong>
                              </td>
                              <td>
                              <input v-if="question.type != 'date'" v-model="answer.value">
                              <div v-if="question.type == 'date'" class="input-group date" ref="answerDatePicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="answer.value">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                              </div>
                              </td>
                            </div>
                          </tr>
                        </div>
                      </div>
                      <!-- End of Question Return -->
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <input type='hidden' name="table_name" :value="returns.table[0].name" />
          </template>
          <!-- End template for Return Tab -->
          <div class="row" style="margin-bottom:50px;">
            <div v-if="wc_version != 1.0" class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
              <div class="navbar-inner">
                <div class="container">
                  <p class="pull-right" style="margin-top:5px;">
                    <button class="btn btn-primary" name="save_exit">Save and Exit</button>
                    <button class="btn btn-primary" @click.prevent="save()" name="save_continue">Save and Continue</button>
                    <button class="btn btn-primary" name="draft">{{returnBtn}}</button>
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
  name: 'externalReturnQuestion',
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
        returnBtn: 'Submit',
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
    },
    submit: function(e) {
      console.log('SUBMIT func()')
      let vm = this;
      vm.form=document.forms.enter_return_question
    },
    init: function() {
      console.log('INIT FUNC')

      // TODO: set return button for payment.
      // returnBtn = return.requires_payment ? 'Pay and Submit' : 'Submit'

    }

  },
  computed: {

  },
  beforeRouteEnter: function(to, from, next) {
    console.log('BEFORE-ROUTE func()')
     Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
        next(vm => {
           vm.returns = res.body;
           console.log(vm.returns);

        // TODO: set return button if requires payment.
        // if (vm.returns.requires_pay)
        //   returnBtn = 'Pay and Submit'
        // }
        });
     }, err => {
        console.log(err);
     });
   },
   mounted: function(){
       console.log('MOUNTED func()')
        let vm = this;
        vm.form = document.forms.enter_return_question;
        console.log("from mounted")
        console.log(vm.form)

    },

}
</script>
