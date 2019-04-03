<template lang="html">
    <div>
        <div>
            <div class="col-lg-12" >
                <h3>Application {{application.id}}: {{application.licence_type_short_name}}</h3>
            </div>
            <div class="col-md-3 sections-dropdown">
                <affix class="sections-menu" relative-element-selector="#tabs" style="width: 249px">
                <div class="panel panel-default fixed">
                <div class="panel-heading">
                    <div class="dropdown">
                        <ul class="list-unstyled">
                            <li class="open">
                                <h5>Sections</span></h5>
                                <ul class="dropdown-menu dropdown-panel">
                                    <li v-for="(tab, tab_idx) in renderer_tabs" class='dropdown-submenu'>
                                        <a tabindex='-1' class='section-menu' v-on:click="sectionClick(tab)">
                                            {{tab.name}}
                                            <span 
                                                :class="`fa fa-caret-${
                                                    tab.id == section_tab_id ? 'up': 'down'
                                                }`"
                                            />
                                        </a>
                                        <ul class='dropdown-menu-right section-list' id='section-submenu' >
                                            <li v-for="(section, section_idx) in getSections(tab.id)">
                                                <a class='page-scroll section'
                                                    v-on:click="selectTab(tab)"
                                                    v-scroll-to="`#${section.name}`">
                                                    {{section.label}}
                                                </a>
                                            </li>
                                        </ul>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>
                <div class="panel-body" style="padding:0">
                </div>
                </div>
                </affix>
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
import Renderer from '@/utils/renderer';
import '@/scss/forms/form.scss';

export default {
  name: 'renderer-form',
  components: {
      AmendmentRequestDetails,
  },
  data: function() {
    return {
        section_tab_id: 0,
    }
  },
  props:{
  },
  computed: {
    ...mapGetters([
        'application',
        'selected_activity_tab_id',
        'renderer_tabs',
        'unfinishedActivities',
        'sectionsForTab',
    ]),
    listVisibleActivities: function() {
        return this.unfinishedActivities;
    },
    applicationData: function() {
        return this.application.data ? this.application.data[0] : null;
    }
  },
  methods: {
    ...mapActions([
        'setRendererTabs',
        'setRendererSections',
        'setActivityTab',
    ]),
    selectTab: function(component) {
        this.section_tab_id = component.id;
        this.setActivityTab({id: component.id, name: component.label});
    },
    getSections: function(tab_id) {
        return tab_id == this.section_tab_id ? this.sectionsForTab(tab_id) : [];
    },
    initRendererTabs: function() {
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
    },
    initRendererSections: function() {
        let sections = {};
        for(let component of this.listVisibleActivities.filter(
            activity => activity.type == 'tab' && activity.children)) {
                sections[component.id] = [];
                for(let section of component.children) {
                    sections[component.id].push({
                        name: section.name,
                        label: section.label
                    });
                }
        }
        this.setRendererSections(sections);
    },
    sectionClick: function(component) {
        if(this.section_tab_id == component.id) {
            this.section_tab_id = 0;
        }
        else {
            this.section_tab_id = component.id;
        }
    },
  },
  mounted: function() {
      this.initRendererTabs();
      this.initRendererSections();
  },
}
</script>
