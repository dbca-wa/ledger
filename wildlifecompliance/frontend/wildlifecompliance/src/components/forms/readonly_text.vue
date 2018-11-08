<template lang="html">
    <div class="col-md-12">
        <div v-show="box_view" class="form-group">
            <div class="row">
              <label :id="id" class="col-md-3" for="label" >{{ label }}</label>
              <div class="col-md-9">
                  <textarea :readonly="readonly" :type="type" class="form-control" :name="name" :value="value"></textarea>
              </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["box_view","type","name","value", "id", "label","readonly"]
}
</script>

<style lang="css">
</style>
