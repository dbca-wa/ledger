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

            <CommentBlock 
                :label="label"
                :name="name"
                :field_data="field_data"
                />

            <span v-if="min!='' || max!=''">
                <input :readonly="readonly" :type="type" :min="min" :max="max" class="form-control" :name="name" v-model="field_data.value" :required="isRequired" />
            </span>
            <span v-else>
                <input :readonly="readonly" :type="type" class="form-control" :name="name" v-model="value" :required="isRequired" />
            </span>
        </div>
    </div>
</template>

<script>
import CommentBlock from './comment_block.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
import { mapActions } from 'vuex';
export default {
    props:["type","name","id", "field_data","isRequired","help_text","label","readonly", "help_text_url", "min", "max"],
    components: {CommentBlock, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        return {
        }
    },
    methods: {
        ...mapActions([
            'setFormValue',
        ]),
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
