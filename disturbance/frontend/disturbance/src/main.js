// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import resource from 'vue-resource'
import App from './App'
import router from './router'
import bs from 'bootstrap'
import helpers from '@/utils/helpers'
require('../node_modules/bootstrap/dist/css/bootstrap.css');
//require('../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
require('../node_modules/font-awesome/css/font-awesome.min.css')

Vue.config.productionTip = false
Vue.use(resource);

// Add CSRF Token to every request
Vue.http.interceptors.push(function(request, next) {
    // modify headers
    request.headers.set('X-CSRFToken', helpers.getCookie('csrftoken'));

    // continue to next interceptor
    next();
});


/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App }
})
