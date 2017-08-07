<template lang="html">
    <div>
        <div class="form-group">
            <label>{{ label }}</label>
            <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
            <i data-toggle="tooltip" v-if="help_text_assessor && assessorMode" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text_assessor">&nbsp;</i>
            <template v-if="assessorMode">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <div class='input-group date'>
                <input :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value"/>
                <span class="input-group-addon">
                    <span class="glyphicon glyphicon-calendar"></span>
                </span>
            </div>
        </div>
        <Comment :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 
    </div>
</template>

<script>
import moment from 'moment'
import datetimepicker from 'datetimepicker'
import Comment from './comment.vue'
export default {
    props: ['name', 'label', 'readonly', 'help_text', 'help_text_assessor', 'assessorMode', 'value', 'conditions', "handleChange","comment_value","assessor_readonly"],
    data(){
        return {
            showingComment: false
        }
    },
    components: {Comment},
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
</style>
