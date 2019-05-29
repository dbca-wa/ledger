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
                      <input class="form-control" v-model="header.label" disabled="disabled" />
                      <div class="grid-item" v-for ="(field, cnt) in field_data" >
                          <div v-for="(title,key) in field" v-if="key == header.name"
                              :name="`${name}::${header.name}`" :v-model="title.value" :key="`f_${key}`" >

                              <div v-if="header.type === 'date'" >
                                  <input type="text"
                                          :id="header.type"
                                          :disabled="header.readonly"
                                          :name="name + '::' + header.name"
                                          class="form-control"
                                          placeholder="DD/MM/YYYY"
                                          v-model="title.value"
                                          :required="isRequired"
                                  />
                              </div>

                              <div v-if="header.type === 'string'">
                                <input :disabled="header.readonly"
                                        :type="header.type"
                                       class="form-control"
                                       :name="name + '::' + header.name"
                                       v-model="title.value"
                                       :required="isRequired"
                                />
                              </div>

                              <div v-if="header.type === 'number'" >
                                <input  :disabled="header.readonly"
                                        type="text"
                                        class="form-control"
                                        :name="name + '::' + header.name"
                                        v-model="title.value"
                                        :required="isRequired"
                                 />
                              </div>
                          </div>
                      </div>
                  </label>
              </div>
          </div>
          <div >
             <button class="btn btn-link" @click.prevent="addRow()" >Add Row</button>
          </div>
     </div>
</template>
<script>
import datetimepicker from 'datetimepicker';
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import DateField from './date-field.vue'
import TextField from './text.vue'
const GridBlock = {
  /* Example schema config
     Note: Each grid-item requires a unique name ie.'Table-Name::location'.
     {
      "type": "grid",
      "headers": "{'label': 'LOCATION','name': 'location', 'type': 'string','required': 'true'}",
      "name": "table-name",
      "label": "Grid format of Table Data"
      "data" : "{'key': 'value'}"
     }
  */
  props: ['field_data','headers','name', 'label', 'id', 'help_text', 'help_text_url', "readonly", "isRequired"],
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
      this.grid_item = this._props['field_data'];
      let index = this.grid_item.length
      let fieldObj = Object.assign({}, this.grid_item[0]);
      // schema data type on each field is validated - error value required.
      for(let key in fieldObj) {
        fieldObj[key] = {'value':'', 'error':''}
      };
      this.grid_item.push(fieldObj);
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
    },
    value: {
      get: function() {
         return this.field_data.value;
      },
      set: function(value) {
         this.field_data.value = value;
      }
    },
  },
  mounted:function () {
      $(`[id='date']`).datetimepicker({
          format: 'DD/MM/YYYY'
      }).off('dp.change').on('dp.change', (e) => {
          this.value = $(e.target).data('DateTimePicker').date().format('DD/MM/YYYY');
      });
      if (this.isChecked) {
          var input = this.$refs.Checkbox;
          var e = document.createEvent('HTMLEvents');
          e.initEvent('change', true, true);

          /* replacing input.disabled with onclick because disabled checkbox does NOT get posted with form on submit */
          if(this.readonly) {
              this.isClickable = "return false;";
          } else {
              this.isClickable = "return true;";
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
        grid-template-columns: [labels] 5120px;
        grid-template-rows: auto;
        overflow: scroll;
        background-color: #ffffff;
    }
    .grid-container > label {
        grid-column: labels;
        grid-row: auto;
    }
    .grid-item {
        grid-column: 1 / 1;
        grid-row: 1 / 1;
        border: 1px solid #ffffff;
    }
</style>






