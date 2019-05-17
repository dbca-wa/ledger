<template lang="html">
    <div class="form-group">
        <label :id="id" for="label" class="expander-label">{{ label }}</label>
        <template v-if="help_text">
            <HelpText :help_text="help_text" />
        </template>

        <template v-if="help_text_url">
            <HelpTextUrl :help_text_url="help_text_url" />
        </template>

        <CommentBlock 
            :label="label"
            :name="name"
            :field_data="field_data"
            />

        <div class="row header-titles-row">
            <div :class="`col-xs-${Math.floor(12 / component.header.length)}`"
                v-for="(header, index) in component.header"
                v-bind:key="`expander_header_${component.name}_${index}`">
                    {{ header.label }}
            </div>
        </div>
        <div class="expander-table" v-for="(table, tableIdx) in expanderTables">
            <div class="row header-row">
                <div :class="`col-xs-${Math.floor(12 / component.header.length)}`"
                    v-for="(header, index) in component.header"
                    v-bind:key="`expander_header_${component.name}_${index}`">
                        <span v-if="!index" :class="`expand-icon ${isExpanded(table) ? 'collapse' : ''}`"
                            v-on:click="toggleTableVisibility(table)"></span>
                        <span class="header-contents">
                            <compliance-renderer-block
                            :component="removeLabel(header)"
                            :json_data="value"
                            :instance="table"
                            v-bind:key="`expander_header_contents_${component.name}_${index}`"
                            />
                        </span>
                        <a v-if="tableIdx && index == component.header.length-1 && !readonly" class="delete-icon fa fa-trash-o" title="Delete row"
                            @click.prevent="removeTable(table)"></a>
                </div>
            </div>
            <div :class="{'hidden': !isExpanded(table)}">
                <div class="row expander-row" v-for="(subcomponent, index) in component.expander" v-bind:key="`expander_row_${component.name}_${index}`">
                    <div class="col-xs-12">
                        <compliance-renderer-block
                            :component="subcomponent"
                            :json_data="value"
                            :instance="table"
                            v-bind:key="`expander_contents_${component.name}_${index}`"
                            />
                    </div>
                </div>
            </div>
        </div>
        <div class="row" v-if="!readonly">
            <input type="button" value="Add New" class="btn btn-primary add-new-button"
                @click.prevent="addNewTable">
        </div>
    </div>
</template>

<script>
import CommentBlock from './comment_block.vue';
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
        help_text: String,
        help_text_url: String,
        component: {
            type: Object | null,
            required: true
        },
        field_data: {
            type: Object | null,
            required: true
        },
        readonly:Boolean,
    },
    components: {
        CommentBlock,
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
            'setFormValue',
            'refreshApplicationFees',
        ]),
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
            this.refreshApplicationFees();
        },
        addNewTable: function(params={}) {
            let { tableId } = params;
            if(!tableId) {
                tableId = this.getTableId(this.lastTableId+1);
            }
            this.existingTables.push(tableId);
            this.updateVisibleTables(
                this.existingTables
            );
            this.refreshApplicationFees();
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
        removeLabel: function(header) {
            let newHeader = {...header};
            delete newHeader['label'];
            return newHeader;
        },
    },
    computed:{
        ...mapGetters([
            'canViewComments',
            'canViewDeficiencies',
            'canEditDeficiencies',
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
            return this.field_data;
        },
    }
}

export default ExpanderTable;
</script>
