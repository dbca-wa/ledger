<template lang="html">
    <div>
        <div class="col-md-3">
            <h3>Return: {{ returns.id }}</h3>
        </div>
        <div :class="`${form_width ? form_width : 'col-md-9'}`" id="returns-tabs">
            <div >
              <ul class="nav nav-tabs">
                <li ><a data-toggle="tab_1">Return</a></li>
              </ul>
            </div>
            <div class="tab-content">
              {{ this.$slots.default }}
            </div>
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
    selectTab: function(component) {
        this.returns_tab_id = component.id;
        this.setReturnsTab({id: component.id, name: component.label});
    },
  },
  mounted: function() {

  },
}
</script>
