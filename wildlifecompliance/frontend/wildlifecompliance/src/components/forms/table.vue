<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <!--
            <template v-if="assessorMode && !assessor_readonly && wc_version != 1.0">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <textarea :readonly="readonly" class="form-control" rows="5" :name="name" :required="isRequired">{{ value }}</textarea><br/>
            -->

            <div id="content-editable-table">
              <table class="table table-striped editable-table">
                <thead v-if="table.thead.length">
                  <tr>
                    <th v-for="(heading, index) in table.thead">
                      {{ table.thead[index] }}
                    </th>

                    <!--
                    <th>
                      <button class="btn btn-primary" type="button" v-on:click="addColumn()" title="Add Column">+</button>
                    </th>
                    -->
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="row in table.tbody">
                    <td v-for="(value, index) in row">
                      <input type="text" v-model="row[index]" />
                    </td>
                    <td>
                        <button class="btn btn-md" type="button"> <a class="ibtnDel fa fa-trash-o" title="Delete row" style="cursor: pointer; color:red;"></a> </button>
                    </td>
                    <td>&nbsp;</td>
                  </tr>

                  <tr>
                    <td  v-bind:colspan="table.thead.length + 1">
                      <button class="btn btn-primary" type="button" v-on:click="addRow()" title="Add Row">+</button>
                    </td>
                  </tr>
                </tbody>

              </table>

              <pre class="output">
                {{tableJSON}}
              </pre>
            </div>

            <pre class="output">
                {{rows}}
            </pre>

        </div>
        <!--<Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> -->
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    //props:["name","value", "id", "isRequired", "help_text","help_text_assessor","assessorMode","label","readonly","comment_value","assessor_readonly", "help_text_url", "help_text_assessor_url"],
    props:{
        name:String,
        label:String,
        id:String,
        isRequired:String,
        comment_value: String,
        assessor_readonly: Boolean,
        help_text:String,
        help_text_assessor:String,
        help_text_url:String,
        help_text_assessor_url:String,
        assessorMode:{
            default:function(){
                return false;
            }
        },
        value:{
            default:function () {
                return null;
            }
        },
        readonly:Boolean,
        rows: [],


    },

    components: {Comment, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        return {
            showingComment: false,

            tableJSON: '',
            table: {
              thead: [
                'Heading 1',
                'Heading 2',
                'Heading 3',
                'Heading 4'
              ],
              tbody: [
                ['R:1 V:1', 'R:1 V:2', 'R:1 V:3', 'R:1 V:4'],
              ],
              tfoot: [
              ],
            }

        }

    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },

        updateTableJSON: function() {
          this.tableJSON = JSON.stringify(this.table);
        },

        addColumn: function() {
          this.table.thead.push('Heading ' + (this.table.thead.length + 1));

          for(var i = 0, length = this.table.tbody.length; i < length; i++) {
            this.table.tbody[i].push('R:' + (i + 1) + ' V:' + this.table.thead.length);
          }

          this.table.tfoot.push('Footer ' + this.table.thead.length);

          this.updateTableJSON();
        },

        addRow: function() {
          var newRow = [];

          for(var i = 0, length = this.table.thead.length; i < length; i++) {
            newRow.push('R:' + (this.table.tbody.length + 1) + ' V:' + (i + 1))
          }

          this.table.tbody.push(newRow);

          this.updateTableJSON();
        }

    },

    computed:{
        wc_version: function (){
            return this.$root.wc_version;
        },


    },


    mounted:function () {
        let vm = this;


        vm.updateTableJSON();

        $('#content-editable-table').on('change', '[type="text"]', function() {
          vm.updateTableJSON();
        });

        $("#content-editable-table").on("click", ".ibtnDel", function (event) {
            $(this).closest("tr").remove();
        });
    },
}
</script>

<style scoped lang="css">
    .container {
      padding: 30px;
      width: 100%;
    }

    .editable-table {

      [type="text"] {
        background: none;
        border: none;
        display: block;
        width: 100%;
      }
    }

    .output {
      white-space: normal;
    }

    input[id="header"] {
        outline-style: none;
    }
</style>
:w

