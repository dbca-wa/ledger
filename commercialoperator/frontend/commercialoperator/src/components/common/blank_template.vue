<template lang="html">
    <div>
    </div>
</template>

<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

import Treeselect from '@riophae/vue-treeselect'

export default {
    name:'TreeSelect',
    components:{
        Treeselect
    },
    props:{
        proposal:{
            type: Object,
            required:true
        },
        boo_type:{
            type: Boolean,
            default: false
        },
        num_type:{
            type: Number,
            default: 100
        },
        str_type:{
            type: String,
            default: 'abc'
        },
    },

    data() {
      return {
        items: [],
      }
    },

    computed: {
    },

    methods:{
        fetchDataExample: function(){
            let vm = this;

            //vm.$http.get(api_endpoints.park_treeview).then((response) => { 
            //console.log('treeview_url: ' + api_endpoints.park_treeview + '?format=json&proposal=' + vm.proposal.id)
            vm.$http.get(api_endpoints.park_treeview + '?format=json&proposal=' + vm.proposal.id)
            .then((response) => {
                vm.options = response.body['options'];
                vm.selected_items = response.body['selected_items'];
            },(error) => {
                console.log(error);
            })
        },
        test:function(event, node){
            alert("event: " + event + " park_id: " + node.raw.id + ", park_name: " + node.raw.label );
            console.log("event: " + event + " park_id: " + node.raw.id + ", park_name: " + node.raw.label );
        },
        mousedown_event_stop_propagation:function(){
            $('.option-label-container').on('mousedown', function(e) {
                e.stopPropagation();
                return false;
            });
        },
    },

    beforeUpdate: function() {
    },

    updated: function() {
    },

    beforeMount: function() {
    },

    mounted:function () {
        let vm = this;
        //vm.fetchParkTreeview()
    }
}
</script>

<style lang="css" scoped>
</style>

