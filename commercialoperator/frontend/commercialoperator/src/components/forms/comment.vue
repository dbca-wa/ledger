<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <label :id="id" class="col-md-3" for="label" >Deficiency</label>
                  <div class="col-md-9">
                      <textarea :readonly="readonly" :data-question="question" class="form-control deficiency" :name="name" :value="value" :required="isRequired"></textarea>
                  </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["name","question","value", "id", "readonly", "isRequired"]
}
</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
</style>
