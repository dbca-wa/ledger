// module for all third party dependencies

import $ from 'jquery'
var DataTable = require('datatables.net');
var DataTableBs = require('datatables.net-bs');
var DataTableRes = require('datatables.net-responsive-bs');
var bootstrap = require('bootstrap');
var moment = require('moment/moment.js');
var MomentRange = require('moment-range');
var datetimepicker = require('eonasdan-bootstrap-datetimepicker');
var daterangepicker = require('bootstrap-daterangepicker');
var Moment = MomentRange.extendMoment(moment);
import helpers from './utils/helpers.js';
import {bus} from './utils/eventBus.js';
export {
    $,
    DataTable,
    DataTableBs,
    DataTableRes,
    Moment,
    datetimepicker,
    helpers,
    bus,
    daterangepicker,
}
