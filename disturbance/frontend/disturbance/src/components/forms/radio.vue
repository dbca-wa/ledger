<template lang="html">
    <div>
        <div class="radio">
            <label>
                <input ref="radioB" :name="name" type="radio" :value="value" @change="handleChange"  :required="isRequired" :data-conditions="options" :checked="isChecked"/>{{ label}}
            </label>
        </div>
    </div>
</template>

<script>
export default {
    name:"radiobuttons",
    props:["value","label","name","isRequired","handleChange","conditions","savedValue"],
    computed:{
        isChecked:function () {
            return this.value == this.savedValue;
        },
        options:function () {
            return JSON.stringify(this.conditions);
        }
    },
    mounted:function () {
        if (this.value == this.savedValue) {
            var input = this.$refs.radioB;
            var e = document.createEvent('HTMLEvents');
            e.initEvent('change', true, true);
            input.dispatchEvent(e);
        }
    }
}
</script>

<style lang="css">
</style>
