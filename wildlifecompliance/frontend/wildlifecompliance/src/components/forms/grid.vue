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
              <div v-for="(grid,index) in component">
                  <label v-if="grid.headers" v-for="header in grid.headers">
                      <input class="form-control" v-model="header.label"  disabled="disabled">
                  </label>
              </div>
              <div v-for="(grid,index) in component">
                  <label v-if="grid.headers" v-for="header in grid.headers">
                      <div v-for ="field in grid.data">
                          <input v-for="(title,key) in field" v-if="key == header.label" class="form-control"
                              :name="`${grid.name}::${header.label}`" v-model="title.value" >
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
const GridBlock = {
  /* Example schema config
     {
      "type": "grid",
      "headers": "{'label': 'LOCATION','type': 'string','required': 'true'}",
      "name": "returns_data",
      "label": "Returns Data"
     }
  */
  props: ['name', 'label', 'value', 'component', 'id', 'help_text', 'help_text_url', "readonly", "isRequired"],
  components: {HelpText, HelpTextUrl},
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
      var component_data = this._props['component'][0]['data'];
      let dataObj = Object.assign({}, component_data[0]);
      for(let key in dataObj) { dataObj[key] = '' };
      component_data.push(dataObj);
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
      console.log(vm)
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
        grid-template-columns: [labels] 2048px;
        overflow: scroll;
    }
    .grid-container > div {

    }
    .grid-container > label {
        grid-column: labels;
        grid-row: auto;
        border: 5px solid #000000;
        background-color: #ffffff;
    }
    .grid-container > head {
        grid-column: col-start;
    }
    .header {
        background-color: yellow;
        grid-area: hd;
    }
</style>






