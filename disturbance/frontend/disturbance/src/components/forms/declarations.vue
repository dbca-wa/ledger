<template lang="html">
    <div class="form-group">
        <label>
            <input ref="Checkbox" :name="name" type="checkbox" @change="handleDeclaration" data-parsley-required :checked="isChecked" />
            {{label}}
        </label>
        <p class="help-block">{{ help_text }}</p>
    </div>
</template>

<script>
export default {
    props:['name','label','help_text',"handleDeclaration"],
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
