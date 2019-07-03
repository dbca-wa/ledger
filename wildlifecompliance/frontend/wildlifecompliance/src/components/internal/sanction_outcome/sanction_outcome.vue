
<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-4">Type</label>
                    <!-- <select class="form-control" v-model="sanction_outcome.type_id"> -->
                    <!-- <select class="form-control" v-bind:value="sanction_outcome.type_id" v-on:change="typeChanged($event)"> -->
                    <select class="form-control" v-on:change="typeChanged($event)">
                        <option v-for="option in sanction_outcome_types" v-bind:value="option.id" v-bind:key="option.id">
                            {{ option.display }} 
                        </option>
                    </select>
                </div></div>

                <div v-if="displayTabs">
                    <ul class="nav nav-pills">
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+nTab">{{ firstTabTitle }}</a></li>
                        <li class="nav-item" v-if="displayRemediationActions"><a data-toggle="tab" :href="'#'+aTab">Remediation Actions</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="nTab" class="tab-pane fade in active">
                            <div class="row">
                            </div>
                        </div>

                        <div :id="aTab" class="tab-pane fade in">
                            <div class="row">
                            </div>
                        </div>

                        <div :id="dTab" class="tab-pane fade in">
                            <div class="row">
                            </div>
                        </div>
                    </div>

                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Send to Manager</button>
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

      sanction_outcome: {
          type_id: '',
      },
      sanction_outcome_types: [],

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
                '<a href="#" class="remove_button" data-alleged-offence-id="' +
                row.id +
                '">Remove</a>'
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
  computed: {
    ...mapGetters("callemailStore", {
      call_email: "call_email"
    }),
    ...mapGetters("offenceStore", {
      offence: "offence"
    }),
    modalTitle: function() {
      return "Identify Sanction Outcome";
    },
    firstTabTitle: function() {
        for (let i = 0; i < this.sanction_outcome_types.length; i++) {
            if (this.sanction_outcome_types[i]['id'] == this.sanction_outcome.type_id){
                return this.sanction_outcome_types[i]['display'];
            }
        }
        return '';
    },
    displayTabs: function() {
        return this.sanction_outcome.type_id==''? false : true;
    },
    displayRemediationActions: function() {
        return this.sanction_outcome.type_id=='remediation_notice'? true : false;
    }
  },
  methods: {
    ...mapActions("callemailStore", {
      loadCallEmail: "loadCallEmail"
    }),
    ...mapActions("offenceStore", {
    }),
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
    typeChanged: function(e) {
        this.sanction_outcome.type_id = e.target.value;
    },
    sendData: async function() {
      let vm = this;
    },
  },
    created: async function() {
        console.log('created');
        // Load all the types for the sanction outcome
        let sanction_outcome_types = await cache_helper.getSetCacheList('SanctionOutcome_Types', '/api/sanction_outcome/types.json');
        this.sanction_outcome_types.push({'id': '', 'display': ''});
        for (let i = 0; i < sanction_outcome_types.length; i++) {
            this.sanction_outcome_types.push(sanction_outcome_types[i]);
        }
  },
  mounted: function() {
    let vm = this;
    vm.$nextTick(() => {
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
