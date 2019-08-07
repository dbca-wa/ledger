<template lang="html">
    <div class="form-group">
        <label :id="id">
            <input ref="Checkbox" :name="name" type="checkbox" @change="handleDeclaration" data-parsley-required :checked="isChecked" :required="isRequired"/>
            {{label}}
        </label>

        <template v-if="help_text">
            <p class="help-block">{{ help_text }}</p>
        </template>
        <template v-if="help_text_url">
            <HelpTextUrl  :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
        </template> 
    </div>
</template>

<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:['name','label', 'id', 'help_text',"handleDeclaration", "isRequired", "help_text_url"],
    computed:{
        isChecked:function () {
            return (this.value == 'on');
        }
    },
    mounted:function () {
        let vm = this;
        if (vm.isChecked) {
            var input = this.$refs.Checkbox;
            var e = document.createEvent('HTMLEvents');
            e.initEvent('change', true, true);
            input.dispatchEvent(e);
        }
    }
}
</script>

<style lang="css">
</style>
