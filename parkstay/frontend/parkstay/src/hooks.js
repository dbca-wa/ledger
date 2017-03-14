// module for all third party dependencies

import $ from 'jquery'
var DataTable = require( 'datatables.net' )();
var DataTableBs = require( 'datatables.net-bs' )();
var DataTableRes = require( 'datatables.net-responsive-bs' )();
var moment = require('moment');
var MomentRange = require('moment-range');
var datetimepicker = require('datetimepicker');
var validate = require('jquery-validation');
var slick = require('slick-carousel-browserify');
var select2 = require('select2');
var awesomplete = require('awesomplete')
var daterangepicker = require('bootstrap-daterangepicker')
var formValidate = require('formValidate')
var Moment = MomentRange.extendMoment(moment);
import api_endpoints from './apps/api.js';
import helpers from './components/utils/helpers.js'
import {bus} from './components/utils/eventBus.js'
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
    formValidate
}
