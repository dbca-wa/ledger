<template>
  <div id="app">
    <campgrounds></campgrounds>
  </div>
</template>

<script>
import campgrounds from './components/campgrounds.vue'

module.exports = {
  name: 'app',
  components: {
    campgrounds
  }

};
</script>
