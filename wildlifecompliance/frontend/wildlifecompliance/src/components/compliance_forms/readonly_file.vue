<template lang="html">
    <div class="form-group">
      <label :id="id" for="label" >{{ label }}</label>
      <p>{{ value }}</p>
    </div>
</template>

<script>
export default {
    props:["value", "label", "id"]
}
</script>

<style lang="css">
</style>
