<template lang="html">
    <div class="form-group">
        <label>{{ label }}</label>
        <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
        <i data-toggle="tooltip" v-if="help_text_assessor && assessorMode" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text_assessor">&nbsp;</i>
        <div class='input-group date'>
            <input :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value"/>
            <span class="input-group-addon">
                <span class="glyphicon glyphicon-calendar"></span>
            </span>
        </div>
    </div>
</template>

<script>
import moment from 'moment'
import datetimepicker from 'datetimepicker'
export default {
  props: ['name', 'label', 'readonly', 'help_text', 'help_text_assessor', 'assessorMode', 'value', 'conditions', "handleChange"],
  computed: {
    isChecked: function() {
      //TODO return value from database
      return false;
    },
    options: function() {
      return JSON.stringify(this.conditions);
    }
  },
  mounted: function() {
    $('.date').datetimepicker({
      format: 'DD/MM/YYYY'
    });
  }
}
</script>

<style lang="css">
</style>
