<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label>
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
  props: ['name', 'label', 'value', 'help_text', 'conditions', "handleChange","readonly"],
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
          input.dispatchEvent(e);
      }
  }
}
</script>

<style lang="css">
</style>
