// module for all third party dependencies

import $ from 'jquery'

var DataTable = require( 'datatables.net' )();
var DataTableBs = require( 'datatables.net-bs' )();

export {
    $,
    DataTable,
    DataTableBs
}
