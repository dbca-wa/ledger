<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label :id="id">
                    <input :disabled="readonly" ref="Checkbox" :name="name" type="checkbox" data-parsley-required :data-conditions="options" @change="handleChange" :checked="isChecked" />
                    {{ label }}
                <template v-if="help_text">
                  <HelpText :help_text="help_text" />
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import HelpText from './help_text.vue'
export default {
  props: ['name', 'label', 'value', 'id', 'help_text', 'conditions', "handleChange","readonly"],
  components: {HelpText},
  computed: {
    isChecked: function() {
      return (this.value == 'on');
    },
    options: function() {
      return JSON.stringify(this.conditions);
    }
  },
  mounted:function () {
      let vm = this;
      if (vm.isChecked) {
          var input = this.$refs.Checkbox;
          var e = document.createEvent('HTMLEvents');
          e.initEvent('change', true, true);

          var disabledStatus = input.disabled;
          try {
              /* Firefox will not fire events for disabled widgets, so (temporarily) enabling them */
              if(disabledStatus) {
                  input.disabled = false;
              }
              input.dispatchEvent(e);
          } finally {
              if(disabledStatus) {
                  input.disabled = true;
              }
          }
      }
  }
}
</script>

<style lang="css">
</style>
