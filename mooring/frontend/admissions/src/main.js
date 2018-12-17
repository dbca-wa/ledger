// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';
import Vue from 'vue';
import resource from 'vue-resource'
import VueRouter from 'vue-router'
import VModal from 'vue-js-modal';
import admissions from './admissions';
import costs from './costs';
import App from './App';
import alert from './utils/alert.vue';
import store from './utils/store';
import { mapGetters } from 'vuex';
var css = require('./hooks-css.js');
Vue.use(VueRouter);
Vue.use(resource);
Vue.use(VModal);
console.log('main loaded');
require('custom-event-polyfill');
console.log(costs);
const routes = [
    {
        path: '/admissions/',
        component: admissions, 
//        name: 'admissions'
    },
    {
        path: '/admissions-cost/',
        component: costs,
//        name: 'cost'
    }
];

const router = new VueRouter({
  routes,
  mode: 'history',
});


//console.log(router);
new Vue({
    router,
}).$mount('#menu');

const app = new Vue({
    router,
    store,
    components:{
       alert
    },
    watch:{
        $route:function () {
            let vm =this;
            vm.$store.dispatch("updateAlert",{
                visible:false,
                type:"danger",
                message: ""
            });
        }
    },
    computed:{
        ...mapGetters([
            "showAlert",
            "alertType",
           "alertMessage"
        ])
    },
    render: h => h(App)
}).$mount('#appdiv');
