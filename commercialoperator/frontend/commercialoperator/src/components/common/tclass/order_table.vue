<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
            <!-- the next line required for saving value JSON-ified table to application.data - creates an invisible field -->
            <textarea readonly="readonly" class="form-control" rows="5" :name="name" style="display:none;">{{ value }}</textarea><br/>

            <div id="content-editable-table">
              <table class="table table-striped editable-table">
                <thead v-if="table.thead.length">
                  <tr>
                    <th v-for="(heading, index) in table.thead">
                      {{ table.thead[index] }}
                    </th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="(row, row_idx) in table.tbody">
                      <td v-if="col_types[index]=='select'" width="30%" v-for="(value, index) in row">
                          <v-select class="tbl_input" :options="options" v-model="row[index]" @change="park_change(row[index], row, row_idx)" :title="'Adult Price: '+ row[index] +  ', Child Price: ' + row[index]"i :disabled="disabled"/>
                      </td>

                      <td v-if="col_types[index]=='date'" v-for="(value, index) in row">
                          <input id="id_arrival_date" class="tbl_input" :type="col_types[index]" :max="expiry_date" :min="today()" v-model="row[index]" :required="isRequired" :onclick="isClickable" :disabled="row[0]=='' || row[0]==null" @change="date_change(row[index], row, row_idx)"/>
                      </td>

                      <td v-if="col_types[index]=='text' || col_types[index]=='number'" v-for="(value, index) in row">
                          <input :readonly="readonly" class="tbl_input" :type="col_types[index]" min="0" value="0" v-model="row[index]" :required="isRequired" :onclick="isClickable" :disabled="row[1]==''" @change="calcPrice(row[index], row, row_idx)"/>
                      </td>

                      <td v-if="col_types[index]=='total'" v-for="(value, index) in row">
                          <div class="currencyinput"><input class="tbl_input" :type="col_types[index]" min="0" value="0" v-model="row[index]" disabled/> </div>
                      </td>

                      <td v-if="!readonly">
                          <a class="fa fa-trash-o" v-on:click="deleteRow(row)" title="Delete row" style="cursor: pointer; color:red;" :disabled="disabled"></a>
                      </td>
                  </tr>

                  <tr>
                      <td colspan="5" align="right" >
                          <div><label>Total:</label></div>
                      </td>
                      <td align="left" >
                          <div class="currencyinput"><input class="tbl_input" :type="number" min="0" :value="total_price()" disabled/> </div>
                      </td>
                  </tr>

                </tbody>
                <span><button class="btn btn-primary" type="button" v-on:click="addRow()" :disabled="disabled">+</button>Add another park and/or date</span>

              </table>

              <!-- for debugging -->
              <!--
              <pre class="output">
                {{ value }}
              </pre>
              <pre class="output">
                {{ headers }}
              </pre>
              <pre class="output">
                {{ expiry_date }}
              </pre>
              -->
            </div>

        </div>
        <input type="hidden" class="form-control" :name="name" :value="value"/>
    </div>
</template>

<script>

import Vue from 'vue'
import vSelect from "vue-select"
Vue.component('v-select', vSelect)

export default {
    //props:["name","value", "expiry_date", "id", "isRequired", "help_text","help_text_assessor","assessorMode","label","readonly","comment_value","assessor_readonly", "help_text_url", "help_text_assessor_url"],
    props:{
        headers: [],
        options: [],
        name: String,
        label: String,
        expiry_date: String,
        id: String,
        isRequired: String,
        comment_value: String,
        disabled: Boolean,
        readonly:Boolean,
        value:{
            default:function () {
                return null;
            }
        },
    },

    components: {
    },

    /* Example schema config
       {
        "type": "table",
        "headers": "{\"Species\": \"text\", \"Quantity\": \"number\", \"Date\": \"date\", \"Taken\": \"checkbox\"}",
        "name": "Section2-0",
        "label": "The first table in section 2"
       }
    */
    data(){
        let vm = this;
        var value  =JSON.parse(vm.value);

        var headers = JSON.parse(vm.headers)
        vm.col_headers = Object.keys(headers);
        vm.col_types = Object.values(headers);

        vm._options = [
            {'label': 'Nungarin', 'value': 'Nungarin'},
            {'label': 'Ngaanyatjarraku', 'value': 'Ngaanyatjarraku'},
            {'label': 'Cuballing', 'value': 'Cuballing'}
        ];

        // setup initial empty row for display
        vm.init_row = vm.reset_row();
        //for(var i = 0, length = vm.col_headers.length; i < length; i++) { vm.init_row.push('')  }

        if (value == null) {
            vm.table = {
                    //thead: ['Heading 1'],
                    thead: vm.col_headers,
                    tbody: [
                        //['No header specified']
                        vm.init_row
                    ]
            }
        } else {
            vm.table = {
                    thead: value['thead'],
                    tbody: value['tbody']
            }
        }

        return { 
            idx_park: 0,
            idx_arrival_date: 1,
            idx_adult: 2,
            idx_child: 3,
            idx_free: 4,
            idx_price: 5,

            isClickable: "return true;" ,
            selected_park:{
                default:function () {
                    return {
                        value: String,
                        label: String,
                        prices: Object,
                    }
                }
            },
            net_park_prices:{
                default:function () {
                    return {
                        value: Number,
                        idx: Number,
                    }
                }
            },

        }
    },
    watch:{
    },
    beforeUpdate() {
    },
    filters: {
        _price: function(row_idx){
            let vm = this;
            return row_idx ? vm.net_park_prices[row_idx]: '';
        },
        price: function(dict, key){
            return dict[key];
        },
    },
    methods: {
        total_price: function() {
            let vm = this;
            var total = 0.0;
            for (var key in vm.table.tbody) { 
                total += isNaN(parseFloat(vm.table.tbody[key][vm.idx_price])) ? 0.00 : parseFloat(vm.table.tbody[key][vm.idx_price]);
            }
            return total.toFixed(2);
        },

        today: function() {
            var day = new Date();
            var dd = day.getDate();
            var mm = day.getMonth()+1; //January is 0!
            var yyyy = day.getFullYear();
             if(dd<10){
                    dd='0'+dd
                } 
                if(mm<10){
                    mm='0'+mm
                } 

            return yyyy+'-'+mm+'-'+dd;
        },
        reset_row: function() {
            var init_row = [];
            for(var i = 0, length = this.col_headers.length; i < length; i++) { init_row.push('')  }
            return init_row;
        },
        reset_row_part: function(row) {
            // reset part of the row (from date onwards)
            for(var i = 1, length = row.length; i < length; i++) { row[i]=''  }
            return row;
        },

        updateTableJSON: function() {
          let vm = this;
          vm.tableJSON = JSON.stringify(vm.table);
          vm.value = vm.tableJSON;
        },

        addRow: function() {
          let vm = this;
          var newRow = [];

          for(var i = 0, length = vm.table.thead.length; i < length; i++) {
            newRow.push('')
          }
          vm.table.tbody.push(newRow);

          vm.updateTableJSON();
        },
        deleteRow: function(row) {
            let vm = this;

            // pop row from data structure
            vm.table.tbody = vm.table.tbody.filter(function(item) {
                return item !== row
            })
            vm.updateTableJSON();
        },

        adult_price: function(row) {
            return row[this.idx_park] ? row[this.idx_park].prices.adult : '';
        },
        child_price: function(row) {
            return row[this.idx_park] ? row[this.idx_park].prices.child : '';
        },
        calcPrice: function(selected_park, row, row_idx) {
          let vm = this;
          if (selected_park) {
            console.log('*** ' + selected_park + ' row: ' + row);

            var adult_price = isNaN(parseInt(row[vm.idx_adult])) ? 0.00 : parseInt(row[vm.idx_adult]) * vm.adult_price(row);
            var child_price = isNaN(parseInt(row[vm.idx_child])) ? 0.00 : parseInt(row[vm.idx_child]) * vm.child_price(row);

            vm.net_park_prices[row_idx] = (adult_price + child_price).toFixed(2);
            vm.table.tbody[row_idx][vm.idx_price] = (adult_price + child_price).toFixed(2);
            vm.updateTableJSON();
          }
        },
        park_change: function(selected_park, row, row_idx) {
          let vm = this;
            if (selected_park==null) {
                // reset the row
                vm.table.tbody[row_idx] = vm.reset_row();
            }
            vm.updateTableJSON();
        },
        date_change: function(selected_date, row, row_idx) {
          let vm = this;
            if (selected_date==null || selected_date=='') {
                // reset part of the row (date onwards)
                vm.table.tbody[row_idx] = vm.reset_row_part(row);
            }
            vm.updateTableJSON();
        },
    },

    computed:{
        wc_version: function (){
            return this.$root.wc_version;
        },
    },


    mounted:function () {
        let vm = this;

        vm.updateTableJSON();

        //$('#content-editable-table').on('change', '[type="text"]', function() {
        $('#content-editable-table').on('change', '.tbl_input', function() {
            vm.updateTableJSON();
        });

        $("#content-editable-table").on("click", ".ibtnDel", function (event) {
            $(this).closest("tr").remove();
        });

        //if (vm.disabled) {
        //    vm.options = [];
        //    vm.options.push({value:0, label:'No parks available'})
        //}

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

        $("#id_arrival_date").keypress(function(event) {event.preventDefault();});
    }
}
</script>

<style scoped lang="css">
    .container {
      padding: 30px;
      width: 100%;
    }

    .editable-table
        input[type=number]{
            width: 40%;
        }

    .output {
      white-space: normal;
    }

    input[id="header"] {
        outline-style: none;
    }

    div.currencyinput{
        position:relative;
        padding-left: 15px;
    }

    div.currencyinput:after{
    position: absolute;
        left: 6px;
        top: 2px;
        content: '$';
    }
</style>

