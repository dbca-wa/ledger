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
        <!--<div v-if="isRepeatable" v-for="n in repeat" class="panel panel-default">-->
        <div v-for="n in repeat" class="panel panel-default">
            <div v-if="isRepeatable">
                <div class="repeat-group panel-body" :data-que="n">
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

    <div>
        <div class="col-sm-12">
            <slot></slot>
        </div>

        <div v-for="n in repeat" class="panel panel-default">
            <p>N: {{name}} {{n}} {{isRepeatable}}</p>
            <div class="repeat-group panel-body" :data-que="n">
            </div>
        </div>


    </div>
</template>

<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    name:"group",
    props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode", "isRepeatable"],
    //props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode"],
    data:function () {
        return{
            repeat:0,
            //isRepeatable:true,
            isExpanded:true
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
                /*
                if (vm.repeat == 1) {
                    vm.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        vm.repeat+=1;
                    }
                }
                */
                vm.repeat+=1;

                var id = vm.repeat - 1;
                //$('div[data-que='+id+']').html($('div[data-que=1]').html());
                $('div[data-que=1]').clone().appendTo('div[data-que='+vm.repeat+']');

                //$("div").attr("id", function(i){return "child"+i;})
                $('div[data-que='+id+']').attr("name", function(i){return "child"+i;})
            }
        },

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
