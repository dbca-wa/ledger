<template>
    <div>
        <div class="col-sm-12 form-group"><div class="row">
            <div class="col-sm-12">
                <datatable ref="related_items_table" id="related_items_table" :dtOptions="dtOptionsRelatedItems" :dtHeaders="dtHeadersRelatedItems" />
            </div>
        </div></div>
        <div>
            <WeakLinks />
        </div>
    </div>
</template>
<script>
import Vue from "vue";
import datatable from '@vue-utils/datatable.vue'
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import moment from 'moment';
import 'bootstrap/dist/css/bootstrap.css';
import 'eonasdan-bootstrap-datetimepicker';
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import WeakLinks from '@/components/common/weak_links.vue';

export default {
  name: "RelatedItems",
  data: function() {
    return {
      dtHeadersRelatedItems: [
          'Number',
          'Type',
          'Description',
          'Action',
      ],
      dtOptionsRelatedItems: {
          columns: [
              {
                  data: 'identifier',
              },
              {
                  data: 'model_name',
              },
              {
                  data: 'descriptor',
              },
              {
                  data: 'Action',
                  mRender: function(data, type, row){
                      // return '<a href="#" class="remove_button" data-offender-id="' + row.id + '">Remove</a>';
                      return '<a href="#">View (not implemented)</a>';
                  }
              },
          ]
      },
    };
  },
  components: {
    datatable,
    WeakLinks,
  },
  watch: {
      displayedEntity: {
          handler: function (){
              this.constructRelatedItemsTable();
          },
          deep: true
      },
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
    ...mapGetters('inspectionStore', {
      inspection: "inspection",
    }),
    ...mapGetters('offenceStore', {
      offence: "offence",
    }),
    ...mapGetters('sanctionOutcomeStore', {
      sanction_outcome: "sanction_outcome",
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    displayedEntity: function() {
        if (this.call_email && this.call_email.id) {
            return this.call_email;
        } else if (this.inspection && this.inspection.id) {
            return this.inspection;
        } else if (this.offence && this.offence.id) {
            return this.offence;
        } else if (this.sanction_outcome && this.sanction_outcome.id) {
            return this.sanction_outcome;
        }
    },

  },
  methods: {
    constructRelatedItemsTable: function() {
        console.log('constructRelatedItemsTable');
        this.$refs.related_items_table.vmDataTable.clear().draw();

        if(this.displayedEntity && this.displayedEntity.related_items){
          for(let i = 0; i< this.displayedEntity.related_items.length; i++){
            let already_exists = this.$refs.related_items_table.vmDataTable.columns(0).data()[0].includes(this.displayedEntity.related_items[i].id);

            if (!already_exists){
                this.$refs.related_items_table.vmDataTable.row.add(
                    {
                        'identifier': this.displayedEntity.related_items[i].identifier,
                        'descriptor': this.displayedEntity.related_items[i].descriptor,
                        'model_name': this.displayedEntity.related_items[i].model_name,
                        'Action': this.displayedEntity.related_items[i],
                    }
                ).draw();
            }
          }
        }
    },
  },
  created: async function() {
  },
  mounted: function() {
      this.$nextTick(() => {
          this.constructRelatedItemsTable();
      });
  }
};
</script>

<style lang="css">
.action-button {
    margin-top: 5px;
}
#main-column {
  padding-left: 2%;
  padding-right: 0;
  margin-bottom: 50px;
}
.awesomplete {
    width: 100% !important;
}
.nav>li>a:focus, .nav>li>a:hover {
  text-decoration: none;
  background-color: #eee;
}
.nav-item {
  background-color: hsla(0, 0%, 78%, .8) !important;
  margin-bottom: 2px;
}
.advice-url-label {
  visibility: hidden;
}
.advice-url {
  padding-left: 20%;
}
</style>
