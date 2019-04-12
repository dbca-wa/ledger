<template lang="html">
    <div class="form-group">
        <label :id="id" for="label" class="expander-label">{{ label }}</label>
        <template v-if="help_text">
            <HelpText :help_text="help_text" />
        </template>

        <template v-if="help_text_url">
            <HelpTextUrl :help_text_url="help_text_url" />
        </template>

        <div v-if="canViewComments">
            <div v-if="!showingComment">
                <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
            </div>
            <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
        </div>

        <!--<textarea readonly="readonly" class="form-control form-value" :name="name">{{ value }}</textarea>-->

        <div class="expander-table" v-for="(table, tableIdx) in expanderTables">
            <div class="row header-row">
                <div :class="`col-xs-${Math.floor(12 / component.header.length)}`"
                    v-for="(header, index) in component.header"
                    v-bind:key="`expander_header_${component.name}_${index}`">
                        <span v-if="!index" :class="`expand-icon ${isExpanded(table) ? 'collapse' : ''}`"
                            v-on:click="toggleTableVisibility(table)"></span>
                        <span class="header-contents">
                            <renderer-block
                            :component="header"
                            :json_data="value"
                            :instance="table"
                            v-bind:key="`expander_header_contents_${component.name}_${index}`"
                            />
                        </span>
                        <a v-if="tableIdx && index == component.header.length-1" class="delete-icon fa fa-trash-o" title="Delete row"
                            @click.prevent="removeTable(table)"></a>
                </div>
            </div>
            <div :class="{'hidden': !isExpanded(table)}">
                <div class="row expander-row" v-for="(subcomponent, index) in component.expander" v-bind:key="`expander_row_${component.name}_${index}`">
                    <div class="col-xs-12">
                        <renderer-block
                            :component="subcomponent"
                            :json_data="value"
                            :instance="table"
                            v-bind:key="`expander_contents_${component.name}_${index}`"
                            />
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <input type="button" value="Add New" class="btn btn-primary add-new-button"
                @click.prevent="addNewTable">
        </div>
    </div>
</template>

<script>
import Comment from './comment.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
import { mapGetters, mapActions } from 'vuex';
import '@/scss/forms/expander_table.scss';

const ExpanderTable = {
    props:{
        name: String,
        label: String,
        id: String,
        isRequired: String,
        comment_value: String,
        help_text: String,
        help_text_url: String,
        component: {
            type: Object | null,
            required: true
        },
        json_data: {
            type: Object | null,
            required: true
        },
        readonly:Boolean,
    },
    components: {
        Comment,
        HelpText,
        HelpTextUrl
    },
    data(){
        return {
            expanded: {},
        };
    },
    methods: {
        ...mapActions([
            'removeFormInstance',
            'setFormValue'
        ]),
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        isExpanded: function(tableId) {
            return this.expanded[tableId];
        },
        toggleTableVisibility: function(tableId) {
            if(this.expanded[tableId]) {
                this.$delete(this.expanded, tableId);
            }
            else {
                this.$set(this.expanded, tableId, true);
            }
        },
        removeTable: function(tableId) {
            if(this.expanded[tableId]) {
                this.$delete(this.expanded, tableId);
            }
            this.removeFormInstance(
                this.getInstanceName(tableId)
            );
            this.updateVisibleTables(
                this.existingTables.filter(table => table != tableId)
            );
        },
        addNewTable: function(params={}) {
            let { tableId } = params;
            if(!tableId) {
                tableId = this.getTableId(this.lastTableId+1);
            }
            this.existingTables.push(tableId);
        },
        updateVisibleTables: function(tableList) {
            this.setFormValue({
                key: this.component.name,
                value: {
                    "value": tableList,
                }
            });
        },
        getTableId: function(tableIdx) {
            return `${this.id}_table_${tableIdx}`;
        },
        getInstanceName: function(tableId) {
            return `__instance-${tableId}`
        },
    },
    computed:{
        ...mapGetters([
            'canViewComments',
            'getFormValue',
        ]),
        lastTableId: function() {
            if(!this.existingTables.length) {
                return 0;
            }
            let lastId = 0;
            this.existingTables.map(tableId => tableId[tableId.length-1] > lastId && (lastId = tableId[tableId.length-1]));
            return parseInt(lastId, 10);
        },
        existingTables: function() {
            return this.getFormValue(this.component.name) || [];
        },
        expanderTables: function() {
            if(!this.existingTables.length) {
                this.addNewTable();
            }
            return this.existingTables;
        },
        value: function() {
            return this.json_data;
        },
    },
    mounted:function () {
    }
}

export default ExpanderTable;
</script>
