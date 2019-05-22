<template lang="html">
    <div>
        <div class="col-md-3">
            <h3>Return: {{ returns.lodgement_number }}</h3>
            <div v-if="returns.format === 'sheet'">
                <label>Species on Return:</label>
                <div v-for="species in returns.sheet_species_list">
                    <a class="change-species" :species_id="species" :href="'/external/return/sheet/'+returns.id+'/'+species"><h5>{{fullSpeciesList[species]}}</h5></a>
                </div>
            </div>
        </div>
        <div class="col-md-1">&nbsp;</div>
        <div :class="`${form_width ? form_width : 'col-md-9'}`">
            <div id="tabs" >
                <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs" >
                    <li class="active"><a id="0">1. Return</a></li>
                    <li v-if="returns.has_payment" ><a id="1">2. Confirmation</a></li>
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
        fullSpeciesList: {'': ''},
        //fullSpeciesList: {'S000001': 'Western Grey Kangaroo', 'S000002': 'Western Red Kangaroo',
        //                  'S000003': 'Blue Banded Bee', 'S000004': 'Orange-Browed Resin Bee'},
        returns_tab_id: 0,
    }
  },
  props:{
    form_width: {
        type: String,
        default: 'col-md-9'
    },
  },
  computed: {
    ...mapGetters([
      'returns',
      'returns_tabs',
      'selected_returns_tab_id',
    ]),
    returnsData: function() {
        return this.returns;
    }
  },
  methods: {
    ...mapActions([
      'setReturnsTabs',
      'setReturnsSpecies',
    ]),
    selectReturnsTab: function(component) {
        this.returns_tab_id = component.id;
        this.setReturnsTab({id: component.id, name: component.label});
    },
    initReturnsTab: function() {
        console.log('initReturnsTab')
        let tabs_list = [{name: 'step-0', label: '1. Return', id: 0},
                         {name: 'step-1', label: '2. Confirmation', id: 1},
                        ];
        this.setReturnsTabs(tabs_list);
    },
  },
}
</script>
