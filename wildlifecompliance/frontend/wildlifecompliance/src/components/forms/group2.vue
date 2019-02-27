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

<!-- EXAMPLE TEST SCHEMA - 'Importing Fauna (Non-Commercial)'

[{"help_text_url": "site_url:/help/disturbance/user/anchor=Section7-10", "name": "Section7-10", "type": "radiobuttons", "label": "8.10 Does existing road/trail infrastructure provide adequate access for the proposal without the need for further work?", "conditions": {"yes": [{"children": [{"isRequired": "true", "_help_text_url": "site_url:/help/disturbance/user/anchor=Section7-10-Yes1", "type": "text_area", "name": "Section7-10-Yes1", "label": "8.10.1 Prepare summary of access details and specify any road/trail access considerations/requirements"}, {"name": "Section7-10-Yes2", "type": "file", "label": "8.10.2 Highlight access route on map and attach map", "isRequired": "true", "_help_text_url": "site_url:/help/disturbance/user/anchor=Section7-10-Yes2", "isRepeatable": "true"}], "type": "group", "name": "Section7-10-YesGroup", "label": ""}], "no": [{"children": [{"children": [{"type": "checkbox", "name": "Section7-10-No1-No1", "label": "Minor - slight modification, upgrade or ongoing maintenance"}, {"conditions": {"on": [{"children": [{"type": "label", "name": "Section7-10-No1-No2-On-1", "label": "For DBCA only: If the value of work is greater than $20,000 and is of a complex and/or high-risk nature seek approval to call quotes/tender for works and notify Procurement Manager."}], "type": "group", "name": "Section7-10-No1-No2-OnGroup", "label": ""}]}, "type": "checkbox", "name": "Section7-10-No1-No2", "label": "Major works or new construction"}], "isRequired": "true", "type": "group", "name": "Section7-10-No1-NoGroup", "label": "8.10.3 Select the applicable type of work(s)"}], "isRepeatable": "true", "type": "group", "name": "Section7-10-NoGroup", "label": ""}]}, "options": [{"isRequired": "true", "value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]}]

-->

    <div>
        <div v-for="n in repeat" class="panel panel-default">
            <div v-if="isRepeatable">
                <div class="repeat-group panel-body" :data-que="n" :data-children="repeatable_options">
                    <p>N: {{name}} {{n}} {{isRepeatable}}</p>
                    <RepeatGroup :data_children="repeatable_children" :renderer="renderer" />
                </div>
            </div>
            <div v-else>
                <p>v-else block</p>
                <slot></slot>
            </div>
        </div>
        <button v-if="isRepeatable" v-on:click.stop.prevent="add_another">Add Another</button>
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
import RepeatGroup from './repeat_group.vue'
export default {
    name:"group",
    props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode", "isRepeatable", "repeatable_children", "renderer"],
    //props:["label", "name", "id", "help_text", "help_text_url", "isRemovable", "isPreviewMode"],
    data:function () {
        return{
            repeat:1,
            //isRepeatable:true,
            isExpanded:true,
            //cloned: $('#id_slot').clone().appendTo('div[data-que='+vm.repeat+']');
            //cloned: $('#id_slot').clone(),
        }
    },
    computed: {
        //repeatable_options: function() {
        //  return this.isRepeatable ? JSON.stringify(this.repeatable_children): "";
        //},
        repeatable_options: function() {
	  	    return JSON.stringify( this.replace_item(this.repeatable_children, 'name', this.repeat) );
        }

    },
    components: {HelpText, HelpTextUrl, RepeatGroup},
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
        _add_another:function (e) {
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

                $('div[data-que=1]').clone().appendTo('div[data-que='+vm.repeat+']');
            }
        },
		replace_item:function(obj, key, append_string) {
            /* Recursively append 'append_string' to value each time key is encountered */
		    if (obj.hasOwnProperty(key)) {
			    obj[key] = obj[key] + '_rep' + append_string;
		    }
		  
		    for (let _key in obj){
				if (typeof obj[_key] === 'object') {
				    console.log(_key, obj[_key]);
				    this.replace_item(obj[_key], key, append_string)
			    }
		    } return false;
		},
        add_another:function (e) {
            let vm = this;

            if (vm.isRepeatable) {

                let  el = $(e.target).attr('data-que');
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
