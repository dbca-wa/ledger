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

                      <td v-if="col_types[index]=='checkbox'" v-for="(value, index) in row">
                          <div><input class="tbl_input" :type="col_types[index]" v-model="row[index]" @change="calcPrice(row, row_idx)"/> </div>
                      </td>

                      <td v-if="col_types[index]=='text' || col_types[index]=='number'" v-for="(value, index) in row">
                          <input :readonly="readonly" class="tbl_input" :type="col_types[index]" min="0" value="0" v-model="row[index]" :required="isRequired" :onclick="isClickable" :disabled="row[1]==''" @change="calcPrice(row, row_idx)"/>
                      </td>

                      <td v-if="col_types[index]=='total'" v-for="(value, index) in row">
                          <div class="currencyinput"><input class="tbl_input" :type="col_types[index]" min="0" value="0" v-model="row[index]" disabled/> </div>
                      </td>

                      <td v-if="!readonly">
                          <a class="fa fa-trash-o" v-on:click="deleteRow(row)" title="Delete row" style="cursor: pointer; color:red;" :disabled="disabled"></a>
                      </td>
                  </tr>

                  <tr>
                      <td colspan="6" align="right" >
                          <div><label>Total:</label></div>
                      </td>
                      <td align="left">
                          <div class="currencyinput"><input class="tbl_input" type="total" min="0" :value="total_price()" disabled/> </div>
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

/*
        [
          {
            "arrival": "2019-11-26",
            "district": [
              {
                "district_id": 4,
                "total_adults": 4,
                "total_children": 4,
              },
              {
                "district_id": 5,
                "total_adults": 5,
                "total_children": 5,
              }
            ]
          },
*/

        //max_group_arrival_by_date[selected_date].total_adults
        return { 
            idx_park: 0,
            idx_arrival_date: 1,
            idx_same_group_tour: 2,
            idx_adult: 3,
            idx_child: 4,
            idx_free: 5,
            idx_price: 6,

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
            max_group_arrival: [],

            total_adults_same_group: 0,
            total_children_same_group: 0,
            districts: [],
            arrival_dates: [],

        }
    },
    watch:{
        options: function() {
            this.add_previous_visitors_same_group_tour();
            this.districts = this.get_districts();
            this.arrival_dates = this.get_arrival_dates();
            console.log('districts: ' + this.districts);
            console.log('arrivals: ' + this.arrival_dates);
        },
        table: function() {
            this.update_arrival_dates()
            console.log('arrival_dates: ' + this.arrival_dates);
        }
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
          newRow[vm.idx_same_group_tour] = false;
          
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

            /* need to recalc table prices, because same_tour group calc may have changed for one or more rows */
            vm.update_arrival_dates()
            vm.calcPrice(row, row_idx)
        },

        adult_price: function(row) {
            return row[this.idx_park] ? row[this.idx_park].prices.adult : '';
        },
        child_price: function(row) {
            return row[this.idx_park] ? row[this.idx_park].prices.child : '';
        },
        check: function(selected_park, row, row_idx) {
            console.log('check')
        },
        calcPrice: function(row, row_idx) {
          let vm = this;

          var total_adults_same_group = 0;
          var total_children_same_group = 0;
          var no_adults = 0;
          var no_children = 0;
          var selected_adults = 0;
          var selected_children = 0;
          var adult_price = 0;
          var child_price = 0;

          var selected_arrival_date = row[vm.idx_arrival_date]

          console.log('check')
          if (selected_arrival_date !== "") {

            for(var i=0; i<vm.districts.length; i++) {
                var district_id = vm.districts[i];

                for(var j=0; j<vm.arrival_dates.length; j++) {
                    var arrival = vm.arrival_dates[j];
                    var count = 0

                    for(var k=0; k<vm.table.tbody.length; k++) {
                        console.log('idx:  ' + k + ' ' + k);
                        var row = vm.table.tbody[k]
                        var same_tour_group_checked = row[vm.idx_same_group_tour]

                        if (district_id == row[0].district_id && arrival == row[1]) {
                            var row_idx = k

                            /*
                            console.log('*** idx ' + k + " - " + arrival + ' - ' + district_id + ' - ' + selected_park);
                            console.log(JSON.stringify(row));
                            console.log(JSON.stringify(vm.max_group_arrival));
                            //console.log(JSON.stringify(vm.max_group_arrival[]["district"].district_id)); 
                            console.log();
                            */

                            selected_adults = isNaN(parseInt(row[vm.idx_adult])) ? 0 : parseInt(row[vm.idx_adult])
                            selected_children = isNaN(parseInt(row[vm.idx_child])) ? 0 : parseInt(row[vm.idx_child])

                            /* Previous Sessions - total no_adults and children, excluding those from the same tour group, previously already paid for */
                            if (count == 0 && same_tour_group_checked) {
                                var [total_adults_same_group, total_children_same_group] = vm.get_visitors_same_group_tour(arrival, district_id)
                            }

                            if (same_tour_group_checked) {
                                no_adults = Math.max( selected_adults - total_adults_same_group, 0);
                                no_children = Math.max( selected_children - total_children_same_group, 0);
                            } else {
                                no_adults = selected_adults;
                                no_children = selected_children;
                            }

                            adult_price = no_adults==0 ? 0.00 : no_adults * vm.adult_price(row);
                            child_price = no_children==0 ? 0.00 : no_children * vm.child_price(row);

                            vm.net_park_prices[row_idx] = (adult_price + child_price).toFixed(2);
                            vm.table.tbody[row_idx][vm.idx_price] = (adult_price + child_price).toFixed(2);
                            vm.updateTableJSON();

                            if (same_tour_group_checked) {
                                total_adults_same_group = Math.max( total_adults_same_group, selected_adults )
                                total_children_same_group = Math.max( total_children_same_group, selected_children )
                                count += 1
                            }
                        }
                    }
                }
            }
          }
        },

        get_districts: function() {
            let vm = this;
            var districts = [];
            var district_id;
            for(var i=0, length=vm.options.length; i<length; i++) {
                district_id = vm.options[i].district_id
                if ( !(districts.indexOf(district_id) > -1)) {
                    districts.push(district_id)
                }
            }
            return districts.sort();
        },

        get_arrival_dates: function() {
            let vm = this;
            var arrival_dates = [];
            var keys = [];
            var arrival = '';
            for(var i=0; i<vm.options.length; i++) {
                keys = Object.keys(vm.options[i].max_group_arrival_by_date)
                for(var j=0; j<keys.length; j++) {
                    arrival = keys[j]
                    if ( !(arrival_dates.indexOf(arrival) > -1)) {
                        arrival_dates.push(arrival)
                    }
                }
            }
            return arrival_dates.sort();
        },

        add_arrival_date: function(arrival) {
            /* updates vm.arrival_dates list with the newly added row's selected arrival date */
            let vm = this;
            if ( !(vm.arrival_dates.indexOf(arrival) > -1)) {
                vm.arrival_dates.push(arrival)
            }
        },
        update_arrival_dates: function() {
            /* updates vm.arrival_dates list with current arrival dates from the table
               (initial update to vm.arrival_dates occured 
            */
            let vm = this;
            var selected_date = [];

            for(var i=0; i<vm.table.tbody.length; i++) {
                selected_date = vm.table.tbody[i][1]
                if ( !(vm.arrival_dates.indexOf(selected_date) > -1)) {
                    vm.arrival_dates.push(selected_date);
                }
            }
        },

        update_max_visitors: function() {
            for(var i=0, length=vm.table.tbody.length; i<length; i++) {
                vm.update_visitors_same_group_tour(arrival, district_id, Math.max( selected_adults, total_adults_same_group), Math.max( selected_children, total_children_same_group))

            }
        },

        get_max_visitors(arrival, district_id) {
            let vm = this;
            if (arrival in vm.tour_group_data && district_id in vm.tour_group_data[arrival]) {
                return [vm.tour_group_data[arrival][district_id].total_adults, vm.tour_group_data[arrival][district_id].total_children];
            } else {
                return [0, 0];
            }
        },
        park_change: function(selected_park, row, row_idx) {
          let vm = this;
            if (selected_park===null || selected_park==='') {
                // reset the row
                vm.table.tbody[row_idx] = vm.reset_row();
            }
            vm.updateTableJSON();

            /* need to recalc table prices, because same_tour group calc may have changed for one or more rows */
            vm.update_arrival_dates()
            vm.calcPrice(row, row_idx)
        },
        date_change: function(selected_date, row, row_idx) {
          let vm = this;
            if (selected_date===null || selected_date==='') {
                // reset part of the row (date onwards)
                vm.table.tbody[row_idx] = vm.reset_row_part(row);
            }
            vm.updateTableJSON();
            //vm.add_arrival_date(selected_date)

            /* need to recalc table prices, because same_tour group calc may have changed for one or more rows */
            vm.update_arrival_dates()
            vm.calcPrice(row, row_idx)
        },
        get_visitors_same_group_tour: function(arrival, district_id) {
            let vm = this;

            for(var i=0; i<vm.max_group_arrival.length; i++) { 
                if (arrival==vm.max_group_arrival[i].arrival) {
                    for(var j=0; j<vm.max_group_arrival[i].district.length; j++) { 
                        if (district_id==vm.max_group_arrival[i].district[j].district_id) {
                            return [ vm.max_group_arrival[i].district[j].total_adults, vm.max_group_arrival[i].district[j].total_children ]
                        }
                    }
                }
            }
            return [0, 0]
        },
        find_arrival_idx: function(arrival) {
            let vm = this;

            for(var i=0, length=vm.max_group_arrival.length; i<length; i++) { 
                if (arrival==vm.max_group_arrival[i].arrival) {
                    return i
                }
            }
            return -1
        },
        find_district_idx: function(arrival, district_id) {
            let vm = this;

            var idx = vm.find_arrival_idx(arrival)
            if (idx > -1) {
                for(var j=0, length=vm.max_group_arrival[idx].district.length; j<length; j++) { 
                    if (district_id==vm.max_group_arrival[idx].district[j].district_id) {
                        return j
                    }
                }
            }
            return -1
        },
        update_visitors_same_group_tour: function(arrival, district_id, total_adults, total_children) {
            /*
                Checks if a park in this district has been previously booked on the same arrival date, if so pay for only excess adults and children
            */
            let vm = this;

            var idx1 = vm.find_arrival_idx(arrival)
            var idx2 = vm.find_district_idx(arrival, district_id)
            if (idx1 > -1 && idx2 > -1) {
                if (district_id==vm.max_group_arrival[idx1]["district"][idx2]["district_id"]) {
                    vm.max_group_arrival[idx1]["arrival"] = arrival
                    vm.max_group_arrival[idx1]["district"][idx2]["total_adults"] = total_adults
                    vm.max_group_arrival[idx1]["district"][idx2]["total_children"] = total_children
                }
            } else if (idx1 > -1) {
                vm.max_group_arrival[idx1]["district"].push({district_id: district_id, total_adults: total_adults, total_children:total_children})
            } else if (idx2 > -1) {
                vm.max_group_arrival.push({arrival: arrival, district: [{district_id: district_id, total_adults: total_adults, total_children: total_children}]})
            }

        },
        add_previous_visitors_same_group_tour: function() {
            /*
                Checks if a park in this district has been previously booked on the same arrival date, if so add it to the max_group_arrival dict
            */
            let vm = this;
            var arrival_dates = []
            var arrival = ''
            var district_id = ''
            var key = ''
            var total_adults = 0;
            var total_children = 0;

            for(var i=0; i<vm.options.length; i++) {
                arrival_dates = Object.keys(vm.options[i].max_group_arrival_by_date)
                district_id = vm.options[i].district_id
                for(var j=0; j<arrival_dates.length; j++) {
                    arrival = arrival_dates[j]
                    total_adults = vm.options[i].max_group_arrival_by_date[arrival].total_adults
                    total_children = vm.options[i].max_group_arrival_by_date[arrival].total_children
                    vm.max_group_arrival.push({arrival: arrival, district: [{district_id: district_id, total_adults: total_adults, total_children: total_children}]})
                }
            }
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
    },

    updated() {
        let vm = this;
    },
}
</script>

<style scoped lang="css">
    .container {
      padding: 30px;
      width: 100%;
    }

    .editable-table
        input[type=number]{
            width: 60px;
        }

    .editable-table
        input[type=total]{
            width: 100px;
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

