define(['jQuery', 'lodash', 'moment', 'js/wl.dataTable'], function ($, _, moment, dataTable) {
    "use strict";

    // constants
    var DATE_TIME_FORMAT = 'DD/MM/YYYY HH:mm:ss';

    function initActionsLog(options) {
        // multi-used selectors
        var $logListContent, logDataTable;

        // default options
        options = _.defaults(options || {}, {
            showLogPopoverSelector: '#showActionLog',
            logTableSelector: $('<table id="actionsLog-table" class="table table-striped table-bordered dataTable">'),
            logListURL: 'insert-default-url-here'
        });

        // if log table is in a popover, need to prepare log table container before initializing table or
        // search/paging/etc won't show
        if (options.showLogPopoverSelector) {
            $logListContent = $('<div>').append($(options.logTableSelector));
        }

        // init log table
        logDataTable = initLogTable(options.logListURL, options.logTableSelector);

        // init log table popover if provided
        if (options.showLogPopoverSelector) {
            $(options.showLogPopoverSelector).popover({
                container: 'body',
                title: 'Action log',
                content: $logListContent,
                placement: 'right',
                trigger: "manual",
                html: true
            }).click(function () {
                var isVisible = $(this).data()['bs.popover'].tip().hasClass('in');
                if (!isVisible) {
                    logDataTable.ajax.reload();
                    $(this).popover('show');
                    $('[data-toggle="tooltip"]').tooltip();
                } else {
                    $(this).popover('hide');
                }
            });
        }
    }

    function initLogTable(logListURL, tableSelector) {
        var $table = $(tableSelector),
            tableOptions = {
                paging: true,
                info: true,
                searching: true,
                processing: true,
                deferRender: true,
                serverSide: false,
                autowidth: true,
                order: [[2, 'desc']],
                // TODO: next one is to avoid the 'search' field to go out of the popover (table width is small).
                // see https://datatables.net/reference/option/dom
                dom:
                "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                ajax: {
                    url: logListURL
                }
            },
            colDefinitions = [
                {
                    title: 'Who',
                    data: 'who'
                },
                {
                    title: 'What',
                    data: 'what'
                },
                {
                    title: 'When',
                    data: 'when',
                    render: function (date) {
                        return moment(date).format(DATE_TIME_FORMAT);
                    }
                }
            ];

        // set DT date format sorting
        dataTable.setDateTimeFormat(DATE_TIME_FORMAT);

        // activate popover when table is drawn.
        $table.on('draw.dt', function () {
            var $tablePopover = $table.find('[data-toggle="popover"]');
            if ($tablePopover.length > 0) {
                $tablePopover.popover();
                // the next line prevents from scrolling up to the top after clicking on the popover.
                $($tablePopover).on('click', function (e) {
                    e.preventDefault();
                    return true;
                });
            }
        });

        return dataTable.initTable($table, tableOptions, colDefinitions);
    }

    return {
        init: function(options) {
            return initActionsLog(options);
        }
    };
});