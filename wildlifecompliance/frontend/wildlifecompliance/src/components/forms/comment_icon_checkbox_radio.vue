<template>
    <div>
        <template v-if="canViewComments">
            <template v-if="!showingComment">
                <a v-if="comment_value" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
            </template>
            <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
        </template>
        <Comment :question="label" :name="name+'-comment-field'" v-show="showingComment" :value="comment_value"/>
    </div>
</template>
<script>
import { mapGetters } from 'vuex';
import Comment from './comment.vue';
export default {
    props:["name","comment_value","label"],
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
    },
    computed: {
        ...mapGetters([
            'canViewComments',
        ]),
    }
}
</script>
