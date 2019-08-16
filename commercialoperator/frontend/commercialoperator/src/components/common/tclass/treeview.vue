<template lang="html">
  <div>
      <a class="test-url col-sm-4" @click="btn_test($event)">Test URL</a>
      <input type="button" @click="btn_test($event)" class="btn btn-primary" value="button test"/>
      <div>
        <label class="control-label">select parks (new)</label>
        <treeselect
          v-model="value"
          :max-height="200"
          :multiple="true"
          :options="options"
          :open-on-click="false"
          :value-consists-of="valueconsistsof"
          :always-open="true"
          :clearable="true"
          :flat="false"
          :appendToBody="false"
          :default-expand-level="0"
        >

<!--
        <template v-slot="{ item }">
          <a href="#" v-if="item.to">{{item.label}} {{item.to}}</a>
        </template>

        <label slot="option-label" slot-scope="{ node, shouldshowcount, count, labelclassname, countclassname }" :class="labelclassname">
            {{ node.isbranch ? 'branch' : 'leaf' }}: {{ node.label }}
            <span v-if="shouldshowcount" :class="countclassname">({{ count }})</span>
        </label>

        <div slot="value-label" slot-scope="{ node }">{{ node.raw.customlabel }}</div>

        <template slot="value-label" slot-scope="{ node }">
          <a href="#" v-if="node.raw.to">{{node.raw.label}} {{node.raw.to}}</a>
        </template>
-->
        <template slot="option-label" slot-scope="{ node }">
                <label class="col-sm-10 control-label">{{ node.raw.label }}</label>
                <!--
                <a class="container-url col-sm-2" href="#https://www.google.com" target="_blank" v-if="node.raw.to">{{node.raw.to}}</a>
                <a class="container-url col-sm-2" @click="btn_test()">edit</a>
                <div class="container-url col-sm-2"><input type="button" @click.stop="btn_test()" class="btn btn-primary" value="button test"/></div>
                -->
                <span v-if="node.raw.to">{{node.raw.to}}>
                    <a id="id_edit_0" class="col-sm-2" v-on:click="btn_test($event)">edit0</a>
                    <a id="id_edit_1" class="col-sm-2" @click.stop="btn_test($event)">edit1</a>
                    <a id="id_edit_2" class="col-sm-2" @click.prevent="btn_test($event)">Edit2</a>
                    <a id="id_edit_3" class="col-sm-2" @click.stop.prevent="btn_test($event)">Edit3</a>
                    <a id="id_edit_4" class="col-sm-2" @click.prevent.self="btn_test($event)">Edit4</a>
                    <a id="id_edit_5" class="col-sm-2" @click.self="btn_test($event)">Edit5</a>
                    <a id="id_edit_6" class="col-sm-2" @click.self.native="btn_test($event)">Edit6</a>
                    <a id="id_edit_7" class="col-sm-2" @click.self.stop="btn_test($event)">Edit7</a>
                    <a id="id_edit_8" class="col-sm-2" @click.self.prevent="btn_test($event)">Edit8</a>
                    <a id="id_edit_9" class="col-sm-2" @click.capture.stop.prevent="btn_test($event)">Edit9</a>
                    <a id="id_edit_10" class="col-sm-2" @click.self.stop.prevent="btn_test($event)">Edit10</a>
                    <i id="id_edit_11" class="fa fa-edit" title="Edit Activities 1" @click="btn_test($event)"></i>
                    <i id="id_edit_12" class="fa fa-edit" title="Edit Activities 2" @click.native.stop.prevent="btn_test($event)"></i>
                    <i id="id_edit_13" class="fa fa-edit" title="Edit Activities 3" @click.native="btn_test($event)"></i>
                </span>
        </template>


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
        btn_test:function(e){
            //e.preventDefault()
            //e.preventPropagation()
            this.$emit('click', e);
            alert("TEST BTN clicked.");
        }
    },

    beforeUpdate: function() {
        var elem=$('#id_edit_0');
        var event = document.createEvent('HTMLEvents');
        event.initEvent('click', true, true);
        elem.dispatchEvent(event);

        event.stopPropagation();

        /*
        $("#id_edit_0").click(
            function (e) { 
                e.stopPropagation(); 
            }
        );
        */
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

/*
      $('.vue-treeselect__label-container .container-url input').click(
          function(e) {
            e.stopPropagation();
            alert("1")
          }
      );

      $(".container-url input").on('click', function (e) {
          e.stopPropagation(); 
          alert("2")
      })

      $(".test-url a").on('click', function (e) {
          alert("TEST URL clicked."); 
      })
      //$("#id_edit_0").on('click', function (e) { e.stopPropagation(); })
*/
      $("#id_edit_0").click(function (e) { e.stopPropagation(); });
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
