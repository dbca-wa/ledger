<template lang="html">
    <div>
        <div id="mydiv"></div>
        <pre>{{ selected_items }}</pre>
        <treeselect
            v-model="selected_items"
            :options="options"
            :open-on-click="true"
            :multiple="multiple"
            :max-height="max_height"
            :value-consists-of="value_consists_of"
            :clearable="clearable"
            :flat="flat"
            open-on-focus="true"
            open-direction="bottom"
            limit="10"
            >

            <input type="hidden" @click="edit_activities_test($event,node)">

            <template slot="option-label" slot-scope="{ node }">
                <label class="col-sm-8 control-label">{{ node.raw.label }}</label>
                <div v-if="node.raw.can_edit" class="option-label-container">
                    <a class="col-sm-4 control-label pull-right" @click.stop="edit_activities_test(node)">Edit access and activities  <i class="fa fa-edit"></i></a>
                </div>

                <!--
                <TreeSelectNode :node="node"></TreeSelectiNode>
                <a class="col-sm-4 control-label pull-right" @click="edit_activities(p.id, p.name)" target="_blank">Edit access and activities  <i class="fa fa-edit"></i></a>
                :always-open="always_open"
                :default-expand-level="default_expand_level"
                -->
            </template>
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
import setupResizeAndScrollEventListeners from '@riophae/vue-treeselect'
//import TreeSelectNode from './treeview_node_edit'

export default {
    name:'TreeSelect',
    components:{
        Treeselect,
        //TreeSelectNode
    },
    props:{
        proposal:{
            type: Object,
            required:true
        },
        selected_items:{
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
            default: true
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
    },

    data() {
      return {
        items: ['Item1', 'Item2', 'Item3', 'Item4', 'Item5', 'Item6', 'Item7', 'Item8'],
        template2: '<a class="col-sm-4 control-label pull-right">Edit access  {{node.raw.label}}</a>',
        _selected_items: [],
        _options: [],

        /*
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
    render(createElement) {
        return compiledTemplate.render.call(this, createElement);
    },

    computed: {
    },

    methods:{
        fetchParkTreeview: function(){
            let vm = this;

            //vm.$http.get(api_endpoints.park_treeview).then((response) => { 
            //vm.$http.get('/api/park_treeview/?format=json&proposal=323').then((response) => { 
            //vm.$http.get(helpers.add_endpoint_json(api_endpoints.park_treeview,('/?format=json&proposal='+vm.proposal.id)))
            console.log('treeview_url: ' + api_endpoints.park_treeview + '?format=json&proposal=' + vm.proposal.id)
            vm.$http.get(api_endpoints.park_treeview + '?format=json&proposal=' + vm.proposal.id)
            .then((response) => {
                vm.options = response.body['options'];
                vm.selected_items = response.body['selected_items'];
            },(error) => {
                console.log(error);
            })
        },
        edit_activities: function(p_id, p_name){
            let vm=this;
            for (var j=0; j<vm.selected_parks_activities.length; j++){
              if(vm.selected_parks_activities[j].park==p_id){ 
                this.$refs.edit_activities.park_activities= vm.selected_parks_activities[j].activities;
                this.$refs.edit_activities.park_access= vm.selected_parks_activities[j].access
              }
            }
            this.$refs.edit_activities.park_id=p_id;
            this.$refs.edit_activities.park_name=p_name;
            this.$refs.edit_activities.fetchAllowedActivities(p_id)
            this.$refs.edit_activities.fetchAllowedAccessTypes(p_id)
            this. $refs.edit_activities.isModalOpen = true;
        },
        //edit_activities_test:function(event, node){
        edit_activities_test:function(node){
            //alert("event: " + event + " park_id: " + node.raw.id + ", park_name: " + node.raw.label );
            alert(" park_id: " + node.raw.id + ", park_name: " + node.raw.label );
        },
        mousedown_event_stop_propagation:function(){
            $('.option-label-container').on('mousedown', function(e) {
                e.stopPropagation();
                return false;
            });
        },
        mousedown_event_stop_propagation2:function(){
            $.each($._data($('.option-label-container')[0], "events"), function(i, event) {
                    $.each(event, function(j, h) {
                        alert(j + ' - ' + h);
                    });
            });
        }
    },

    beforeUpdate: function() {
        let vm=this;
        //vm.mousedown_event_stop_propagation()

//        document.querySelector(".vue-treeselect__label-container > svg").addEventListener("click", function(e) {e.stopPropagation(); e.preventDefault();});
//            Ae.preventDefault();re.stopPropagation();
//            e.preventDefault();
//        });

        /*
        $('.option-label-container').on('mousedown', function(e) {
            e.stopPropagation();
            return false;
        });
        */
    },

    updated: function() {
        let vm=this;
        vm.mousedown_event_stop_propagation()

        /*
        $('.option-label-container').on('mousedown', function(e) {
            e.stopPropagation();
            return false;
        });
        */
    },

    beforeMount: function() {
        let vm=this;
        vm.mousedown_event_stop_propagation()

        /*
        $('.option-label-container').on('mousedown', function(e) {
            e.stopPropagation();
            return false;
        });
        */
    },

    mounted:function () {
        let vm = this;
        vm.fetchParkTreeview()
        setupResizeAndScrollEventListeners()
    }
}
</script>

<style lang="css" scoped>

.vue-treeselect__checkbox-container {
    width: 50px;
}

/*
.option-label-container {
    pointer-events: none;
}

.vue-treeselect__menu {
  position: absolute;
  max-height: none!important;
}
.borderDecoration {
  position: absolute;
  max-height: none!important;
}
*/
</style>

/*
            items: [
            {
                id: 1,
                name: 'Applications :',
                children: [
                  { id: 2, name: 'Calendar : app'  },
                  { id: 3, name: 'Chrome : app'  },
                  { id: 4, name: 'Webstorm : app'  }
                ]
            },
            {
                id: 5,
                name: 'Documents :',
                children: [
                {
                    id: 6,
                    name: 'vuetify :',
                    children: [
                    {
                        id: 7,
                        name: 'src :',
                        children: [
                          { id: 8, name: 'index : ts', to:'Edit'  },
                          { id: 9, name: 'bootstrap : ts'  }
                        ]
                    }
                    ]
                }
                ]
            }
            ],

*/
