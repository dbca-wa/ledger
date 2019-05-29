<template lang="html">
     <div>
          <label :id="id" :required="isRequired" > {{ label }} </label>
          <template v-if="help_text">
              <HelpText :help_text="help_text" />
          </template>
          <template v-if="help_text_url">
              <HelpTextUrl :help_text_url="help_text_url" />
          </template>
          <div class="grid-container">
              <div>
                  <label v-if="headers" v-for="header in headers" >
                      <input class="form-control" v-model="header.label" disabled="disabled" /> <br/>
                      <div v-for ="field in field_data" >
                          <div v-for="(title,key) in field" v-if="key == header.name"
                              :name="`${name}::${header.name}`" v-model="title.value" v-bind:key="`f_${key}`" >
                              <TextField v-if="header.type === 'date'"
                                type="string"
                                :label="title.label"
                                :field_data="title"
                                :name="name + '::' + header.name"
                                :readonly="header.is_readonly"
                                :help_text="help_text"
                                :isRequired="header.isRequired"
                                :help_text_url="help_text_url"
                              />
                              <TextField v-if="header.type === 'number'"
                                type="string"
                                :name="name + '::' + header.name"
                                :field_data="title"
                                :min="header.min"
                                :max="header.max"
                                :label="title.label"
                                :help_text="help_text"
                                :readonly="header.is_readonly"
                                :isRequired="header.isRequired"
                                :help_text_url="help_text_url"
                              />
                              <TextField v-if="header.type === 'string'"
                                type="string"
                                :name="name + '::' + header.name"
                                :field_data="title"
                                :label="title.label"
                                :help_text="help_text"
                                :readonly="header.is_readonly"
                                :isRequired="header.isRequired"
                                :help_text_url="help_text_url"
                              />
                          </div>
                      </div>
                  </label>
              </div>
          </div>
          <input type="button" class="btn btn-primary" @click.prevent="addRow()" >Add Row</button>
     </div>
</template>
<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import DateField from './date-field.vue'
import TextField from './text.vue'
const GridBlock = {
  /* Example schema config
     {
      "type": "grid",
      "headers": "{'label': 'LOCATION','type': 'string','required': 'true'}",
      "name": "returns_data",
      "label": "Returns Data"
     }
  */
  props: ['field_data','headers','name', 'label', 'value', 'id', 'help_text', 'help_text_url', "readonly", "isRequired"],
  components: {HelpText, HelpTextUrl, TextField, DateField},
  data: function() {
    let vm = this;
    if(vm.readonly) {
      return { isClickable: "return false;" }
    } else {
      return { isClickable: "return true;" }
    }
  },
  methods: {
    addRow: function(e) {
      var grid_data = this._props['field_data'];
      let index = grid_data.length
      let dataObj = Object.assign({}, grid_data[0]);

      // schema data type on each field is validated - error value required.
      for(let key in dataObj) { dataObj[key] = {'value':'', 'error':''}};

      grid_data.push(dataObj);
    },
    addColumn: function(e) {
    },
    addArea: function(e) {
    },
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

export default GridBlock;
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
    .grid-container {
        display: grid;
        width: 100%;
        height: 300px;
        border: 1px solid #ffffff;
        grid-template-columns: [labels] 2048px;
        overflow: scroll;
        background-color: #ffffff;
        justify-content: start;
    }
    .grid-container > label {
        grid-column: labels;
        grid-row: auto;
    }
</style>






