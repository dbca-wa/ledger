<template lang="html">
    <div class="form-group">
      <label for="label" >{{ label }}</label>
      <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
      <input :type="type" class="form-control" :name="name" :value="value" />
    </div>
</template>

<script>
export default {
    props:["type","name","value","help_text","label"]
}
</script>

<style lang="css">
</style>
