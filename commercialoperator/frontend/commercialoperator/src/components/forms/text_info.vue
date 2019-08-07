<template lang="html">
    <div class="form-group">
        <label :id="id" for="label" v-html="label"></label>
        <input readonly="true" type="text" class="form-control" :name="name" :value="value" />
    </div>
</template>

<script>
export default {
    props:["label", "name", "value", "id"]
}
</script>

<style lang="css">
</style>
