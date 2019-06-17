<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large>
            <div class="container-fluid">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" :href="'#'+oTab">Offence</a></li>
                    <li><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    <li><a data-toggle="tab" :href="'#'+pTab">Offender(s)</a></li>
                    <li><a data-toggle="tab" :href="'#'+lTab">Location</a></li>
                </ul>
                <div class="tab-content">
                    <div :id="oTab" class="tab-pane fade in active">
                        <div class="row">

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="offence-identifier">Identifier</label>
                                </div>
                                <div class="col-sm-6">
                                    <div v-if="offence">
                                        <input type="text" class="form-control" name="identifier" placeholder="" v-model="offence.identifier" v-bind:key="offence.id">
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Use occurrence from/to</label>
                                <input class="col-sm-1" id="occurrence_from_to_true" type="radio" v-model="offence.occurrence_from_to" v-bind:value="true">
                                <label class="col-sm-1 radio-button-label" for="occurrence_from_to_true">Yes</label>
                                <input class="col-sm-1" id="occurrence_from_to_false" type="radio" v-model="offence.occurrence_from_to" v-bind:value="false">
                                <label class="col-sm-1 radio-button-label" for="occurrence_from_to_false">No</label>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="occurrenceDateFromPicker">
                                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_from" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <div v-if="offence.occurrence_from_to">
                                    <div class="col-sm-3">
                                        <div class="input-group date" ref="occurrenceDateToPicker">
                                            <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_to" />
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="occurrenceTimeFromPicker">
                                        <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_from" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <div v-if="offence.occurrence_from_to">
                                    <div class="col-sm-3">
                                        <div class="input-group date" ref="occurrenceTimeToPicker">
                                            <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_to" />
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Alleged Offence</label>
                                <div class="col-sm-6">
                                    <input class="form-control" id="alleged-offence" />
                                </div>
                                <div class="col-sm-3">
                                    <input type="button" class="btn btn-primary" value="Add" @click.prevent="addAllegedOffence()" />
                                </div>
                            </div></div>
                        </div>
                    </div>

                    <div :id="dTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left" for="offence-details">Details</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <div v-if="offence">
                                                <textarea class="form-control" placeholder="add details" id="offence-details" v-model="offence.details" v-bind:key="offence.id"/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div :id="pTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="form-group">

                                </div>
                            </div>
                        </div>
                    </div>

                    <div :id="lTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12 form-group">
                                <div v-if="offence.location">
                                    <MapLocationOffence v-bind:key="offence.location.id"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
                                <!-- <div v-if="offence.location">
                                    <MapLocationOffence v-bind:key="offence.location.id"/>
                                </div> -->
    </div>
</template>

<script>
import Awesomplete from 'awesomplete';
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import MapLocationOffence from "./map_location_offence1"
import utils from '../utils'
import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';

export default {
  name: "Offence",
  data: function() {
    let vm = this;

    vm.max_items = 10;
    vm.ajax_for_alleged_offence = null;

    return {
      officers: [],
      isModalOpen: false,
      processingDetails: false,
      offender_type: 'indivisual',

      oTab: 'oTab'+vm._uid,
      dTab: 'dTab'+vm._uid,
      pTab: 'pTab'+vm._uid,
      lTab: 'lTab'+vm._uid,
    }
  },
  components: {
    modal,
    MapLocationOffence,
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
    ...mapGetters('offenceStore', {
      offence: 'offence',
    }),
    modalTitle: function() {
        return "Identify Offence";
    },
    occurrenceDateLabel: function() {
      if (this.offence.occurrence_from_to) {
        return "Occurrence date from";
      } else {
        return "Occurrence date";
      }
    },
    occurrenceTimeLabel: function() {
      if (this.offence.occurrence_from_to) {
        return "Occurrence time from";
      } else {
        return "Occurrence time";
      }
    },
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
      ...mapActions('callemailStore', {
        setAllocatedTo: "setAllocatedTo",
      }),
      addAllegedOffence: function() {

      },
      ok: async function () {
          await this.sendData();
          this.close();
      },
      cancel: function() {
          this.isModalOpen = false;
          this.close();
      },
      close: function () {
          let vm = this;
          this.isModalOpen = false;
      },
      sendData: async function(){
          // TODO
          console.log('Send data to save');
      },
      addEventListeners: function () {
          let vm = this;
          let el_fr_date = $(vm.$refs.occurrenceDateFromPicker);
          let el_fr_time = $(vm.$refs.occurrenceTimeFromPicker);
          let el_to_date = $(vm.$refs.occurrenceDateToPicker);
          let el_to_time = $(vm.$refs.occurrenceTimeToPicker);

          // "From" field
          el_fr_date.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
          el_fr_date.on('dp.change', function (e) {
              if (el_fr_date.data('DateTimePicker').date()) {
                  vm.offence.occurrence_date_from = e.date.format('DD/MM/YYYY');
              } else if (el_fr_date.data('date') === "") {
                  vm.offence.occurrence_date_from = "";
              }
          });
          el_fr_time.datetimepicker({ format: 'LT', showClear: true });
          el_fr_time.on('dp.change', function (e) {
              if (el_fr_time.data('DateTimePicker').date()) {
                  vm.offence.occurrence_time_from = e.date.format('LT');
              } else if (el_fr_time.data('date') === "") {
                  vm.offence.occurrence_time_from = "";
              }
          });

          // "To" field
          el_to_date.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
          el_to_date.on('dp.change', function (e) {
              if (el_to_date.data('DateTimePicker').date()) {
                  vm.offence.occurrence_date_to = e.date.format('DD/MM/YYYY');
              } else if (el_to_date.data('date') === "") {
                  vm.offence.occurrence_date_to = "";
              }
          });
          el_to_time.datetimepicker({ format: 'LT', showClear: true });
          el_to_time.on('dp.change', function (e) {
              if (el_to_time.data('DateTimePicker').date()) {
                  vm.offence.occurrence_time_to = e.date.format('LT');
              } else if (el_to_time.data('date') === "") {
                  vm.offence.occurrence_time_to = "";
              }
          });
      },
      search: function(searchTerm){
          var vm = this;
          vm.suggest_list = [];
          vm.suggest_list.length = 0;
          vm.awe.list = [];

          /* Cancel all the previous requests */
          if (vm.ajax_for_alleged_offence != null){
              vm.ajax_for_alleged_offence.abort();
              vm.ajax_for_alleged_offence = null;
          }

          vm.ajax_for_alleged_offence = $.ajax({
              type: 'GET',
              url: '/api/search_alleged_offences/?search=' + searchTerm,
              success: function(data){
                  if (data && data.results) {
                      let persons = data.results;
                      let limit = Math.min(vm.max_items, persons.length);
                      for (var i = 0; i < limit; i++){
                          vm.suggest_list.push(persons[i])
                      }
                  }
                  vm.awe.list = vm.suggest_list;
                  vm.awe.evaluate();
                  console.log(vm.suggest_list);
              },
              error: function (e){
                  console.log(e);
              }
          });
      },
      initAwesomplete: function(){
          var self = this;

          var element_search = document.getElementById('alleged-offence');
          self.awe = new Awesomplete(element_search, {
              maxItems: self.max_items,
              sort: false,
              filter: ()=>{ return true; }, // Display all the items in the list without filtering.
              data: function(item, input){
                  let act = item.act?item.act:'';
                  let name = item.name?item.name:'';
                  let offence_text = item.offence_text?item.offence_text:'';

                  let myLabel = ['<span class="full_name">' + act + ', ' + name + '</span>', offence_text].filter(Boolean).join('<br />');

                  return {
                      label: myLabel,   // Displayed in the list below the search box
                      value: [act, name, offence_text].filter(Boolean).join(', '), // Inserted into the search box once selected
                      id: item.id
                  };
              }
          });
          $(element_search).on('keyup', function(ev){
              var keyCode = ev.keyCode || ev.which;
              if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105) || (keyCode == 8) || (keyCode == 46)){
                  self.search(ev.target.value);
                  return false;
              }
          }).on('awesomplete-selectcomplete', function(ev){
              ev.preventDefault();
              ev.stopPropagation();
              return false;
          }).on('awesomplete-select', function(ev){
              /* Retrieve element id of the selected item from the list
               * By parsing it, we can get the order-number of the item in the list
               */
              console.log("origin");
              console.log(ev.originalEvent.origin);
              let origin = $(ev.originalEvent.origin)
              let originTagName = origin[0].tagName;
              if (originTagName == "SPAN"){
                  origin = origin.parent();
              }
              let elem_id = origin[0].id;
              let reg = /^.+(\d+)$/gi;
              let result = reg.exec(elem_id)
              if(result[1]){
                  let idx = result[1];
                  self.loadAllegedOffence(self.suggest_list[idx].id);
              }else{
                  console.log("result");
                  console.log(result);
              }
          });
      },
      loadAllegedOffence: function(id){
          console.log('AllegdOffence: ' + id + ' selected.');
      }
  },
  created: async function() {
      this.$nextTick(function() {
          this.initAwesomplete();
      });
  },
  mounted: function() {
        let vm = this;
        vm.$nextTick(() => {
            vm.addEventListeners();
        });
  }
};
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
#offence-details {

}
.radio-button-label {
    padding-left: 0;
}
.awesomplete {
    display: inherit !important;
}
</style>
