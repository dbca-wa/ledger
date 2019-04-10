<template lang="html">
    <div>
    </div>
</template>


<script>
import Vue from 'vue';
import { mapActions, mapGetters } from 'vuex';
import '@/scss/forms/form.scss';

export default {
  name: 'returns-renderer-form',
  components: {
  },
  data: function() {
    return {
        return_tab_id: 0,
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
    // getters
    //...mapGetters([
    //    'application',
    //    'selected_activity_tab_id',
    //    'renderer_tabs',
    //    'unfinishedActivities',
    //    'sectionsForTab',
    //]),
  },
  methods: {
    // setters
    //...mapActions([
    //    'setRendererTabs',
    //    'setRendererSections',
    //    'setActivityTab',
    //]),
  },
  mounted: function() {
    // initialise functions.
  },
}
</script>
