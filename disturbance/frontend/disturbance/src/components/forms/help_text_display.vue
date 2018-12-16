<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <p class="col-md-9" v-html="help_text"></p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["help_text"]
}
</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
</style>
