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
    var vm = this; // keep and use created ViewModel context with table.
    return {
        pdBody: 'pdBody' + vm._uid,
        datatable_id: 'return-datatable',
        form: null,
        readonly: false,
        isModalOpen: false,
        sheetTitle: null,
        sheet_total: 0,
        sheet_activity_type: [],
        sheet_headers:["order","Date","Activity","Qty","Total","Comments","Action"],
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
            columnDefs: [
              { visible: false, targets: 0 } // hide order column.
            ],
            columns: [
              { data: "date" },
              { data: "date",
                mRender: function(data, type, full) {
                   let _date = new Date(parseInt(full.date));
                   return _date.toLocaleString("en-GB")
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
                   if (full.activity && vm.is_external
                                && !vm.isTrue(vm.returns.sheet_activity_list[full.activity]['auto'])
                                && (full.transfer === 'notify' || full.transfer === '')) {
                      var column = `<a class="edit-row" data-rowid=\"__ROWID__\">Edit</a><br/>`;
                      column = column.replace(/__ROWID__/g, full.rowId);
                      return column;
                   }
                   if (full.activity && (full.transfer === 'accept' || full.transfer === 'decline')) {
                      return full.transfer;
                   }
                   if (full.activity && vm.is_external
                                && (vm.isTrue(vm.returns.sheet_activity_list[full.activity]['auto'])
                                && full.transfer === 'notify')) {
                      var accept = `<a class="accept-row" data-rowid=\"__ROWID__\">Accept</a> or `;
                      accept = accept.replace(/__ROWID__/g, full.rowId);
                      var decline = `<a class="decline-row" data-rowid=\"__ROWID__\">Decline</a><br/>`;
                      decline = decline.replace(/__ROWID__/g, full.rowId);
                      return accept + decline;
                   } else {
                      return "";
                   }
                }
              }
            ],
            order: [0, 'desc'],
            drawCallback: function() {
              vm.sheetTitle = vm.species_list[vm.returns.sheet_species]
            },
            rowCallback: function(row, data) {
              vm.sheet_total = parseInt(data.total) > vm.sheet_total ? parseInt(data.total) : vm.sheet_total;
            },
            processing: true,
            ordering: true,
            rowId: function(_data) {
              return _data.rowId
            },
            initComplete: function () {
              if (vm.$refs.return_datatable.vmDataTable.ajax.json().length > 0) {
                // cache initial load.
                vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.ajax.json()
              }
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
        'species_transfer',
    ]),
  },
  methods: {
    ...mapActions([
        'setReturns',
        'setReturnsSpecies',
        'setSpeciesCache',
    ]),
    isTrue: function(_value) {
      return (_value === 'true');
    },
    intVal: function(_value) {
      return typeof _value === 'string' ?
          _value.replace(/[\$,]/g, '')*1 :
          typeof _value === 'number' ?
          _value : 0;
    },
    addSheetRow: function () {
      const self = this;
      var rows = self.$refs.return_datatable.vmDataTable
      self.$refs.sheet_entry.isAddEntry = true;
      self.$refs.sheet_entry.row_of_data = rows;
      self.$refs.sheet_entry.activityList = self.returns.sheet_activity_list;
      self.$refs.sheet_entry.speciesType = self.returns.sheet_species
      self.$refs.sheet_entry.entrySpecies = self.sheetTitle;
      self.$refs.sheet_entry.entryActivity = Object.keys(self.returns.sheet_activity_list)[0];
      self.$refs.sheet_entry.entryTotal = self.sheet_total;
      self.$refs.sheet_entry.currentStock = self.sheet_total;
      self.$refs.sheet_entry.entryComment = '';
      self.$refs.sheet_entry.entryLicence = '';
      self.$refs.sheet_entry.entryDateTime = '';
      self.$refs.sheet_entry.isSubmitable = true;
      self.$refs.sheet_entry.isModalOpen = true;
    }
  },
  created: function(){
     this.form = document.forms.enter_return_sheet;
     this.readonly = !this.is_external;
     this.select_species_list = this.species_list;
  },
  mounted: function(){
     var vm = this; // preserve created ViewModel context when mounted for function calls.
     vm.$refs.return_datatable.vmDataTable.on('click','.edit-row', function(e) {
        e.preventDefault();
        vm.$refs.sheet_entry.isChangeEntry = true;
        vm.$refs.sheet_entry.activityList = vm.returns.sheet_activity_list;
        vm.$refs.sheet_entry.speciesType = vm.returns.sheet_species;
        vm.$refs.sheet_entry.row_of_data = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        vm.$refs.sheet_entry.entrySpecies = vm.sheetTitle;
        vm.$refs.sheet_entry.entryDateTime = vm.$refs.sheet_entry.row_of_data.data().date;
        vm.$refs.sheet_entry.entryActivity = vm.$refs.sheet_entry.row_of_data.data().activity;
        vm.$refs.sheet_entry.entryQty = vm.$refs.sheet_entry.row_of_data.data().qty;
        vm.$refs.sheet_entry.initialQty = vm.$refs.sheet_entry.row_of_data.data().qty;
        vm.$refs.sheet_entry.entryTotal = vm.$refs.sheet_entry.row_of_data.data().total;
        vm.$refs.sheet_entry.currentStock = vm.$refs.sheet_entry.row_of_data.data().total;
        vm.$refs.sheet_entry.entryComment = vm.$refs.sheet_entry.row_of_data.data().comment;
        vm.$refs.sheet_entry.entryLicence = vm.$refs.sheet_entry.row_of_data.data().licence;
        vm.$refs.sheet_entry.entryTransfer = vm.$refs.sheet_entry.row_of_data.data().transfer;

        vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.data();

        vm.$refs.sheet_entry.isSubmitable = true;
        vm.$refs.sheet_entry.isModalOpen = true;
        vm.$refs.sheet_entry.errors = false;
     });

     vm.$refs.return_datatable.vmDataTable.on('click','.accept-row', function(e) {
        e.preventDefault();
        var selected = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        var rows = vm.$refs.return_datatable.vmDataTable.data();
        for (let i=0; i<rows.length; i++) {
          if (vm.intVal(rows[i].date)>=vm.intVal(selected.data().date)){ //activity is after accepted
            rows[i].total = vm.intVal(rows[i].total) + vm.intVal(selected.data().qty)
          }
          if (vm.intVal(rows[i].date)==vm.intVal(selected.data().date)) {
            rows[i].transfer = 'accept'
            rows[i].species_id = vm.returns.sheet_species

            let transfer = {}  //{speciesID: {this.entryDateTime: row_data},}
            if (vm.returns.sheet_species in vm.species_transfer){
              transfer = vm.species_transfer[vm.returns.sheet_species]
            }
            transfer[rows[i].date] = rows[i];
            vm.species_transfer[vm.returns.sheet_species] = transfer
          }
        }
        vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.data();
        vm.$refs.return_datatable.vmDataTable.clear().draw();
        vm.$refs.return_datatable.vmDataTable.rows.add(vm.species_cache[vm.returns.sheet_species]);
        vm.$refs.return_datatable.vmDataTable.draw();

     });

     vm.$refs.return_datatable.vmDataTable.on('click','.decline-row', function(e) {
        e.preventDefault();
        var selected = vm.$refs.return_datatable.vmDataTable.row('#'+$(this).attr('data-rowid'));
        var rows = vm.$refs.return_datatable.vmDataTable.data();
        for (let i=0; i<rows.length; i++) {
          if (vm.intVal(rows[i].date)==vm.intVal(selected.data().date)) {
            rows[i].transfer = 'decline'
            rows[i].species_id = vm.returns.sheet_species

            let transfer = {}  //{speciesID: {this.entryDateTime: row_data},}
            if (vm.returns.sheet_species in vm.species_transfer){
              transfer = vm.species_transfer[vm.returns.sheet_species]
            }
            transfer[rows[i].date] = rows[i];
            vm.species_transfer[vm.returns.sheet_species] = transfer
          }
        }
        vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.data();
        vm.$refs.return_datatable.vmDataTable.clear().draw();
        vm.$refs.return_datatable.vmDataTable.rows.add(vm.species_cache[vm.returns.sheet_species]);
        vm.$refs.return_datatable.vmDataTable.draw();
     });

     vm.$refs.return_datatable.vmDataTable.on('click','.pay-transfer', function(e) {  // TODO: payments
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
        if (vm.species_cache[vm.returns.sheet_species]==null
                        && vm.$refs.return_datatable.vmDataTable.ajax.json().length>0) {
            // cache currently displayed species json
            vm.species_cache[vm.returns.sheet_species] = vm.$refs.return_datatable.vmDataTable.ajax.json()
        }
        vm.returns.sheet_species = selected_id;
        if (vm.species_cache[selected_id] != null) {
            // species json previously loaded from ajax
            vm.$refs.return_datatable.vmDataTable.clear().draw();
            vm.$refs.return_datatable.vmDataTable.rows.add(vm.species_cache[selected_id]);
            vm.$refs.return_datatable.vmDataTable.draw();
        } else {
            // load species json from ajax
            vm.$refs.return_datatable.vmDataTable.clear().draw();
            vm.$refs.return_datatable.vmDataTable
                    .ajax.url = helpers.add_endpoint_json(api_endpoints.returns,'sheet_details');
            vm.$refs.return_datatable.vmDataTable.ajax.reload();
        };
     });
  },
};
</script>
