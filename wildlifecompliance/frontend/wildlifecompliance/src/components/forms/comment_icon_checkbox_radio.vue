<template>
    <div>
        <template v-if="canViewComments">
            <template v-if="!showingComment">
                <a v-if="field_data.comment_value" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
            </template>
            <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            <Comment :question="label" :name="name+'-comment-field'" v-show="showingComment" :field_data="field_data"/>
        </template>

        <div v-if="canViewDeficiencies">
            <div v-if="canEditDeficiencies">
                <div v-if="!showingDeficiencies">
                    <a v-if="field_data.deficiency_value" href=""  @click.prevent="toggleDeficiencies"><i style="color:red" class="fa fa-exclamation-triangle">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleDeficiencies"><i class="fa fa-exclamation-triangle">&nbsp;</i></a>
                </div>
                <a href="" v-else  @click.prevent="toggleDeficiencies"><i class="fa fa-ban">&nbsp;</i></a>
                <Comment :question="label" :name="name+'-deficiency-field'" v-show="showingDeficiencies" :field_data="field_data" :isDeficiency="true"/>
            </div>
            <div v-else-if="field_data.deficiency_value" style="color:red">
                <i class="fa fa-exclamation-triangle">&nbsp;</i>
                <span>{{field_data.deficiency_value}}</span>
            </div>
        </div>
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
            showingComment: false,
            showingDeficiencies: false
        }
    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        toggleDeficiencies: function() {
            this.showingDeficiencies = !this.showingDeficiencies;
        },
    },
    computed: {
        ...mapGetters([
            'canViewComments',
            'canViewDeficiencies',
            'canEditDeficiencies',
        ]),
    }
}
</script>
