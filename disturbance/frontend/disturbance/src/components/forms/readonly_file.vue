<template lang="html">
    <div class="form-group">
      <label for="label" >{{ label }}</label>
      <p>{{ value }}</p>
    </div>
</template>

<script>
export default {
    props:["value","label"]
}
</script>

<style lang="css">
</style>
