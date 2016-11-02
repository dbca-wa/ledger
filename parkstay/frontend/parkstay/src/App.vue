<template>
  <div id="app">
    <campgrounds></campgrounds>
  </div>
</template>

<script>
import Hello from './components/Hello.vue'
import campgrounds from './components/campgrounds.vue'

module.exports = {
  name: 'app',
  components: {
    campgrounds
  }

};
</script>
