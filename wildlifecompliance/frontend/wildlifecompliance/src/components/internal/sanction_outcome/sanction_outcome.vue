
<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="col-sm-12 form-group"><div class="row">
                    <label class="col-sm-4">Type</label>
                    <select class="form-control" v-model="call_email.classification_id">
                        <option v-for="option in sanction_outcome_types" :value="option.id" v-bind:key="option.id">
                            {{ option.display }} 
                        </option>
                    </select>
                </div></div>

                <ul class="nav nav-pills">
                    <li class="nav-item active"><a data-toggle="tab" :href="'#'+nTab">Notice (TODO: reactive)</a></li>
                    <li class="nav-item"><a data-toggle="tab" :href="'#'+aTab">Remediation Actions</a></li>
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
    sendData: async function() {
      let vm = this;
    },
  },
    created: async function() {
        console.log('created');
        // Load all the types for the sanction outcome
        let sanction_outcome_types = await cache_helper.getSetCacheList('SanctionOutcome_Types', '/api/sanction_outcome/types.json');
        Object.assign(this.sanction_outcome_types, sanction_outcome_types);
        this.sanction_outcome_types.splice(0, 0, { id: null, name: "", });
        console.log(this.sanction_outcome_types);

        // TODO: load offence under this call_email

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
