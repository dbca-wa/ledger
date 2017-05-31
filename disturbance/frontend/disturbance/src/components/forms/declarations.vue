<template lang="html">
    <div class="form-group">
        <label>
            <input :name="name" type="checkbox" @change="handleDeclaration" data-parsley-required :checked="isChecked" />
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
            //TODO return value from database
            return false;
        }
    }
}
</script>

<style lang="css">
</style>
