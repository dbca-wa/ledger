<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label :id="id">
                <input :onclick="isClickable" ref="Checkbox" :name="name" type="checkbox" :class="group" data-parsley-required :data-conditions="options" @change="handleChange" :checked="isChecked" :required="isRequired"/>
                {{ label }}
                <template v-if="help_text">
                  <HelpText :help_text="help_text" />
                </template>
                <template v-if="help_text_url">
                  <HelpTextUrl :help_text_url="help_text_url" />
                </template>

            </div>
        </div>
    </div>
</template>

<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
  props: ['name', 'label', 'value', 'group', 'id', 'help_text', 'help_text_url', 'conditions', "handleChange","readonly", "isRequired"],
  components: {HelpText, HelpTextUrl},
  data: function() {
    let vm = this;
    if(vm.readonly) {
      return { isClickable: "return false;" }
    } else {
      return { isClickable: "return true;" }
    }
  },
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

          /* replacing input.disabled with onclick because disabled checkbox does NOT get posted with form on submit */
          if(vm.readonly) {
              vm.isClickable = "return false;";
          } else {
              vm.isClickable = "return true;";
		  }
          input.dispatchEvent(e);
      }
  }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
