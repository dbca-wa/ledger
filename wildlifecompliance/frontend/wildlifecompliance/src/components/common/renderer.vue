<template lang="html">
    <div>
        <div>
            <div id="scrollspy-heading" class="col-lg-12" >
                <h3>Application {{application.id}}: {{application.licence_type_short_name}}</h3>
            </div>
            <div class="col-md-3" >
                <div class="panel panel-default fixed">
                <div class="panel-heading">
                    <div class="dropdown">
                        <ul class="list-unstyled">
                        <li ><a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true"><h5>Sections<span class="caret"></span></h5></a>
                            <ul class="dropdown-menu" id="scrollspy-section" >
                            </ul>
                        </li>
                        </ul>
                    </div>
                </div>
                <div class="panel-body" style="padding:0">
                </div>
                </div>
            </div>
            <div class="col-md-9" id="tabs">
                <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs">
                    <li v-for="(activity, index) in listVisibleActivities">
                        <a :class="{'nav-link amendment-highlight': application.has_amendment}"
                            data-toggle="tab" v-on:click="selectTab(activity)">{{activity.label}}</a>
                    </li>
                </ul>
                <div class="tab-content">
                    <div v-for="(activity, index) in listVisibleActivities">
                        <AmendmentRequestDetails :activity_id="activity.id" />
                        <renderer-block
                            :component="activity"
                            :json_data="applicationData"
                            v-if="activity.id == selected_activity_tab_id"
                            v-bind:key="`renderer_block_${index}`"
                            />
                    </div>
                    {{ this.$slots.default }}
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import Vue from 'vue';
import { mapActions, mapGetters } from 'vuex';
import AmendmentRequestDetails from '@/components/forms/amendment_request_details.vue';
import Renderer from '@/utils/renderer'

export default {
  name: 'renderer-form',
  components: {
      AmendmentRequestDetails,
  },
  data: function() {
    return {
    }
  },
  props:{
  },
  computed: {
    ...mapGetters([
        'application',
        'selected_activity_tab_id',
        'visibleActivities',
    ]),
    listVisibleActivities: function() {
        return this.visibleActivities(
            ['issued', 'declined'],  // Hide by decision
            //['discarded']  // Hide by processing_status
        ).filter(activity => !this.application.has_amendment ||
            this.application.amendment_requests.find(
                request => request.licence_activity.id == activity.id
            )
        );
    },
    applicationData: function() {
        return this.application.data ? this.application.data[0] : null;
    }
  },
  methods: {
      ...mapActions([
          'setRendererTabs',
          'setActivityTab',
      ]),
      selectTab: function(component) {
          this.setActivityTab({id: component.id, name: component.label});
      }
  },
  mounted: function() {
      let tabs_list = [];
      for(let component of this.listVisibleActivities.filter(
          activity => activity.type == 'tab')) {
            if(!this.selected_activity_tab_id) {
                this.selectTab(component);
            }
            tabs_list.push({name: component.name,
                            label: component.label,
                            id: component.id
                            });
      }
      this.setRendererTabs(tabs_list);
  }
}
</script>
