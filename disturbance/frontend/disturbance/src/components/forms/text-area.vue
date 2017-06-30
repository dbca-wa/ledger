<template lang="html">
    <div class="form-group">
        <label for="label" >{{ label }}</label>
        <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
        <i data-toggle="tooltip" v-if="help_text_assessor && assessorMode" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text_assessor">&nbsp;</i>
        <textarea :readonly="readonly" class="form-control" rows="5" :name="name">{{ value }}</textarea><br/>
    </div>
</template>

<script>
export default {
    props:["name","value","help_text","help_text_assessor","assessorMode","label","readonly"]
}
</script>

<style lang="css">
</style>
