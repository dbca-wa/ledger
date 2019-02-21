<template>
  <form method="POST" name="enter_return_sheet" enctype="multipart/form-data">
  <div class="container" id="externalReturnSheet">
    <div class="row">
      <div class="col-md-3">
        <h3>Return: {{ returns.id }}</h3>
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
                        <div class="row">
                          <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Type:</label>
                                <select class="form-control" v-model="filterReturnSpeciesType">
                                    <option value="All">All</option>
                                    <option v-for="lt in return_licence_types" :value="lt">{{lt}}</option>
                                </select>
                            </div>
                          </div>
                        </div>
                        <div class = "row">
                          <div class="col-lg-12">
                            <datatable ref="return_datatable" :id="datatable_id" :dtOptions="sheet_options" :dtHeaders="sheet_headers"/>
                          </div>
                        </div>
                      </div>
                      <!-- End of Sheet Return -->
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
  </div>
  </form>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import $ from 'jquery'
import Vue from 'vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturnSheet',
  props: {
     url:{
        type: String,
        required: true
     }
  },
  data() {
    let vm = this;
    return {
        pdBody: 'pdBody' + vm._uid,
        datatable_id: 'return-datatable-'+vm._uid,
        returns: {
            table: [{
                data: null
            }],
        },
        returnTab: 'returnTab'+vm._uid,
        form: null,
        returnBtn: 'Submit',
        sheet_headers:["Date","Type","Number","Total Number","Comments","Action"],
        sheet_options:{
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive: true,
            ajax: {
                "url": helpers.add_endpoint_json(api_endpoints.returns,'sheet_details'),
                "dataSrc": ''
            },
            columns: [
              {
                data: "date",
                mRender:function (data,type,full) {

                    return full.table[0]['data'][0]['DATE']['value'];
                }
              },
              {
                data: "type",
                mRender:function (data,type,full) {

                    return full.table[0]['data'][0]['TYPE']['value'];
                }
              },
              {
                data: "number",
                mRender:function (data,type,full) {

                    return full.table[0]['data'][0]['NUMBER']['value'];
                }
              },
              {
                data: "total",
                mRender:function (data,type,full) {

                    return full.table[0]['data'][0]['TOTAL NUMBER']['value'];
                }
              },
              {
                data: "comment",
                mRender:function (data,type,full) {

                    return full.table[0]['data'][0]['COMMENTS']['value'];
                }
              },
              {
                mRender:function (data,type,full) {

                    return `<a href='/internal/application/${full.id}'>Edit</a><br/>`;
                }
              },
            ],
            processing: true,
            initComplete: function () {
            }
        }
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
      vm.form=document.forms.enter_return_sheet
    },
    addEventListeners: function() {
      let vm = this;
    },
    initialiseSearch:function() {
    },
    filterSpeciesType: function(){
    },
  },
  components:{
    datatable
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
     //vm.form = document.forms.enter_return_question;

     $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
         var chev = $( this ).children()[ 0 ];
         window.setTimeout( function () {
            $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
         }, 100 );
     });
     this.$nextTick(() => {
       vm.addEventListeners();
       vm.initialiseSearch();
     });
  },

}
</script>
