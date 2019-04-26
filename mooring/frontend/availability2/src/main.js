// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';
import 'font-awesome/css/font-awesome.min.css'

import Vue from 'vue';
import availability from './availability';

require('custom-event-polyfill');

Vue.config.productionTip = false;

/* eslint-disable no-new */
global.availability = new Vue(availability);
