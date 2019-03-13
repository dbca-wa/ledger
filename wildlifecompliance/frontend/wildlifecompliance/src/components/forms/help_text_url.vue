<template lang="html">
    <span v-if="help_text_url">
        <a :href="help_text_url" target="_blank"><i class="fa fa-question-circle" style="color:green">&nbsp;</i></a>
    </span>
</template>



<script>
export default {
    props:["help_text_url"],
}
</script>

<style lang="css">
</style>


