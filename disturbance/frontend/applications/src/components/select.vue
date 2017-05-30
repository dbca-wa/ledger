<template lang="html">
    <div>
        <div class="form-group">
          <label>{{ label }}</label>
          <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" :title="help_text">&nbsp;</i>
          <select :id="selectid":name="name" class="form-control" :multiple="isMultiple" :data-conditions="cons" style="width:100%">
              <option value="">Select...</option>
              <option v-for="op in options"  :value="op.value" @change="handleChange" :selected="op.value == value">{{ op.label }}</option>
          </select>
      </div>
  </div>
</template>

<script>
var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
export default {
    props:{
        'name':String,
        'label':String,
        'help_text':String,
        "value":String,
        "options":Array,
        "conditions":Object,
        "handleChange":null,
        "isMultiple":{
            default:function () {
                return null;
            }
        }
    },
    data:function () {
        let vm =this;
        return{
            selected: (this.isMultiple) ? [] : "",
            selectid: "select"+vm._uid
        }
    },
    computed:{
        cons:function () {
            return JSON.stringify(this.conditions);
        }
    },
    methods:{
        init:function () {
            let vm =this;
            setTimeout(function (e) {
                   $('#'+vm.selectid).select2({
                       "theme": "bootstrap",
                       allowClear: true,
                       placeholder:"Select..."
                   }).
                   on("select2:select",function (e) {
                       var selected = $(e.currentTarget);
                       vm.handleChange(selected[0])
                       e.preventDefault();
                   }).
                   on("select2:unselect",function (e) {
                       var selected = $(e.currentTarget);
                        vm.handleChange(selected[0])
                        e.preventDefault();
                   });
               },100);
        }
    },
    mounted:function () {
        this.init();
    }
}
</script>

<style lang="css">
.select2-container {
  width: 100% !important;
}
</style>
