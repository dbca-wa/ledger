<template lang="html">
  <div>
      <div>
        <label class="control-label">Select Parks (New)</label>
        <treeselect
          v-model="value"
          :max-height="200"
          :multiple="true"
          :options="options"
          :open-on-click="true"
          :value-consists-of="valueConsistsOf"
          :always-open="true"
          :clearable="true"
          :flat="false"
          :default-expand-level="0"
        >

<!--
        <template v-slot="{ item }">
          <a href="#" v-if="item.to">{{item.label}} {{item.to}}</a>
        </template>

        <label slot="option-label" slot-scope="{ node, shouldShowCount, count, labelClassName, countClassName }" :class="labelClassName">
            {{ node.isBranch ? 'Branch' : 'Leaf' }}: {{ node.label }}
            <span v-if="shouldShowCount" :class="countClassName">({{ count }})</span>
        </label>

        <div slot="value-label" slot-scope="{ node }">{{ node.raw.customLabel }}</div>
-->
        <div slot="option-label" slot-scope="{ node }">
            <div class="form-group">
                <label class="col-sm-8 control-label">{{ node.raw.label }}</label>
                <a class="col-sm-4 container-url" href="#https://www.google.com" target="_blank" v-if="node.raw.to">{{node.raw.to}}</a>
            </div>
        </div>


<!--
        <template slot="value-label" slot-scope="{ node }">
          <a href="#" v-if="node.raw.to">{{node.raw.label}} {{node.raw.to}}</a>
        </template>
-->

        </treeselect>
      </div>

      <div>
        <pre>{{ value }}</pre>
      </div>
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
import '@riophae/vue-treeselect/dist/vue-treeselect.css'

export default {
    name:'Applications',
    components:{
        Treeselect
    },
    props:{
        proposal:{
            type: Object,
            required:true
        }
    },

    data() {
      return {
        value: [3,5],
        valueConsistsOf: 'LEAF_PRIORITY',
        options: [ {
          id: 1,
          label: 'a',
          children: [ {
            id: 2,
            label: 'aa',
          }, {
            id: 3,
            label: 'ab',
            to: 'ABCDEF',
          } ],
        }, {
          id: 4,
          label: 'b',
        }, {
          id: 5,
          label: 'c',
        } ],
      }
    },

    computed: {
    },

    methods:{
    },

    mounted:function () {

/*
      $('.container-url2').on('click', 'a', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
      });

    $('.container-url').click(
      function(e) {
          e.stopPropagation();
      }
    );

      $('.container-url').on('click', function(event) {
        event.stopPropagation();
      });

      $(".vue-treeselect__label-container div a").on('click', function (e) { e.stopPropagation(); })

    }
*/

      $('.vue-treeselect__label-container > .container-url').click(
          function(e) {
            e.stopPropagation();
          }
      );
    }
}
</script>

<style lang="css" scoped>
.container-url {
    pointer-events: none;
}
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
