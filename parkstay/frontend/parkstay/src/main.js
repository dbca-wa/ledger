// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import Vue from 'vue'
import Campgrounds from './components/campgrounds.vue'
import Router from 'vue-router'

Vue.use(Router);

const routes = [
  { path: '/', component: Campgrounds }
];

const router = new Router({
  'routes' : routes,
  'history': true
});

new Vue({
  'router':router
}).$mount('#app');
