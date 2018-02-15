<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label>
                    <input :disabled="readonly" ref="Checkbox" :name="name" type="checkbox" data-parsley-required :data-conditions="options" @change="handleChange" :checked="isChecked" />
                    {{ label }}
                </label><i data-toggle="tooltip" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  props: ['name', 'label', 'value', 'help_text', 'conditions', "handleChange","reaodnly"],
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
