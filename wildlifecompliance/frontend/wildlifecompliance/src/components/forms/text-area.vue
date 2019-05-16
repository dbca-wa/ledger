<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
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

            <textarea :readonly="readonly" class="form-control" rows="5" :name="name" :required="isRequired" v-model="field_data.value"></textarea><br/>
        </div>
    </div>
</template>

<script>
import CommentBlock from './comment_block.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
export default {
    props:["name", "field_data", "id", "isRequired", "help_text", "label", "readonly", "help_text_url"],
    components: {CommentBlock, HelpText, HelpTextUrl},
    data(){
        return {
        }
    },
    methods: {
    },
    computed:{
    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
