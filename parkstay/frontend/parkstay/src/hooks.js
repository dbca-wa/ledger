// module for all third party dependencies

import $ from 'jquery'
var DataTable = require('datatables.net');
var DataTableBs = require('datatables.net-bs');
var DataTableRes = require('datatables.net-responsive-bs');
var bootstrap = require('bootstrap');
var moment = require('moment/moment.js');
var MomentRange = require('moment-range');
var datetimepicker = require('eonasdan-bootstrap-datetimepicker');
var validate = require('jquery-validation');
var slick = require('slick-carousel-browserify');
var select2 = require('select2');
var awesomplete = require('awesomplete');
var daterangepicker = require('bootstrap-daterangepicker');
var formValidate = require('./components/utils/validator.js');
var Moment = MomentRange.extendMoment(moment);
var swal = require('sweetalert2');
var htmlEscape = require('html-escape');
import api_endpoints from './apps/api.js';
import store from './apps/store';
import helpers from './components/utils/helpers.js';
import {bus} from './components/utils/eventBus.js';
var debounce = function (func, wait, immediate) {
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    'use strict';
    var timeout;
    return function () {
        var context = this;
        var args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    }
};

export {
    $,
    DataTable,
    DataTableBs,
    DataTableRes,
    Moment,
    datetimepicker,
    api_endpoints,
    helpers,
    validate,
    bus,
    slick,
    select2,
    daterangepicker,
    awesomplete,
    formValidate,
    swal,
    htmlEscape,
    store,
    debounce
}
