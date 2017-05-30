<template lang="html">
    <div class="form-group">
      <label for="label" >{{ label }}</label>
      <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
      <textarea class="form-control" rows="5" name="name">{{ value }}</textarea><br/>
    </div>
</template>

<script>
export default {
    props:["name","value","help_text","label"]
}
</script>

<style lang="css">
</style>
