<template lang="html" id="error-404">
  <div> 
    <div class="container">
      <div class="row" >
        <div class="col-lg-12 alert alert-danger">
            <h1 class="text-center"> 404 Not Found </h1>
        </div>
        <div class="col-lg-12" style="margin-top:20px;">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name:'error-404',
}
</script>

<style lang="css">
</style>
