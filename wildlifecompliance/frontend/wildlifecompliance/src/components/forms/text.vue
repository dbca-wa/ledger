<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline" >{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>


            <template v-if="renderer.canViewComments()">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <span v-if="min!='' || max!=''">
                <input :readonly="readonly" :type="type" :min="min" :max="max" class="form-control" :name="name" :value="value" :required="isRequired" />
            </span>
            <span v-else>
                <input :readonly="readonly" :type="type" class="form-control" :name="name" :value="value" :required="isRequired" />
            </span>
        </div>
        <Comment :question="label" :name="name+'-comment-field'" v-show="showingComment" :value="comment_value"/>
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:["type","name","id", "comment_value","value","isRequired","help_text","label","readonly", "help_text_url", "min", "max", "renderer"],
    components: {Comment, HelpText, HelpTextUrl},
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
    },
    computed: {
    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
