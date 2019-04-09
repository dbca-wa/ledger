<template lang="html">
    
    <div>
        <h3>compliance renderer</h3>
        <div v-if="withSectionsSelector" class="col-lg-12" >
        <!--
            <h3>Application {{application.id}}: {{application.licence_type_short_name}}</h3>
        -->
        </div>
        <div v-if="withSectionsSelector" class="col-md-3 sections-dropdown">
            <affix class="sections-menu" relative-element-selector="#tabs">
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
        <div :class="`${form_width ? form_width : 'col-md-9'}`" id="tabs">
<!--
            <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs">
                <li v-for="(call, index) in ['99', '2']">
                    <a :class="{'nav-link amendment-highlight': application.has_amendment}"
                        data-toggle="tab" v-on:click="selectTab(activity)">{{activity.label}}</a>
                </li>
            
            </ul>
-->

            <div class="tab-content">
                <!--
                <div v-for="(data, index) in callEmailData">
                -->
                    <!--
                        v-if="activity.id == selected_activity_tab_id"
                    v-bind:key="`renderer_block_${index}`"
                    -->

                    <h3>compliance renderer block</h3>
                    
                    <div v-for="(col, index) in call_email.schema">
                        <h3>{{ call_email.schema }}</h3>
                        
                        <compliance-renderer-block
                        :component="call_email"
                        :json_data="call_email.schema"
                        
                        />
                    
                    </div>
                <!--
                {{ this.$slots.default }}
                -->
            </div>
            
        </div>
    </div>
 
</template>


<script>
import Vue from 'vue';
import { mapState, mapActions, mapGetters } from 'vuex';
//import ComplianceRendererBlock from './compliance_renderer_block'
//import { createNamespacedHelpers } from 'vuex'

/*
import { createNameSpacedHelpers } from '../../store/index.js'
const { 
    "renderermapState": mapState, 
    "renderermapGetters": mapGetters, 
    "renderermapActions": mapActions 
    } = createNameSpacedHelpers('complianceRendererStore')
const { 
    "callemailmapState": mapState, 
    "callemailmapGetters": mapGetters, 
    "callemailmapActions": mapActions 
    } = createNameSpacedHelpers('callemailStore')
*/
//const { mapState, mapGetters, mapActions } = createNamespacedHelpers('callemailStore')

//import CallEmail from '../../components/internal/call_email/call_email.vue'
//import AmendmentRequestDetails from '@/components/forms/amendment_request_details.vue';
import '@/scss/forms/form.scss';

export default {
  name: 'compliance-renderer-form',
  components: {
      //ComplianceRendererBlock
      //AmendmentRequestDetails,
      //CallEmail
  },
  data: function() {
    console.log("data");
    console.log(this.call_email);
    return {
        section_tab_id: 0,
    }
  },
  props:{
    withSectionsSelector:{
        type: Boolean,
        default: true
    },
    form_width: {
        type: String,
        default: 'col-md-9'
    }
  },
  computed: {
    /*
    ...callemailmapGetters([
        'call_email',
        //'application',
        //'selected_activity_tab_id',
    ]),
    ...renderermapGetters([
        //'application',
        //'selected_activity_tab_id',
        'renderer_tabs',
        //'unfinishedActivities',
        'sectionsForTab',
    ]),
    */
   ...mapGetters({
       call_email: 'callemailStore/call_email',
       renderer_tabs: 'complianceRendererStore/renderer_tabs',
       sectionsForTab: 'complianceRendererStore/sectionsForTab',
   }),
    callEmailData: function() {
        return this.call_email.data ? this.call_email.data[0] : null;
    }
    /*
    listVisibleActivities: function() {
        return this.unfinishedActivities;
    },
    applicationData: function() {
        return this.application.data ? this.application.data[0] : null;
    }
    */
  },
  methods: {
    ...mapActions({
        setRendererTabs: 'complianceRendererStore/setRendererTabs',
        setRendererSections: 'complianceRendererStore/setRendererSections',
        //'setActivityTab',
    }),
    selectTab: function(component) {
        this.section_tab_id = component.id;
        //this.setActivityTab({id: component.id, name: component.label});
    },
    getSections: function(tab_id) {
        return tab_id == this.section_tab_id ? this.sectionsForTab(tab_id) : [];
    },
    
    initRendererTabs: function() {
        let tabs_list = [];
        tabs_list.push({name: "tab_name",
                                label: "tab_label",
                                id: "tab_id"
                                });
        /*
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
        */
        this.setRendererTabs(tabs_list);
    },
    initRendererSections: function() {
        let sections = {};
        /*
        for(let component of this.listVisibleActivities.filter(
            activity => activity.type == 'tab' && activity.children)) {
                sections[component.id] = [];
                for(let section of component.children) {
                    sections[component.id].push({
                        name: section.name,
                        label: section.label
                    });
                }
                */
        sections[component.id].push({
                        name: section.name,
                        label: section.label
                    });
        
        this.setRendererSections(sections);
    },
    
    sectionClick: function(component) {
        if(this.section_tab_id == component.id) {
            this.section_tab_id = 0;  // Collapse the expanded panel upon double click.
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
