<template>
<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">{{ sheetTitle }}
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
                        <label for="">Species Available:</label>
                        <select class="form-control" >
                            <option class="change-species" v-for="specie in returns.sheet_species_list" :value="returns.sheet_species" :species_id="specie" >{{species_list[specie]}}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group" v-if="!readonly" >
                        <button class="btn btn-primary pull-right" @click.prevent="addSheetRow()" name="sheet_entry">New Entry</button>
                    </div>
                </div>
            </div>
             <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="">Activity Type:</label>
                        <select class="form-control">
                            <option v-for="sa in sheet_activity_type" :value="sa">{{sa['label']}}</option>
                        </select>
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
    <SheetEntry ref="sheet_entry"></SheetEntry>
</div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import utils from '@/components/internal/utils'
import $ from 'jquery'
import Vue from 'vue'
import Returns from '../../returns_form.vue'
import { mapActions, mapGetters } from 'vuex'
import CommsLogs from '@common-components/comms_logs.vue'
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
        required: false
     }
  },
  data() {
    let vm = this;
    return {
        pdBody: 'pdBody' + vm._uid,
        datatable_id: 'return-datatable',
        form: null,
        readonly: false,
        isModalOpen: false,
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
                  _data.return_id = vm.returns.id
                  _data.species_id = vm.returns.sheet_species
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
                  if (full.activity && vm.is_external) {
                     var column = `<a class="edit-row" data-rowid=\"__ROWID__\">Edit</a><br/>`
                     column = column.replace(/__ROWID__/g, full.rowId)
                     return column
                  } else {
                     return "";
                  }
                }
              }
            ],
            drawCallback: function() {
              vm.sheetTitle = vm.species_list[vm.returns.sheet_species]
            },
            processing: true,
            ordering: false,
            rowId: function(_data) {
              return _data.rowId
            },
            initComplete: function () {
              // Cache the initial table load.
              vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.ajax.json()
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
  },
  components:{
    SheetEntry,
    datatable,
    Returns,
  },
  computed: {
     ...mapGetters([
        'isReturnsLoaded',
        'returns',
        'species_list',
        'species_cache',
        'is_external',
    ]),
    sheetURL: function(){
      return helpers.add_endpoint_json(api_endpoints.returns,'sheet_details');
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
        'setReturnsSpecies',
        'setSpeciesCache',
    ]),
    save: function(e) {
      this.form=document.forms.enter_return_sheet;
      var data = new FormData(this.form);
      for (const speciesID in this.species_cache) {
        let speciesJSON = []
        for (let i=0;i<this.species_cache[speciesID].length;i++){
          speciesJSON[i] = JSON.stringify(this.species_cache[speciesID][i])
        }
        data.append(speciesID, speciesJSON)
      };
      this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/save'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                       let species_id = this.returns.sheet_species;
                       this.setReturns(response.body);
                       this.returns.sheet_species = species_id;
                       swal('Save',
                            'Return Sheet for Species Saved',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
                    });
    },
    addSheetRow: function () {
      this.$refs.sheet_entry.isAddEntry = true;
      this.$refs.sheet_entry.row_of_data = this.$refs.return_datatable.vmDataTable;
      this.$refs.sheet_entry.activityList = this.returns.sheet_activity_list;
      this.$refs.sheet_entry.speciesType = this.returns.sheet_species
      this.$refs.sheet_entry.entryActivity = Object.keys(this.returns.sheet_activity_list)[0];
      this.$refs.sheet_entry.entryNumber = '';
      this.$refs.sheet_entry.entryTotal = '';
      this.$refs.sheet_entry.entryComment = '';
      this.$refs.sheet_entry.entryLicence = '';
      this.$refs.sheet_entry.entryDateTime = '';
      this.$refs.sheet_entry.isSubmitable = true;
      this.$refs.sheet_entry.isModalOpen = true;
    }
  },
  mounted: function(){
     var vm = this;
     vm.form = document.forms.enter_return_sheet;
     vm.readonly = !vm.is_external;
     vm.select_species_list = this.species_list
     vm.$refs.return_datatable.vmDataTable.on('click','.edit-row', function(e) {
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.entrySpecies = vm.sheetTitle    ;
        vm.$refs.sheet_entry.entryActivity = vm.$refs.sheet_entry.row_of_data.data().activity;
        vm.$refs.sheet_entry.entryQty = vm.$refs.sheet_entry.row_of_data.data().qty;
        vm.$refs.sheet_entry.entryTotal = vm.$refs.sheet_entry.row_of_data.data().total;
        vm.$refs.sheet_entry.entryComment = vm.$refs.sheet_entry.row_of_data.data().comment;
        vm.$refs.sheet_entry.entryLicence = vm.$refs.sheet_entry.row_of_data.data().licence;
        vm.$refs.sheet_entry.isSubmitable = true;
        vm.$refs.sheet_entry.isModalOpen = true;
     });

     vm.$refs.return_datatable.vmDataTable.on('click','.accept-decline-transfer', function(e) {
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.isModalOpen = false;
     });

     vm.$refs.return_datatable.vmDataTable.on('click','.pay-transfer', function(e) {
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.isModalOpen = false;
     });

     // Instantiate Form Actions
     $('form').on('click', '.change-species', function(e) {
        e.preventDefault();
        let selected_id = $(this).attr('species_id');
        if (vm.species_cache[vm.returns.sheet_species] == null) {
            // cache currently displayed species json
            vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.ajax.json()
        }
        vm.returns.sheet_species = selected_id;
        if (vm.species_cache[selected_id] != null) {
            // species json previously loaded from ajax
            vm.$refs.return_datatable.vmDataTable.clear().draw()
            vm.$refs.return_datatable.vmDataTable.rows.add(vm.species_cache[selected_id])
            vm.$refs.return_datatable.vmDataTable.draw()
        } else {
            // load species json from ajax
            vm.$refs.return_datatable.vmDataTable.clear().draw()
            vm.$refs.return_datatable.vmDataTable.ajax.url = helpers.add_endpoint_json(api_endpoints.returns,'sheet_details');
            vm.$refs.return_datatable.vmDataTable.ajax.reload()
        };
     });
  },
};
</script>
