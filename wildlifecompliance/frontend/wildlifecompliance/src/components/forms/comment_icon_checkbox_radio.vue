<template>
    <div>
        <template v-if="canViewComments">
            <template v-if="!showingComment">
                <a v-if="field_data.comment_value" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
            </template>
            <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
        </template>
        <Comment :question="label" :name="name+'-comment-field'" v-show="showingComment" :field_data="field_data"/>
    </div>
</template>
<script>
import { mapGetters } from 'vuex';
import Comment from './comment.vue';
export default {
    props:["name","field_data","label"],
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
