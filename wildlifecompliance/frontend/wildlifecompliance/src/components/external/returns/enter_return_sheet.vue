<template>
  <form method="POST" name="enter_return_sheet" enctype="multipart/form-data">
  <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
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
                    <h3 class="panel-title">Species Type 1
                      <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                         <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                      </a>
                    </h3>
                  </div>
                  <div class="panel-body panel-collapse in" :id="pdBody">
                    <div class="col-sm-12">
                        <div class="row">
                          <div class="col-md-6">
                            <div class="form-group">
                                <label for="">Activity Type:</label>
                                <select class="form-control" v-model="filterSheetActivityType">
                                    <option value="ALL">All</option>
                                    <option v-for="sa in sheet_activity_type" :value="sa">{{sa}}</option>
                                </select>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="form-group">
                                <button class="btn btn-primary pull-right" @click.prevent="addSheetRow()" name="sheet_entry">New Entry</button>
                            </div>
                          </div>
                        </div>
                        <div class = "row">
                          <div class="col-lg-12">
                            <datatable ref="return_datatable" :id="datatable_id" :dtOptions="sheet_options" :dtHeaders="sheet_headers"/>
                          </div>
                        </div>
                    <!-- End of Sheet Return -->
                    </div>
                  </div>
                </div>
                <div v-for="(item,index) in returns.sheet_species_list">
                 <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Species Type 2
                      <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                         <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                      </a>
                    </h3>
                  </div>
                  <div class="panel-body panel-collapse in" :id="pdBody">
                    <div class="col-sm-12">

                    </div>
                  </div>
                </div>
                </div>

              </div>
            </div>
          </template>
          <!-- End template for Return Tab -->
        </div>
      </div>
      <div class="row" style="margin-bottom:50px;">
        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
          <div class="navbar-inner">
            <div class="container">
              <p class="pull-right" style="margin-top:5px;">
                <button class="btn btn-primary" name="add_sheet">Add Species Type</button>
                <button class="btn btn-primary" name="save_sheet" @click.prevent="save()">Save</button>
               </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <SheetEntry ref="sheet_entry" :return_id=5 @refreshFromResponse="refreshFromResponse"></SheetEntry>
  </form>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import $ from 'jquery'
import Vue from 'vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import SheetEntry from './enter_return_sheet_entry.vue'
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
    let cnt = 0;
    return {
        pdBody: 'pdBody' + vm._uid,
        datatable_id: 'return-datatable',
        returns: {
            id: 0,
            table: [{
                data: null
            }],
        },
        returnTab: 'returnTab'+vm._uid,
        form: null,
        isModalOpen: false,
        returnBtn: 'Submit',
        sheet_activity_type: [],
        sheet_headers:["Date","Activity","Qty","Total","Comments","Action"],
        sheet_options:{
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive: true,
            ajax: {
                url: helpers.add_endpoint_json(api_endpoints.returns,'sheet_details'),
                dataSrc: '',
                type: 'GET',
                data: function(_data) {
                  _data.return_id = vm.$refs.return_datatable._uid
                  return _data;
                },
            },
            columns: [
              { data: "date",
                mRender:function(data,type,full){
                    return data
                }
              },
              { data: "activity",
                mRender: function(data, type, full) {
                  return vm.returns.sheet_activity_list[data]
                }
              },
              { data: "qty" },
              { data: "total" },
              { data: "comment" },
              { data: "editable",
                mRender: function(data, type, full) {
                  if (full.activity) {
                     var column = `<a class="edit-row" data-date=\"__DATE__\" ` +
                                  `data-activity=\"__ACTIVITY__\"  data-qty=\"__QTY__\" ` +
                                  `data-total=\"__TOTAL__\" data-comment=\"__COMMENT__\" ` +
                                  `data-licence=\"__LICENCE__\">Edit</a><br/>`

                     column = column.replace(/__DATE__/g, full.date)
                     column = column.replace(/__ACTIVITY__/g, full.activity)
                     column = column.replace(/__QTY__/g, full.qty)
                     column = column.replace(/__TOTAL__/g, full.total)
                     column = column.replace(/__COMMENT__/g, full.comment)
                     column = column.replace(/__LICENCE__/g, full.licence)
                     return column
                  } else {
                     return "";
                  }
                }
              }
            ],
            processing: true,
            rowId: function(_data) {
              return _data.date
            },
            initComplete: function () {
              console.log('entered init Function')
              // Populate activity list from the data in the table
              var activityColumn = vm.$refs.return_datatable.vmDataTable.columns(1);
              activityColumn.data().unique().sort().each( function ( d, j ) {
                let activityTitles = [];
                $.each(d,(index,a) => {
                  a != null && activityTitles.indexOf(a)<0 ? activityTitles.push(vm.returns.sheet_activity_list[a]): '';
                })
                vm.sheet_activity_type = activityTitles;
              });
            }
        }
    }
    returns: null
  },
  methods: {
    save: function(e) {
      console.log('save func')
      // FIXME: Not working yet!! (doesn't break though..)
      let vm = this;
      vm.form=document.forms.enter_return_sheet
      let data = new FormData(vm.form);
      console.log(vm.$refs.return_datatable)
      console.log(JSON.stringify(vm.$refs.return_datatable.vmDataTable.row(0).data()))
      console.log(vm.returns)
      data.append('specieID', vm.returns)
      vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/save'),data,{
                       emulateJSON:true,
                    }).then((response)=>{
                       swal('Sent',
                            'successful returns',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
                    });
    },
    submit: function(e) {
      console.log('submit func')
      let vm = this;
      vm.form=document.forms.enter_return_sheet
    },
    addEventListeners: function() {
      let vm = this;
    },
    initialiseSearch:function() {
    },
    filterSheetActivityType: function(){
       console.log('filterSheetActivityType')
    },
    refreshFromResponse:function(response){
       console.log('RefreshFromResponse function')
       let vm = this;
       console.log(response.body)
       //vm.return = helpers.copyObject(response.body);
    },
    addSheetRow: function () {
       let vm = this;
       vm.$refs.sheet_entry.speciesType = '<Species type 1>';
       vm.$refs.sheet_entry.entryActivity = '';
       vm.$refs.sheet_entry.entryNumber = '';
       vm.$refs.sheet_entry.entryTotal = '';
       vm.$refs.sheet_entry.entryComment = '';
       vm.$refs.sheet_entry.entryLicence = '';
       vm.$refs.sheet_entry.isModalOpen=true;
    }
  },
  components:{
    SheetEntry,
    datatable,
  },
  computed: {
    sheetURL: function(){
      return helpers.add_endpoint_json(api_endpoints.returns,'sheet_details');
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
  },
  beforeRouteEnter: function(to, from, next) {
    console.log('BEFORE-ROUTE func()')
    Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
        next(vm => {
           vm.returns = res.body;
           console.log(vm);
           console.log(vm.returns)
        });
    }, err => {
      console.log(err);
    });
  },
  mounted: function(){
     console.log('MOUNTED func')
     let vm = this;
     vm.form = document.forms.enter_return_sheet;
     vm.$refs.return_datatable.vmDataTable.on('click','.edit-row', function(e) {
        e.preventDefault();
        vm.$refs.sheet_entry.entryActivity = $(this).attr('data-activity');
        vm.$refs.sheet_entry.entryQty = $(this).attr('data-qty');
        vm.$refs.sheet_entry.entryTotal = $(this).attr('data-total');
        vm.$refs.sheet_entry.entryComment = $(this).attr('data-comment');
        vm.$refs.sheet_entry.entryLicence = $(this).attr('data-licence');
        vm.$refs.sheet_entry.speciesType = '<Species type 1>';

        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#2019/01/31')
        //vm.$refs.sheet_entry.table = vm.$refs.return_datatable.vmDataTable
        //vm.$refs.return_datatable.vmDataTable.row('#2019/01/31').data().qty = 100
        //let newData = ["2019/01/23", "SA01", "5000", '5', 'Initial Stock Taking', '']
        //console.log(vm.$refs.return_datatable.vmDataTable.row(1).data())
        //vm.$refs.return_datatable.vmDataTable.ajax.reload()
        // Fix the table rendering columns
        vm.$refs.sheet_entry.isModalOpen=true;
     });
  },
};
</script>
