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
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <div class='input-group date'>
                <input type="text" :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value" :required="isRequired"/>
                <span class="input-group-addon">
                    <span class="glyphicon glyphicon-calendar"></span>
                </span>
            </div>
        </div>
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 
    </div>
</template>

<script>
import moment from 'moment'
import datetimepicker from 'datetimepicker'
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props: ['name', 'label', 'id', 'readonly', 'help_text', 'help_text_assessor', 'assessorMode', 'value', 'conditions', "handleChange","comment_value","assessor_readonly", "isRequired", 'help_text_url', 'help_text_assessor_url'],
    data(){
        return {
            showingComment: false
        }
    },
    components: {Comment, HelpText, HelpTextUrl},
    computed: {
        isChecked: function() {
        //TODO return value from database
        return false;
        },
        options: function() {
        return JSON.stringify(this.conditions);
        }
    },
    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        }
    },
    mounted: function() {
        $('.date').datetimepicker({
        format: 'DD/MM/YYYY'
        });
    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
