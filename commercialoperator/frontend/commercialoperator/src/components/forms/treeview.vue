<template lang="html">
    <div>
        <!-- <pre>TreeSelect: {{ value }}</pre> -->
        <treeselect
            v-model="value"
            :options="options"
            :open-on-click="true"
            :multiple="multiple"
            :max-height="max_height"
            :value-consists-of="value_consists_of"
            :clearable="clearable"
            :flat="flat"
            :default-expand-level="default_expand_level"
            :normalizer="normalizer"
            :open-direction="open_direction"
            :disabled="disabled"
            open-on-focus="true"
            limit="20"
            >

            <template slot="option-label" slot-scope="{ node }">
                <label class="col-sm-8 control-label">{{ node.raw.name }}</label>
                <div v-if="node.raw.can_edit" class="option-label-container">
                    <span v-if="is_checked(node)">
                        <a class="col-sm-4 control-label pull-right" @click.stop="edit_activities(node)">{{ edit_display_text(node) }}  <i class="fa fa-edit"></i></a>
                    </span>
                    <span v-else>
                        <p class="col-sm-4 control-label pull-right" style="color: grey;">{{ edit_display_text(node) }}  <i class="fa fa-edit"></p>
                    </span>
                </div>
            </template>

            <div slot="value-label" slot-scope="{ node }">
                <div v-if="allow_edit">
                    <a @click.stop="edit_activities(node)" :disabled="!is_checked(node)" :title="edit_display_text(node)"> {{node.label}} </a>
                </div>
                <div v-else>
                    <a> {{node.label}} </a>
                </div>
            </div>

        </treeselect>
    </div>
</template>

<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

/* hack because I have modified two methods in vue-treeselect.js --> renderLabelContainer, renderOptionContainer. TODO look to override instead
   sudo npm install --save @riophae/vue-treeselect
   import Treeselect from '@riophae/vue-treeselect'
*/
import Treeselect from '@/third-party/vue-treeselect/dict/vue-treeselect.js'
import '@/third-party/vue-treeselect/dict/vue-treeselect.css'

import Profile from '@/components/user/profile.vue'
//import setupResizeAndScrollEventListeners from '@riophae/vue-treeselect'

export default {
    name:'TreeSelect',
    components:{
        Treeselect,
    },
    props:{
        proposal:{
            type: Object,
            required:true
        },
        value:{
            type: Object,
            required:false
        },
        options:{
            type: Object,
            required:false
        },
        flat:{
            type: Boolean,
            default: false
        },
        always_open:{
            type: Boolean,
            default: true
        },
        clearable:{
            type: Boolean,
            default: false
        },
        multiple:{
            type: Boolean,
            default: true
        },
        max_height:{
            type: Number,
            default: 350
        },
        default_expand_level:{
            type: Number,
            default: 0
        },
        value_consists_of:{
            type: String,
            default: 'LEAF_PRIORITY', // last leaf nodes get pushed to selected_items array
        },
        open_direction:{
            type: String,
            default: 'bottom'
        },
        allow_edit:{
            type: Boolean,
            default: false
        },
        disabled:{
            type: Boolean,
            default: false
        },

    },

    data() {
      return {
        //_options: [],
        normalizer(node) {
            return {
                id: node.last_leaf ? node.id : node.name,
                //id: node.last_leaf ? node.node_id : node.name,
                label: node.hasOwnProperty('label') ? node.label : node.name,
                children: node.children,
                isDisabled: node.is_disabled,
                }
            }
        }
    },
    watch:{
        value: function(){
            /* allows two-way update of array value ( 'selected_access' )
               Requires parent Prop: ' :value.sync="selected_access" ', eg. 
               <TreeSelect ref="selected_access" :proposal="proposal" :value.sync="selected_access" :options="land_access_options" :default_expand_level="1"></TreeSelect>
            */

            this.$emit("update:value", this.value)
        },
    },

    computed: {
    },

    methods:{
        get_node_id:function(node){
            //id: node.last_leaf ? node.id : (node.hasOwnProperty('node_id') : node.node_id ? node.name), // this is a nested if statement
            if (node.last_leaf) {
                return node.id
            } else if (node.hasOwnProperty('node_id')) {
                return node.node_id
            } else {
                return node.name
            }
        },
        edit_activities_test:function(node){
            //alert("event: " + event + " park_id: " + node.raw.id + ", park_name: " + node.raw.label );
            alert(" park_id: " + node.raw.id + ", park_name: " + node.raw.label );
        },
        edit_display_text:function(node){
            if (node.raw.hasOwnProperty('sections')) {
                return 'Edit sections and activities';
            } else {
                return 'Edit access and activities';
            }
        },
        edit_activities:function(node){
            if (node.raw.hasOwnProperty('sections')) {
                this.$parent.edit_sections(node)
            } else if (node.raw.hasOwnProperty('allowed_zone_activities')) {
                this.$parent.edit_activities(node)
            } else {
                this.$parent.edit_activities(node)
            }
        },
        is_checked:function(node){
            return this.value.includes(node.id);
        },
        mousedown_event_stop_propagation:function(){
            $('.option-label-container').on('mousedown', function(e) {
                e.stopPropagation();
                return false;
            });
        },
    },

    updated: function() {
        this.mousedown_event_stop_propagation()
    },

    mounted:function () {
    }
}
</script>

<style lang="css" scoped>
    /*
    .vue-treeselect__checkbox-container {
        width: 50px;
    }
    */
</style>

/*
    data() {
      return {
        normalizer(node) {
            return {
                id: node.name,
                label: node.name,
                children: node.children,
            }
        },

        /*
        _selected_items: [],
        _options: [],

        selected_items: [3,5],
        options: [ {
          id: 1,
          label: 'a',
          children: [ {
            id: 2,
            label: 'aa',
            can_edit: false,
          }, {
            id: 3,
            label: 'ab',
            can_edit: true,
          } ],
        }, {
          id: 4,
          label: 'b',
          can_edit: false,
        }, {
          id: 5,
          label: 'c',
          can_edit: false,
        } ],
        */
      }
    },
*/

