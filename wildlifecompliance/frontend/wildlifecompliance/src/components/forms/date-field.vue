<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id">{{ label }}</label>
            
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>

            <template v-if="canViewComments">
                <template v-if="!showingComment">
                    <a v-if="field_data.comment_value" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <div class='input-group date'>
                <input type="text" :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" v-model="value" :required="isRequired"/>
                <span class="input-group-addon">
                    <span class="glyphicon glyphicon-calendar"></span>
                </span>
            </div>
        </div>
        <Comment :question="label" :name="name+'-comment-field'" v-show="showingComment" :field_data="field_data"/>
    </div>
</template>

<script>
import moment from 'moment';
import datetimepicker from 'datetimepicker';
import Comment from './comment.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
import { mapGetters } from 'vuex';
export default {
    props: ["name", "label", "id", "readonly", "help_text", "field_data", "conditions", "handleChange", "isRequired", "help_text_url"],
    data(){
        return {
            showingComment: false
        }
    },
    components: {Comment, HelpText, HelpTextUrl},
    computed: {
        ...mapGetters([
            'canViewComments',
        ]),
        isChecked: function() {
            //TODO return value from database
            return false;
        },
        options: function() {
        return JSON.stringify(this.conditions);
        },
        value: {
            get: function() {
                return this.field_data.value;
            },
            set: function(value) {
                this.field_data.value = value;
            }
        },
    },
    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        }
    },
    mounted: function() {
        $('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        }).off('dp.change').on('dp.change', (e) => {
            this.value = $(e.target).data('DateTimePicker').date().format('DD/MM/YYYY');
        });
    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
