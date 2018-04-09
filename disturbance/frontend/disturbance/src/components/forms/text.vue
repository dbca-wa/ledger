<template lang="html">
    <div>
        <div class="form-group">
            <label for="label" >{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 
            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <input :readonly="readonly" :type="type" class="form-control" :name="name" :value="value" />
        </div>
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
export default {
    props:["type","name","comment_value","value","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly"],
    components: {Comment, HelpText},
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
