<template lang="html">
    <div class="form-group">
        <label for="label" v-html="label"></label>
        <input disabled="true" type="text" class="form-control" :name="name" :value="value" />
    </div>
</template>

<script>
export default {
    props:["label", "name", "value"]
}
</script>

<style lang="css">
</style>
