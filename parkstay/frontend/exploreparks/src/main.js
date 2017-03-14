// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';
import 'awesomplete/awesomplete.css';

import Vue from 'vue';
import VuePaginate from 'vue-paginate';
import ParkFinder from './parkfinder.vue';

Vue.use(VuePaginate);

global.parkfinder = new Vue(ParkFinder);
