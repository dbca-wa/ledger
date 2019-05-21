<template lang="html">
    <div>
        <div class="col-md-3">
            <h3>Return: {{ returns.lodgement_number }}</h3>
        </div>
        <div class="col-md-1">&nbsp;</div>
        <div :class="`${form_width ? form_width : 'col-md-9'}`">
            <div id="tabs">
                <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs" >
                    <li class="active"><a id="tab_1">1. Return</a></li>
                    <li v-if="returns.has_payment" ><a id="tab_2">2. Confirmation</a></li>
                </ul>
            </div>
            {{ this.$slots.default }}
        </div>
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
        returns_tab_id: 0,
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
    },
  },
  computed: {
    ...mapGetters([
      'returns',
      'selected_returns_tab_id',
    ]),
    returnsData: function() {
        return this.returns;
    }
  },
  methods: {
    ...mapActions([
      'setReturnsTab',
    ]),
    selectReturnsTab: function(component) {
        this.returns_tab_id = component.id;
        this.setReturnsTab({id: component.id, name: component.label});
    },
    initReturnsTab: function() {
        let tabs_list = [];
        tabs_list.push({name: 'component.name', label: 'component.label', id: 'component.id'});
        this.setReturnsTab(tabs_list);
    },
    initFirstTab: function(){
        const tab = $('#tabs-section li:first-child a')[0];
        if(tab) {
            tab.click();
        }
    },
  },
  mounted: function() {

  },
}
</script>
