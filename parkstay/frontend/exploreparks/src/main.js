// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import VuePaginate from 'vue-paginate';
import jQuery from 'jquery';
import ParkFinder from './parkfinder.vue';

Vue.use(VuePaginate);

global.parkfinder = new Vue({
  el: '#parkfinder',
  components: { 'parkfinder': ParkFinder }
});
