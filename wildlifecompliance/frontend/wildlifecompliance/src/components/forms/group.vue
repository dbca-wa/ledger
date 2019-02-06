<template lang="html">
<!--
    <div class="top-buffer bottom-buffer">
        <div v-if="isRepeatable" v-for="n in repeat" class="panel panel-default">
            <div class="repeat-group panel-body" :data-que="n">
                <p>N: {{n}}i</p>
                <label :id="id" class="inline">{{label}}</label>
                <template v-if="help_text">
                    <HelpText :help_text="help_text" /> 
                </template>

                <template v-if="help_text_url">
                    <HelpTextUrl :help_text_url="help_text_url" /> 
                </template>
                
                <a class="collapse-link-top pull-right" @click.prevent="expand"><span class="glyphicon glyphicon-chevron-down"></span></a>
                <div class="children-anchor-point collapse in" style="padding-left: 0px"></div>
                <span :class="{'hidden':isRemovable}" v-if="isPreviewMode">
                    <a :id="'remove_'+name" >Remove {{label}}</a>
                </span>
                <a class="collapse-link-bottom pull-right"  @click.prevent="minimize"><span class="glyphicon glyphicon-chevron-up"></span></a>
                <div :class="{'row':true,'collapse':true, 'in':isExpanded}" style="margin-top:10px;" >
                    <div class="col-sm-12">
                        <slot></slot>
                    </div>
                </div>
            </div>
        </div>
        <button v-on:click="handleChange">Add Another</button>
    </div>
-->


<!--
    <div>
            <div v-if="isRepeatable" v-for="n in repeat">
                <div class="repeat-group" :data-que="n">
                            <slot></slot>
                </div>
            </div>
            <button v-on:click="handleChange">Add Another</button>
    </div>
-->

<!--
    <div>
        <div v-for="n in repeat" class="panel panel-default">
            <div v-if="isRepeatable">
                <div class="repeat-group panel-body" :data-que="n" ref="list">
                    <p>N: {{name}} {{n}} {{isRepeatable}}</p>
                    <slot></slot>
                </div>
            </div>
            <div v-else>
                <slot></slot>
            </div>
        </div>
        <button v-if="isRepeatable" v-on:click.stop.prevent="add_another2">Add Another</button>
    </div>
-->

<!--
    <div>
        <div id="id_slot" class="col-sm-12">
            <slot></slot>
        </div>

        <div v-for="n in repeat" class="panel panel-default">
            <p>N: {{name}} {{n}} {{isRepeatable}}</p>
            <div class="repeat-group panel-body" :data-que="n">
            </div>
        </div>

        <div id="id_slot2" ref="list" class="col-sm-12"></div>

        <button v-if="isRepeatable" v-on:click.stop.prevent="add_another3">Add Another</button>
    </div>
-->

    <div>
        <div v-for="n in repeat" class="panel panel-default">
            <div v-if="isRepeatable" ref="list">
                <div class="repeat-group panel-body" :data-que="n">
                    <p>N: {{name}} {{n}} {{isRepeatable}}</p>
                    <slot></slot>
                </div>
                <div class="repeat-group panel-body" :data-que="2">
                    <p>N: {{name}} {{2}} {{isRepeatable}}</p>
                    <slot></slot>
                </div>
            </div>
            <div v-else>
                <slot></slot>
            </div>
        </div>
        <button v-if="isRepeatable" v-on:click.stop.prevent="add_another4">Add Another</button>
    </div>

</template>

<script>
import Vue from 'vue'

Vue.mixin({
    methods: {
        compile: function(content, refs){
            var tmp = Vue.extend({
                template: content
                //mytest: content
            }); 
            new tmp().$mount(this.$refs[refs]);
        },

        calert: function(){
            alert('Çalışıyor');
        },
    }
})

import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    name:"group",
    props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode", "isRepeatable"],
    //props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode"],
    data:function () {
        return{
            repeat:1,
            //isRepeatable:true,
            isExpanded:true,
            //cloned: $('#id_slot').clone().appendTo('div[data-que='+vm.repeat+']');
            cloned: $('#id_slot').clone(),
        }
    },
    components: {HelpText, HelpTextUrl},
    methods:{
        expand:function(e) {
            this.isExpanded = true;
        },
        minimize:function(e) {
            this.isExpanded = false;
        },
        handleChange:function (e) {
            let vm = this;

            //vm.show_spinner = true;
            if (vm.isRepeatable) {

                let  el = $(e.target).attr('data-que');
                //let avail = $('input[name='+e.target.name+']');
                let avail = $('.repeat-group');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                //avail.pop();
                if (vm.repeat == 1) {
                    vm.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        vm.repeat+=1;
                    }
                }
                //$('#mydiv1').clone().appendTo('#mydiv2');
                //$('#mydiv1').clone().appendTo('div[data-que='+vm.repeat+']');
                //$('div[data-que='+vm.repeat+']').clone().appendTo('div[data-que=1]');
                //$('div[data-que=1]').clone().appendTo('div[data-que='+vm.repeat+']');
                //$('div[data-que=1]').html($('div[data-que='+vm.repeat+']').html());
            //    $('div[data-que='+vm.repeat+']').html($('div[data-que=1]').html());
                //jQuery('.div1').html(jQuery("#div2").html());
                //$(e.target).css({ 'display': 'none'});

                var id = vm.repeat - 1;
                $('div[data-que='+id+']').html($('div[data-que=1]').html());
            }
            //vm.show_spinner = false;
        },
        add_another:function (e) {
            var id = vm.repeat - 1;
            //$('div[data-que='+vm.repeat-1+']').html($('div[data-que=1]').html());
            $('div[data-que='+id+']').html($('div[data-que=1]').html());
        },

        add_another2:function (e) {
            let vm = this;

            if (vm.isRepeatable) {

                let  el = $(e.target).attr('data-que');
                let avail = $('.repeat-group');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                vm.repeat+=1;

                var id = vm.repeat - 1;
                //$('div[data-que='+id+']').html($('div[data-que=1]').html());
                //$('div[data-que=1]').clone().appendTo('div[data-que='+vm.repeat+']');

                //$("div").attr("id", function(i){return "child"+i;})
                //$('div[data-que='+id+']').attr("name", function(i){return "child"+i;})
``
                $('div[data-que=1]').clone().appendTo('div[data-que='+vm.repeat+']');
            }
        },

        add_another3:function (e) {
            let vm = this;

            //var element = $('#id_slot').append(vm.cloned);
            //var element = $('#id_slot2').append($('#id_slot').clone());
            var element = $('#id_slot').clone();
            //this.$compile(element.get(0));
            this.compile(element, 'list');
        },

        add_another4:function (e) {
            let vm = this;

            if (vm.isRepeatable) {

                let  el = $(e.target).attr('data-que');
                let avail = $('.repeat-group');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                vm.repeat+=1;

                var id = vm.repeat - 1;
                $('div[data-que=1]').clone().appendTo('div[data-que=2]');

                var element = $('div[data-que=2]');
                //var element = $('#id_slot').clone();
                this.compile(element, 'list');
            }
        },


/*
        compile: function(content, refs){ 
            var tmp = Vue.extend({
                template: content
            }); 
            new tmp().$mount(this.$refs[refs]);
        },
*/

        add_empty_div:function (e) {
            // add empty div placeholder for 'add another' button
            let vm = this;
            if (vm.isRepeatable) {
                let avail = $('.repeat-group');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                vm.repeat+=1;
            }
        },

    },
    mounted:function () {
        var vm =this;
        $('[data-toggle="tooltip"]').tooltip();
    }
}
</script>

<style lang="css">
    .collapse-link-top,.collapse-link-bottom{
        cursor:pointer;
    }
</style>
