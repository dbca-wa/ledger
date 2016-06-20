define(['jQuery', 'datatables.net', 'datatables.bootstrap'], function ($) {
    "use strict";

    return {
        init: function() {
            $('#customersTable').DataTable({
                ordering: false,
                searching: false,
                info: false
            });
        }
    }
});