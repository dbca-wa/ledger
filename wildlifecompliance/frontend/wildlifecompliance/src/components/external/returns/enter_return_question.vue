<template>
  <form method="POST" name="enter_return_question" enctype="multipart/form-data">
  <div class="container" id="externalReturnQuestion">

    <Returns v-if="isReturnsLoaded">
    <div class="row">

      <!-- div class="col-md-1" div -->
      <div class="col-md-8">
        <div class="row">
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
                    <div class="col-sm-16">
                      <div>
                        <div v-for="(item,index) in returns.table">
                          <tr v-for="(question,key) in item.headers">
                            <div v-for="answer in item.data">
                              <renderer-block :component="question" :json_data="answer.value" v-bind:key="`q_${key}`"/>
                            </div>
                          </tr>
                        </div>
                      </div>
                      <!-- End of Question Return -->
                    </div>
                  </div>
                </div>

            <input type='hidden' name="table_name" :value="returns.table[0].name" />
          </template>
          <!-- End template for Return Tab -->
          <div class="row" style="margin-bottom:50px;">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
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
    </Returns>
  </div>
  </form>
</template>

<script>
import Returns from '../../returns_form.vue'
import { mapActions, mapGetters } from 'vuex'
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
        pdBody: 'pdBody' + vm._uid,
        form: null,
        returnBtn: 'Submit',
        dateFormat: 'DD/MM/YYYY',
        datepickerOptions:{
            format: 'DD/MM/YYYY',
            showClear:true,
            useCurrent:false,
            keepInvalid:true,
            allowInputToggle:true
        },
        filterAnswerDatePicker: '',
    }
  },
  components: {
    Returns,
  },
  computed: {
    ...mapGetters([
        'isReturnsLoaded',
        'returns',
    ]),
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
    ]),
    addEventListeners: function(){
      let vm = this;
      // Initialise Application Date Filters
      //$(vm.$refs.answerDatePicker).data('date') = '27/02/2019';
      $(vm.$refs.answerDatePicker).datetimepicker(vm.datepickerOptions);
      $(vm.$refs.answerDatePicker).on('dp.change', function(e){
         if ($(vm.$refs.answerDatePicker).data('DateTimePicker').date()) {
            vm.filterAnswerDatePicker =  e.date.format('DD/MM/YYYY');
         }
         else if ($(vm.$refs.answerDatePicker).data('date') === "") {
            vm.filterAnswerDatePicker = "27/02/2019";
         }
      });
    },
  },
  beforeRouteEnter: function(to, from, next) {
     next(vm => {
       vm.load({ url: `/api/returns/${to.params.return_id}.json` })
     });

  },
}
</script>
