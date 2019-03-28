<template>
  <form method="POST" name="enter_return_sheet" enctype="multipart/form-data">
  <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
  <div class="container" id="externalReturnSheet">
    <div class="row">
      <div class="col-md-3">
        <h3>Return: {{ returns.id }}</h3>
        <!-- List of applicable species available for Return -->
        <label>Species on Return:</label>
        <div v-for="species in returns.sheet_species_list">
          <a href='/external/return/sheet/5' ><h5>{{fullSpeciesList[species]}}</h5></a>
        </div>
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
                  <div class="panel-heading" v-show="!isNewSpecies">
                     <h3 class="panel-title">{{ sheetTitle }}
                      <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                         <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                      </a>
                    </h3>
                  </div>
                  <div class="panel-heading" v-show="isNewSpecies">
                     <h3 class="panel-title">
                       <select class="form-control, col-md-9" v-model="returns.sheet_species">
                         <option v-for="sp in returns.licence_species_list" :value="sp">{{fullSpeciesList[sp]}}</option>
                       </select>
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
                                    <option v-for="sa in sheet_activity_type" :value="sa">{{sa['label']}}</option>
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
                <button class="btn btn-primary" name="add_sheet" @click.prevent="addSpecies()">Add Species Type</button>
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
    return {
        pdBody: 'pdBody' + vm._uid,
        datatable_id: 'return-datatable',
        returns: {
            id: 0,
            table: [{
                data: null
            }],
        },
        fullSpeciesList: {'': ''},
        //fullSpeciesList: {'S000001': 'Western Grey Kangaroo', 'S000002': 'Western Red Kangaroo',
        //                  'S000003': 'Blue Banded Bee', 'S000004': 'Orange-Browed Resin Bee'},
        returnTab: 'returnTab'+vm._uid,
        form: null,
        isModalOpen: false,
        returnBtn: 'Submit',
        isNewSpecies: false,
        newSpecies: null,
        sheetTitle: null,
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
                    let _date = new Date(parseInt(data));
                    return _date.toLocaleString()
                }
              },
              { data: "activity",
                mRender: function(data, type, full) {
                   return vm.returns.sheet_activity_list[data]['label']
                }
              },
              { data: "qty" },
              { data: "total" },
              { data: "comment" },
              { data: "editable",
                mRender: function(data, type, full) {
                  if (full.activity) {
                     var column = `<a class="edit-row" data-rowid=\"__ROWID__\">Edit</a><br/>`
                     column = column.replace(/__ROWID__/g, full.rowId)
                     return column
                  } else {
                     return "";
                  }
                }
              }
            ],
            processing: true,
            ordering: false,
            rowId: function(_data) {
              return _data.rowId
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
      let vm = this;
      vm.form=document.forms.enter_return_sheet;
      let data = new FormData(vm.form);
      var speciesData = [];
      vm.$refs.return_datatable.vmDataTable.rows().every(function(rowIdx,tableloop,rowloop) {
        let _data = this.data();
        speciesData[rowIdx] = JSON.stringify(_data)
      });
      data.append('species_id', vm.returns.sheet_species)
      data.append('species_data', speciesData);
      vm.$http.post(helpers.add_endpoint_json(api_endpoints.returns,vm.returns.id+'/save'),data,{
                       emulateJSON:true,
                    }).then((response)=>{
                       vm.returns = response.body;
                       vm.sheetTitle = vm.fullSpeciesList[vm.returns.sheet_species];
                       vm.isNewSpecies = false;
                       swal('Save',
                            'Return Sheet for Species Saved',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
                    });
    },
    addSpecies: function(e) {
      let vm = this;
      vm.form=document.forms.enter_return_sheet;
      let data = new FormData(vm.form);
      var speciesData = [];
      vm.$refs.return_datatable.vmDataTable.clear().draw()
      vm.speciesTitle = vm.newSpecies
      data.append('species_id', vm.newSpecies);
      data.append('species_data', speciesData);
      vm.isNewSpecies = true;
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
       //vm.return = helpers.copyObject(response.body);
    },
    addSheetRow: function () {
      let vm = this;
      console.log(Object.keys(vm.returns.sheet_activity_list)[0])
      vm.$refs.sheet_entry.isAddEntry = true;
      vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable;
      vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
      vm.$refs.sheet_entry.speciesType = vm.newSpecies;
      vm.$refs.sheet_entry.entryActivity = Object.keys(vm.returns.sheet_activity_list)[0];
      vm.$refs.sheet_entry.entryNumber = '';
      vm.$refs.sheet_entry.entryTotal = '';
      vm.$refs.sheet_entry.entryComment = '';
      vm.$refs.sheet_entry.entryLicence = '';
      vm.$refs.sheet_entry.entryDateTime = '';
      vm.$refs.sheet_entry.isSubmitable = true;
      vm.$refs.sheet_entry.isModalOpen = true;
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
    Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
        next(vm => {
           vm.returns = res.body;
           vm.sheetTitle = 'Please Add Species Type';
           vm.newSpecies = vm.returns.sheet_species
           if (vm.returns.sheet_species != '0000000') {
              vm.sheetTitle = vm.fullSpeciesList[vm.returns.sheet_species]
           };
        });
    }, err => {
      console.log(err);
    });
  },
  mounted: function(){
     let vm = this;
     vm.form = document.forms.enter_return_sheet;

     // Row Actions
     vm.$refs.return_datatable.vmDataTable.on('click','.edit-row', function(e) {
        console.log('entered edit-row')
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.entryActivity = vm.$refs.sheet_entry.row_of_data.data().activity;
        vm.$refs.sheet_entry.entryQty = vm.$refs.sheet_entry.row_of_data.data().qty;
        vm.$refs.sheet_entry.entryTotal = vm.$refs.sheet_entry.row_of_data.data().total;
        vm.$refs.sheet_entry.entryComment = vm.$refs.sheet_entry.row_of_data.data().comment;
        vm.$refs.sheet_entry.entryLicence = vm.$refs.sheet_entry.row_of_data.data().licence;
        vm.$refs.sheet_entry.isSubmitable = true;
        vm.$refs.sheet_entry.isModalOpen = true;
     });
     vm.$refs.return_datatable.vmDataTable.on('click','.accept-decline-transfer', function(e) {
        console.log('entered accept-decline-transfer')
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.isModalOpen = false;
     });
  },
};
</script>
