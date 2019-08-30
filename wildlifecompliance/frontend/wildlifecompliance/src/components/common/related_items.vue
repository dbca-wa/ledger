<template>
    <div>
        <div class="col-sm-12 form-group"><div class="row">
            <div class="col-sm-12">
                <datatable ref="related_items_table" id="related-items-table" :dtOptions="dtOptionsRelatedItems" :dtHeaders="dtHeadersRelatedItems" />
            </div>
        </div></div>
        <div>
            <!--WeakLinks @weak-link-selected="createWeakLink"/-->
            <WeakLinks ref="weak_links_lookup"/>
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
    props: {
          parent_update_related_items: {
              type: Function,
          },
    },

    data: function() {
    return {
      displayedEntityType: null,
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
                      if (!row.Action.weak_link) {
                          return row.Action.action_url;
                      } else if (row.Action.weak_link && row.Action.can_user_action) {
                          return '<a href="#" class="remove_button" second-content-type="' + row.Action.second_content_type + '" second-object-id="' + row.Action.second_object_id + '">Remove</a>';
                      } else {
                          return '';
                      }
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
            this.displayedEntityType = 'callemail';
            return this.call_email;
        } else if (this.inspection && this.inspection.id) {
            this.displayedEntityType = 'inspection';
            return this.inspection;
        } else if (this.offence && this.offence.id) {
            this.displayedEntityType = 'offence';
            return this.offence;
        } else if (this.sanction_outcome && this.sanction_outcome.id) {
            this.displayedEntityType = 'sanctionoutcome';
            return this.sanction_outcome;
        }
    },

  },
  methods: {
    createWeakLink: async function() {
        let url = '/api/create_weak_link/'
        let payload = {
            'can_user_action': this.displayedEntity.can_user_action,
            'first_content_type': this.displayedEntityType,
            'first_object_id': this.displayedEntity.id,
            'second_content_type': this.$refs.weak_links_lookup.second_content_type,
            'second_object_id': this.$refs.weak_links_lookup.second_object_id,
        }
        // post payload to url, then
        let relatedItems = await Vue.http.post(url, payload);
        console.log(relatedItems)
        if (relatedItems.ok) {
            await this.parent_update_related_items(relatedItems.body);
        }

    },
    removeWeakLink: async function(e) {
        let secondContentType = e.target.getAttribute("second-content-type");
        let secondObjectId = e.target.getAttribute("second-object-id");
        let url = '/api/remove_weak_link/'
        let payload = {
            'can_user_action': this.displayedEntity.can_user_action,
            'first_content_type': this.displayedEntityType,
            'first_object_id': this.displayedEntity.id,
            'second_content_type': secondContentType,
            'second_object_id': secondObjectId,
        }
        // post payload to url, then
        let relatedItems = await Vue.http.post(url, payload);
        console.log(relatedItems)
        if (relatedItems.ok) {
            await this.parent_update_related_items(relatedItems.body);
        }
    },

    constructRelatedItemsTable: function() {
        console.log('constructRelatedItemsTable');
        this.$refs.related_items_table.vmDataTable.clear().draw();

        if(this.displayedEntity.related_items){
          for(let i = 0; i< this.displayedEntity.related_items.length; i++){
            //let already_exists = this.$refs.related_items_table.vmDataTable.columns(0).data()[0].includes(this.displayedEntity.related_items[i].id);

            let actionColumn = new Object();
            Object.assign(actionColumn, this.displayedEntity.related_items[i]);
            actionColumn.can_user_action = this.displayedEntity.can_user_action;

            //if (!already_exists) {
            this.$refs.related_items_table.vmDataTable.row.add(
                {
                    'identifier': this.displayedEntity.related_items[i].identifier,
                    'descriptor': this.displayedEntity.related_items[i].descriptor,
                    'model_name': this.displayedEntity.related_items[i].model_name,
                    'Action': actionColumn,
                }
            ).draw();
            //}
          }
        }
    },
    addEventListeners: function() {
      $('#related-items-table').on(
          'click',
          '.remove_button',
          this.removeWeakLink,
          );
    }
  },
  created: async function() {
  },
  mounted: function() {
      this.$nextTick(() => {
          this.addEventListeners();
          this.constructRelatedItemsTable();

      });
  }
};
</script>

<style lang="css">
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
.action-button {
    margin-top: 5px;
}
</style>
