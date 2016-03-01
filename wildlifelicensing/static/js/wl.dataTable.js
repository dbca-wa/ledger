define(
    'js/wl.dataTable',
    [
        'jQuery',
        'datatables.net',
        'dataTableBootstrap'
    ],
    function ($) {
        'use strict';

        var defaultOptions = {
            paging: true,
            info: true,
            searching: true,
            scrollCollapse: true,
            processing: true,
            deferRender: true,
            autowidth: true
        };

        function decorateTable(table) {

            table.populate = function (data) {
                if (data) {
                    if (typeof data === 'string') {
                        data = $.parseJSON(json);
                    }
                    table.rows.add(data).draw();
                }
            };

            table.fetch = function (url) {
                return $.ajax({
                    url: url,
                    dataType: 'json',
                    success: function (data) {
                        table.populate(data);
                    }
                });
            };
            return table;
        }

        return {
            initTable: function (selector, tableOptions, columnsOptions) {
                var options = {},
                    table;
                $.fn.DataTable.ext.errMode = "throws";  // will throw a console error instead of an alert
                $.extend(options, defaultOptions, tableOptions, {columns: columnsOptions});
                table = $(selector).DataTable(options);
                // add some methods
                return decorateTable(table);
            }
        }
    }
);
