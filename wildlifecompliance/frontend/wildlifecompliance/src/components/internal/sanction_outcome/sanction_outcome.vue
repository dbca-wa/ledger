<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-1">Type</label>
                    <div class="col-sm-4">
                        <select class="form-control" v-on:change="typeSelected($event)">
                            <option v-for="option in options_for_types" v-bind:value="option.id" v-bind:key="option.id">
                                {{ option.display }} 
                            </option>
                        </select>
                    </div>
                </div></div>

                <div v-if="displayTabs">
                    <ul class="nav nav-pills">
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+nTab">{{ firstTabTitle }}</a></li>
                        <li class="nav-item" v-if="displayRemediationActions"><a data-toggle="tab" :href="'#'+aTab">Remediation Actions</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="nTab" class="tab-pane fade in active"><div class="row">

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-2">
                                    <label class="control-label pull-left">Region</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome">
                                        <select></select>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-2">
                                    <label class="control-label pull-left">District</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome">
                                        <select></select>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-2">
                                    <label class="control-label pull-left" for="identifier">Identifier</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome">
                                        <input type="text" class="form-control" name="identifier" placeholder="" v-model="sanction_outcome.identifier" v-bind:key="sanction_outcome.id">
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-2">
                                    <label class="control-label pull-left">Offence</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome">
                                        <select class="form-control" v-on:change="offenceSelected($event)">
                                            <option value=""></option>
                                            <option v-for="option in options_for_offences" v-bind:value="option.id" v-bind:key="option.id">
                                                {{ option.id + ': ' + option.status + ', ' + option.identifier }} 
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-2">
                                    <label class="control-label pull-left">Offender</label>
                                </div>
                                <div class="col-sm-7">
                                    <div v-if="sanction_outcome && sanction_outcome.current_offence && sanction_outcome.current_offence.offenders">
                                        <select class="form-control" v-on:change="offenderSelected($event)">
                                            <option value=""></option>
                                            <!-- <option v-for="offender in options_for_offenders" v-bind:value="offender.id" v-bind:key="offender.id"> -->
                                            <option v-for="offender in sanction_outcome.current_offence.offenders" v-bind:value="offender.id" v-bind:key="offender.id">
                                                <span v-if="offender.person">
                                                    {{ offender.person.first_name + ' ' + offender.person.last_name + ', DOB:' + offender.person.dob }} 
                                                </span>
                                                <span v-else-if="offender.organisation">
                                                    {{ offender.organisation.name + ', ABN: ' + offender.organisation.abn }} 
                                                </span>
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group">
                                <div class="row col-sm-12">
                                    <label class="control-label pull-left">Alleged committed offences</label>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <datatable ref="tbl_alleged_offence" id="tbl_alleged_offence" :dtOptions="dtOptionsAllegedOffence" :dtHeaders="dtHeadersAllegedOffence" />
                                    </div>
                                </div>
                            </div>

                        </div></div>

                        <div :id="aTab" class="tab-pane fade in"><div class="row">


                        </div></div>

                        <div :id="dTab" class="tab-pane fade in"><div class="row">


                        </div></div>
                    </div>

                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" :disabled="!displaySendToManagerButton" class="btn btn-default" @click="ok">Send to Manager</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from "vue";
import modal from "@vue-utils/bootstrap-modal.vue";
import datatable from "@vue-utils/datatable.vue";
import { mapGetters, mapActions } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "../utils";
import $ from "jquery";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";

export default {
  name: "SanctionOutcome",
  data: function() {
    let vm = this;

    return {
      nTab: "nTab" + vm._uid,
      aTab: "aTab" + vm._uid,
      dTab: "dTab" + vm._uid,
      isModalOpen: false,
      processingDetails: false,

      // This is the object to be sent to the server when saving
      sanction_outcome: {
        type_id: "",
        identifier: "",
        current_offence: null,        // Store an offence to be saved as an attribute of the sanction outcome
                                      // The offenders and the alleged_offences under this offence object are used
                                      // to construct a dropdown list for the offenders and the alleged offences datatable
        current_offender: null,       // Store an offender to be saved as an attribute of the sanction outcome
      },

      // List for dropdown
      options_for_types: [],
      options_for_offences: [],

      dtHeadersAllegedOffence: [
        "id",
        "Act",
        "Section/Regulation",
        "Alleged Offence",
        "Action"
      ],
      dtOptionsAllegedOffence: {
        columns: [
          {
            data: "id",
            visible: false
          },
          {
            data: "Act"
          },
          {
            data: "Section/Regulation"
          },
          {
            data: "Alleged Offence"
          },
          {
            data: "Action",
            mRender: function(data, type, row) {
              return (
                '<a href="#" class="remove_button" data-alleged-offence-id="' + row.id + '">Remove</a>'
              );
            }
          }
        ]
      }
    };
  },
  components: {
    modal,
    datatable,
  },
  watch: {
      current_offence: {
          handler: function (){
            this.currentOffenceChanged();
          },
      },
      current_offender: {
          handler: function (){
            this.currentOffenderChanged();
          },
      },
  },
  computed: {
    ...mapGetters("callemailStore", {
      call_email: "call_email"
    }),
    ...mapGetters("offenceStore", {
      offence: "offence"
    }),
    current_offence: function() {
      return this.sanction_outcome.current_offence;
    },
    current_offender: function() {
      return this.sanction_outcome.current_offender;
    },
    modalTitle: function() {
      return "Identify Sanction Outcome";
    },
    firstTabTitle: function() {
      for (let i = 0; i < this.options_for_types.length; i++) {
        if (
          this.options_for_types[i]["id"] == this.sanction_outcome.type_id
        ) {
          return this.options_for_types[i]["display"];
        }
      }
      return "";
    },
    displayTabs: function() {
      return this.sanction_outcome.type_id == "" ? false : true;
    },
    displaySendToManagerButton: function() {
      if (!this.processingDetails && this.sanction_outcome.type_id){
        return true
      }
      return false;
    },
    displayRemediationActions: function() {
      return this.sanction_outcome.type_id == "remediation_notice"
        ? true
        : false;
    }
  },
  methods: {
    ...mapActions("callemailStore", {
      loadCallEmail: "loadCallEmail"
    }),
    ...mapActions("offenceStore", {}),
    ok: async function() {
        await this.sendData();
        this.close();
    },
    cancel: function() {
      this.isModalOpen = false;
      this.close();
    },
    close: function() {
      this.isModalOpen = false;
    },
    addEventListener: function() {
      // Clear existing events in case there are.  
      // Otherwise multiple click events are raised by a single click.
      $('#tbl_alleged_offence').off('click');
      $('#tbl_alleged_offence').on('click', 'tbody tr td', function(e){
          let elem_a = e.target.getElementsByClassName('remove_button');
          if (elem_a.length > 0){
            let alleged_offence_id = elem_a[0].getAttribute('data-alleged-offence-id');
            console.log('alleged_offence_id clicked: ' + alleged_offence_id);
          }
      })
    },
    offenceSelected: function(e) {
      let vm = this;
      let offence_id = parseInt(e.target.value);
      for (let i=0; i<vm.options_for_offences.length; i++) {
        if (vm.options_for_offences[i].id == offence_id) {
          // Update current offence
          vm.sanction_outcome.current_offence = vm.options_for_offences[i];
          return;
        }
      }
      // User selected the empty line
      vm.sanction_outcome.current_offence = null;
    },
    offenderSelected: function(e) {
      let vm = this;
      let offender_id = parseInt(e.target.value);
      for (let i=0; i<vm.sanction_outcome.current_offence.offenders.length; i++) {
        if (vm.sanction_outcome.current_offence.offenders[i].id == offender_id) {
          // Update current offender
          vm.sanction_outcome.current_offender = vm.sanction_outcome.current_offence.offenders[i]
          return;
        }
      }
      // User selected the empty line
      vm.sanction_outcome.current_offender = null;
    },
    typeSelected: function(e) {
      this.sanction_outcome.type_id = e.target.value;
    },
    sendData: async function() {
      let vm = this;
    },
    currentOffenderChanged: function() {
      console.log('currentOffenderChanged');
    },
    currentOffenceChanged: function() {
      console.log('currentOffenceChanged');
      let vm = this;

      vm.sanction_outcome.current_offender = null;

      // The dropdown list of the offenders are directly linked to the vm.sanction_outcome.offence.offenders.
      // That's why the dropdown list is updated automatically whenever vm.sanction_outcome.offence is chanaged.

      // Construct the datatable of the alleged offences
      vm.$refs.tbl_alleged_offence.vmDataTable.rows().remove().draw();   // Clear the table anyway
      if (vm.sanction_outcome.current_offence) {
        for (let j=0; j < vm.sanction_outcome.current_offence.alleged_offences.length; j++){
          vm.$refs.tbl_alleged_offence.vmDataTable.row.add({
              "id": vm.sanction_outcome.current_offence.alleged_offences[j].id,
              "Act": vm.sanction_outcome.current_offence.alleged_offences[j].act,
              "Section/Regulation": vm.sanction_outcome.current_offence.alleged_offences[j].name,
              "Alleged Offence": vm.sanction_outcome.current_offence.alleged_offences[j].offence_text
          }).draw();
        }
      }
      vm.addEventListener();
    },
    updateOptionsForOffences: function(call_email_id) {
      let vm = this;
      let returned = Vue.http.get(
          "/api/offence/filter_by_call_email.json",
          { params: { 'call_email_id': call_email_id }}
      );
      returned.then((res)=>{
          console.log(res.body);
          vm.options_for_offences = res.body;
      })
    }
  },
  created: async function() {
    let vm = this;

    // Load all the types for the sanction outcome
    let options_for_types = await cache_helper.getSetCacheList(
      "SanctionOutcome_Types",
      "/api/sanction_outcome/types.json"
    );
    vm.options_for_types.push({ id: "", display: "" });
    for (let i = 0; i < options_for_types.length; i++) {
      vm.options_for_types.push(options_for_types[i]);
    }
    vm.updateOptionsForOffences(vm.call_email.id);
  },
  mounted: function() {
    let vm = this;
    vm.$nextTick(() => {
      console.log('mounted');
    });
  }
};
</script>

<style lang="css" scoped>
.btn-file {
  position: relative;
  overflow: hidden;
}
.btn-file input[type="file"] {
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
.top-buffer {
  margin-top: 5px;
}
.top-buffer-2x {
  margin-top: 10px;
}
.radio-button-label {
  padding-left: 0;
}
.tab-content {
  background: white;
  padding: 10px;
  border: solid 1px lightgray;
}
#DataTable {
  padding: 10px 5px;
  border: 1px solid lightgray;
}
</style>
