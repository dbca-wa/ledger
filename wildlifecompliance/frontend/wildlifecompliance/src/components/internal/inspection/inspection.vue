<template lang="html">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <h3>Inspection: {{ inspection.number }}</h3>
        </div>
        
      </div>
          <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                </div>
            </div>

            
          </div>

          <div class="col-md-9" id="main-column">  
            <div class="row">

                <div class="container-fluid">
                    <ul class="nav nav-pills aho2">
                        <li class="nav-item active"><a data-toggle="tab" :href="'#'+iTab">Inspection</a></li>
                        <li class="nav-item"><a data-toggle="tab" :href="'#'+rTab">Related Items</a></li>
                    </ul>
                    <div class="tab-content">
                        <div :id="iTab" class="tab-pane fade in active">

                          <FormSection :formCollapse="false" label="Caller" Index="0">
                            
                            <div class="row"><div class="col-sm-8 form-group">
                              <label class="col-sm-12">Title</label>
                              <input :readonly="readonlyForm" class="form-control" v-model="inspection.title"/>
                            </div></div>
                            <div class="col-sm-4 form-group"><div class="row">
                              <label class="col-sm-12">Details</label>
                            <textarea :readonly="readonlyForm" class="form-control" v-model="inspection.details"/>
                            </div></div>
                            
                            
                          </FormSection>
            
                          
                        </div>  
                        <div :id="rTab" class="tab-pane fade in">
                            <FormSection :formCollapse="false" label="Related Items">
                                <div class="col-sm-12 form-group"><div class="row">
                                    <div class="col-sm-12">
                                        <datatable ref="related_items_table" id="related_items_table" :dtOptions="dtOptionsRelatedItems" :dtHeaders="dtHeadersRelatedItems" />
                                    </div>
                                </div></div>
                            </FormSection>
                        </div>
                    </div>
                </div>       


            </div>          
          </div>

        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                        <div class="navbar-inner">
                            <div class="container">
                                <p class="pull-right" style="margin-top:5px;">
                                    
                                    <input type="button" @click.prevent="saveExit" class="btn btn-primary" value="Save and Exit"/>
                                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                </p>
                            </div>
                        </div>
        </div>          
        
    </div>
</template>
<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";

import CommsLogs from "@common-components/comms_logs.vue";
import datatable from '@vue-utils/datatable.vue'
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import moment from 'moment';
import 'bootstrap/dist/css/bootstrap.css';
import 'eonasdan-bootstrap-datetimepicker';

export default {
  name: "ViewInspection",
  data: function() {
    return {
      iTab: 'iTab'+this._uid,
      rTab: 'rTab'+this._uid,
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
      disabledDates: {
        from: new Date(),
      },
      workflow_type: '',
      
      sectionLabel: "Details",
      sectionIndex: 1,
      pBody: "pBody" + this._uid,
      loading: [],
      
      //callemailTab: "callemailTab" + this._uid,
      comms_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/comms_log"
      ),
      comms_add_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/add_comms_log"
      ),
      logs_url: helpers.add_endpoint_json(
        api_endpoints.inspection,
        this.$route.params.inspection_id + "/action_log"
      ),
      workflowBindId: '',
    };
  },
  components: {
    CommsLogs,
    FormSection,
    datatable,
  },
  watch: {
      call_email: {
          handler: function (){
              this.constructRelatedItemsTable();
          },
          deep: true
      },
  },
  computed: {
    ...mapGetters('inspectionStore', {
      inspection: "inspection",
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    
    readonlyForm: function() {
        return false;
    },
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ...mapActions('inspectionStore', {
      loadInspection: 'loadInspection',
      saveInspection: 'saveInspection',
      setInspection: 'setInspection', 
    }),
    
    updateWorkflowBindId: function() {
        let timeNow = Date.now()
        if (this.workflow_type) {
            this.workflowBindId = this.workflow_type + '_' + timeNow.toString();
        } else {
            this.workflowBindId = timeNow.toString();
        }
    },
    constructRelatedItemsTable: function() {
        console.log('constructRelatedItemsTable');
        
        let vm = this;
        
        vm.$refs.related_items_table.vmDataTable.clear().draw();

        if(vm.call_email.related_items){
          for(let i = 0; i<vm.call_email.related_items.length; i++){
            let already_exists = vm.$refs.related_items_table.vmDataTable.columns(0).data()[0].includes(vm.call_email.related_items[i].id);

            if (!already_exists){
                vm.$refs.related_items_table.vmDataTable.row.add(
                    {
                        'identifier': vm.call_email.related_items[i].identifier,
                        'descriptor': vm.call_email.related_items[i].descriptor,
                        'model_name': vm.call_email.related_items[i].model_name,
                        'Action': vm.call_email.related_items[i],
                    }
                ).draw();
            }
          }
        }
    },
    addWorkflow(workflow_type) {
      this.workflow_type = workflow_type;
      this.updateWorkflowBindId();
      this.$nextTick(() => {
        this.$refs.add_workflow.isModalOpen = true;
      });
      // this.$refs.add_workflow.isModalOpen = true;
    },
    offence(){
      this.$refs.offence.isModalOpen = true;
    },
    save: async function () {
        if (this.inspection.id) {
            await this.saveInspection({ route: false, crud: 'save' });
        } else {
            await this.saveInspection({ route: false, crud: 'create'});
            this.$nextTick(function () {
                this.$router.push(
                  { name: 'view-inspection', 
                    params: { id: this.inspection.id }
                  });
            });
        }
    },
    saveExit: async function() {
      if (this.inspection.id) {
        await this.saveInspection({ route: true, crud: 'save' });
      } else {
        await this.saveInspection({ route: true, crud: 'create'});
      }
    },
    duplicate: async function() {
      await this.saveInspection({ route: false, crud: 'duplicate'});
    },
  },
  beforeRouteEnter: function(to, from, next) {
      console.log(to);
            next(async (vm) => {
                await vm.loadInspection({ inspection_id: to.params.inspection_id });
                
            });
  },
  created: async function() {
      console.log(this)
    
    //if (this.$route.params.inspection_id) {
      //await this.loadInspection({ inspection_id: this.$route.params.inspection_id });
    //}
    
  },
  mounted: function() {
      let vm = this;
      $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
          var chev = $( this ).children()[ 0 ];
          window.setTimeout( function () {
              $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
          }, 100 );
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
</style>
