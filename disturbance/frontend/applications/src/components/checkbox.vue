<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label>
                    <input :name="name" type="checkbox" data-parsley-required :data-conditions="options" @change="handleChange" />
                    {{ label }}
                </label><i data-toggle="tooltip" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:['name','label','help_text','conditions',"handleChange"],
    computed:{
        isChecked:function () {
            //TODO return value from database
            return false;
        },
        options:function () {
            return JSON.stringify(this.conditions);
        }
    }
}
</script>

<style lang="css">
</style>
