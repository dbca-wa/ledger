<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>

            <template v-if="renderer.canViewComments()">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>

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
                  <tr v-for="row in table.tbody">
                    <td v-for="(value, index) in row">
                        <!-- <input type="text" v-model="row[index]" /> -->
                        <input :readonly="readonly" class="tbl_input" :type="col_types[index]" min="0" v-model="row[index]" :required="isRequired" :onclick="isClickable"/>
                    </td>
                    <td v-if="!readonly">
                        <a class="fa fa-trash-o" v-on:click="deleteRow(row)" title="Delete row" style="cursor: pointer; color:red;"></a>
                    </td>
                  </tr>

                  <tr>
                    <td v-if="!readonly">
                      <button class="btn btn-primary" type="button" v-on:click="addRow()" title="Add Row">+</button>
                    </td>
                  </tr>
                </tbody>

              </table>

              <!-- for debugging -->
              <!--
              <pre class="output">
                {{ value }}
              </pre>
              <pre class="output">
                {{ headers }}
              </pre>
              -->
            </div>

        </div>
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:{
        headers: String,  // Input received as String, later converted to JSON within data() below
        name: String,
        label: String,
        id: String,
        isRequired: String,
        comment_value: String,
        help_text: String,
        help_text_url: String,
        renderer: {
            type: Object,
            required: true
        },
        value:{
            default:function () {
                return null;
            }
        },
        readonly:Boolean,

        /*
        tableJSON:{
            default:function () {
                return '';
            }
        },

        table:{
            default:function () {
                return {
                    thead: [],
                    tbody: [],
                }
            }
        }
        */

    },

    components: {Comment, HelpText, HelpTextUrl},

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
        var col_headers = Object.keys(headers);
        vm.col_types = Object.values(headers);

        // setup initial empty row for display
        var init_row = [];
        for(var i = 0, length = col_headers.length; i < length; i++) { init_row.push('')  }

        if (value == null) {
            vm.table = {
                    //thead: ['Heading 1'],
                    thead: col_headers,
                    tbody: [
                        //['No header specified']
                        init_row
                    ]
            }
        } else {
            vm.table = {
                    thead: value['thead'],
                    tbody: value['tbody']
            }
        }

        let data = {
            showingComment: false,
        }
        if(vm.readonly) {
            data.isClickable = "return false;";
        } else {
            data.isClickable = "return true;";
        }

        return data;

    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
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
            //newRow.push('R:' + (vm.table.tbody.length + 1) + ' V:' + (i + 1))
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
        }

    },

    computed:{
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

    }
}
</script>

<style scoped lang="css">
    .container {
      padding: 30px;
      width: 100%;
    }

    .editable-table[type="text"] {
        background: none;
        border: none;
        display: block;
        width: 100%;
    }

    .output {
      white-space: normal;
    }

    input[id="header"] {
        outline-style: none;
    }
</style>

