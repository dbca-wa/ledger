<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id">{{ label }}</label>

            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText  :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl  :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
     
            <template v-if="readonly">
                <select v-if="!isMultiple" disabled ref="selectB" :id="selectid" :name="name" class="form-control" :data-conditions="cons" style="width:100%">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" @change="handleChange" :selected="op.value == value">{{ op.label }}</option>
                </select>
                <select v-else disabled ref="selectB" :id="selectid" class="form-control" multiple style="width:100%">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" :selected="multipleSelection(op.value)">{{ op.label }}</option>
                </select>
                <template v-if="isMultiple">
                    <input v-for="v in value" input type="hidden" :name="name" :value="v" :required="isRequired"/>
                </template>
                <template v-else>
                    <input type="hidden" :name="name" :value="value" :required="isRequired"/>
                </template>
            </template>
            <template v-else>
                <select v-if="!isMultiple" ref="selectB" :id="selectid" :name="name" class="form-control" :data-conditions="cons" style="width:100%" :required="isRequired">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" @change="handleChange" :selected="op.value == value">{{ op.label }}</option>
                </select>
                <select v-else ref="selectB" :id="selectid" :name="name" class="form-control" multiple style="width:100%" :required="isRequired">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" :selected="multipleSelection(op.value)">{{ op.label }}</option>
                </select>
            </template>
        </div>

        
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 


    </div>
</template>

<script>
var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:{
        'name':String,
        'label':String,
        'id': String,
        'isRequired': String,
        'help_text':String,
        'help_text_assessor':String,
        'help_text_url':String,
        'help_text_assessor_url':String,
        "value":[String,Array],
        "comment_value": String,
        "assessor_readonly": Boolean,
        "options":Array,
        "conditions":Object,
        "handleChange":null,
        "isMultiple":{
            default:function () {
                return false;
            }
        },
        "assessorMode":{
            default:function () {
                return false;
            }
        },
        'readonly': Boolean
    },
    data:function () {
        let vm =this;
        return{
            selected: (this.isMultiple) ? [] : "",
            selectid: "select"+vm._uid,
            multipleSelected: [],
            showingComment: false,
           
        }
    },
    computed:{
        cons:function () {
            return JSON.stringify(this.conditions);
        },
    },
    components: { Comment, HelpText, HelpTextUrl,},
    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
       

        multipleSelection: function(val){
            if (Array.isArray(this.value)){
                if (this.value.find(v => v == val)){
                    return true;
                }
            }else{
                if (this.value == val){return true;}
            }
            return false;
        },
        init:function () {
            let vm =this;
            setTimeout(function (e) {
                   $('#'+vm.selectid).select2({
                       "theme": "bootstrap",
                       allowClear: true,
                       placeholder:"Select..."
                   }).
                   on("select2:select",function (e) {
                       var selected = $(e.currentTarget);
                       vm.handleChange(selected[0])
                       e.preventDefault();
                        if( vm.isMultiple){
                            vm.multipleSelected = selected.val();
                        }
                   }).
                   on("select2:unselect",function (e) {
                        var selected = $(e.currentTarget);
                        vm.handleChange(selected[0])
                        e.preventDefault();
                        if( vm.isMultiple){
                            vm.multipleSelected = selected.val();
                        }
                   });
                   if (vm.value) {
                       vm.handleChange(vm.$refs.selectB);
                   }
               },100);
        }
    },
    mounted:function () {
        this.init();
    }
}
</script>

<style lang="css">
.select2-container {
  width: 100% !important;
}

input {
    box-shadow:none;
}
</style>
