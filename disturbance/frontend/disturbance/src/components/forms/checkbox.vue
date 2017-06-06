<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label>
                    <input :name="name" type="checkbox" data-parsley-required :data-conditions="options" @change="handleChange" :checked="isChecked" />
                    {{ label }}
                </label><i data-toggle="tooltip" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  props: ['name', 'label', 'value', 'help_text', 'conditions', "handleChange"],
  computed: {
    isChecked: function() {
      return (this.value == 'on');
    },
    options: function() {
      return JSON.stringify(this.conditions);
    }
  }
}
</script>

<style lang="css">
</style>
