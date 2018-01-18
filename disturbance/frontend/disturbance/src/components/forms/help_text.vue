<template lang="html">
    <span v-if="!isForAssessor">
        <i v-if="help_text" data-toggle="tooltip" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
    </span>
    <span v-else>
        <i v-if="help_text && assessorMode" data-toggle="tooltip" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text">&nbsp;</i>
    </span>
</template>

<script>
export default {
    props:["help_text","assessorMode","isForAssessor"]
}
</script>

<style lang="css">
</style>
