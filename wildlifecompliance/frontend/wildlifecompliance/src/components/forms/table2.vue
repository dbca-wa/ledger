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


            <!--
            <template>
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <textarea :readonly="readonly" class="form-control" rows="5" :name="name" :required="isRequired">{{ value }}</textarea><br/>
            -->

            <table id="dynamic-table" class=" table order-list">
                <thead>
                    <tr>
                        <td>Name</td>
                        <td>Gmail</td>
                        <td>Phone</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="col-sm-4">
                            <input type="text" name="name" class="form-control" />
                        </td>
                        <td class="col-sm-4">
                            <input type="mail" name="mail"  class="form-control"/>
                        </td>
                        <td class="col-sm-3">
                            <input type="text" name="phone"  class="form-control"/>
                        </td>
                        <td class="col-sm-2"><a class="deleteRow"></a>

                        </td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="5" style="text-align: left;">
                            <input type="button" class="btn btn-lg btn-block " id="addrow" value="Add Row" />
                        </td>
                    </tr>
                    <tr>
                    </tr>
                </tfoot>
            </table>

            {{rows}}
            <pre class="output">
                {{rows}}
            </pre>

        </div>
        <!--<Comment :question="label" :name="name+'-comment-field'" v-show="showingComment :value="comment_value"/> -->
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:{
        name:String,
        label:String,
        id:String,
        isRequired:String,
        comment_value: String,
        help_text:String,
        help_text_url:String,
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
            showingComment: false
        }
    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },

        // https://bootsnipp.com/snippets/402bQ
        init_table() {
            let vm = this;
            var counter = 0;

            $("#addrow").on("click", function () {
                var newRow = $("<tr>");
                var cols = "";

                cols += '<td><input type="text" class="form-control" name="name' + counter + '"/></td>';
                cols += '<td><input type="text" class="form-control" name="mail' + counter + '"/></td>';
                cols += '<td><input type="text" class="form-control" name="phone' + counter + '"/></td>';

                cols += '<td><input type="button" class="ibtnDel btn btn-md btn-danger "  value="Delete"></td>';
                newRow.append(cols);
                $("table.order-list").append(newRow);
                counter++;
 
                vm.rows = vm.tableToJSON()      
                
            });

            $("table.order-list").on("click", ".ibtnDel", function (event) {
                $(this).closest("tr").remove();       
                counter -= 1
            });
        },

        calculateRow(row) {
            var price = +row.find('input[name^="price"]').val();
        },

        calculateGrandTotal() {
            var grandTotal = 0;
            $("table.order-list").find('input[name^="price"]').each(function () {
                grandTotal += +$(this).val();
            });
            $("#grandtotal").text(grandTotal.toFixed(2));
        },

        tableToJSON() {
            //var $table = $("#dynamic-table"),
            var $table = $("table"),
                rows = [],
                header = [];

            $table.find("thead td").each(function () {
                header.push($(this).html());
            });

            $table.find("tbody tr").each(function () {
                var row = {};

                $(this).find("td input").each(function (i) {
                    var key = header[i],
                        //value = $(this).html();
                        value = $(this).text();

                    row[key] = value;
                });

                rows.push(row);
            });

            //console.log(JSON.stringify(rows))
            return rows
        }

    },
    computed:{
    },


    mounted:function () {
        let vm = this;
        vm.init_table();

        vm.rows = vm.tableToJSON();
        //console.log(table)

        console.log(JSON.stringify(vm.rows))
    },
}
</script>

<style scoped lang="css">
    input {
        box-shadow:none;
    }
</style>
