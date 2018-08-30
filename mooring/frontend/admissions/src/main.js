// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';
import 'font-awesome/css/font-awesome.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router'
import admissions from './admissions';
import costs from './costs';
import App from './App';
Vue.use(VueRouter);

require('custom-event-polyfill');

const routes = [
    {
        path: '/admissions',
        component: admissions,
        name: 'admissions'
    },
    {
        path: '/admissions-cost',
        component: costs,
        name: 'cost'
    }
];

const router = new VueRouter({
  routes,
  mode: 'history',
});

const app = new Vue({
    router,
    render: h => h(App)
}).$mount('#app');