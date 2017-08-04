<template lang="html">
    <div>
        <div class="form-group">
            <label for="label" >{{ label }}</label>
            <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
            <i data-toggle="tooltip" v-if="help_text_assessor && assessorMode" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text_assessor">&nbsp;</i>
            <template v-if="assessorMode">
                <a href="" v-if="!showingComment" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <textarea :readonly="readonly" class="form-control" rows="5" :name="name">{{ value }}</textarea><br/>
        </div>
        <Comment :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 
    </div>
</template>

<script>
import Comment from './comment.vue'
export default {
    props:["name","value","help_text","help_text_assessor","assessorMode","label","readonly","comment_value","assessor_readonly"],
    components: {Comment},
    data(){
        let vm = this;
        return {
            showingComment: false
        }
    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        }
    }
}
</script>

<style lang="css">
</style>
