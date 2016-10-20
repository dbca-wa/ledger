define(['jQuery', 'lodash', 'moment', 'js/wl.dataTable'], function ($, _, moment, dataTable) {
    "use strict";

    // constants
    var DATE_TIME_FORMAT = 'DD/MM/YYYY HH:mm:ss';

    function initCommunicationLog(options) {
        // default options
        options = _.defaults(options || {}, {
            showLogPopoverSelector: '#showCommunicationLog',
            showLogEntryModalSelector: '#addCommunicationLogEntry',
            logEntryModalSelector: '#logCommEntryModal',
            logEntryFormSelector: '#addLogCommEntryForm',
            logTableSelector: $('<table id="communicationsLog-table" class="table table-striped table-bordered dataTable">'),
            logListURL: 'insert-default-url-here',
            addLogEntryURL: 'insert-default-url-here'
        });

        // multi-used selectors
        var $logEntryModal = options.logEntryModalSelector ? $(options.logEntryModalSelector) : null,
            $logListContent,
            logDataTable;

        // init log entry modal if provided
        if ($logEntryModal) {
            $(options.showLogEntryModalSelector).click(function () {
                $logEntryModal.modal('show');
            });
        }

        // if log table is in a popover, need to prepare log table container before initializing table or 
        // search/paging/etc won't show 
        if (options.showLogPopoverSelector) {
            $logListContent = $('<div>').append($(options.logTableSelector));
        }

        // init log table
        logDataTable = initCommunicationTable(options.logListURL, options.logTableSelector);

        // init log table popover if provided
        if (options.showLogPopoverSelector) {
            $(options.showLogPopoverSelector).popover({
                container: 'body',
                title: 'Communication log',
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

        // init log entry form if provided
        if (options.logEntryFormSelector) {
            $(options.logEntryFormSelector).submit(function (e) {
                var formData, submitPromise;

                e.preventDefault();

                // need a FormData object because it transmits data in the same format as form’s submit() method would,
                // as if the form encoding type were set to “multipart/form-data”, essentially allowing file attachments
                formData = new FormData($(this).get(0));

                submitPromise = $.ajax({
                    url: options.addLogEntryURL,
                    data: formData,
                    contentType: false,
                    processData: false,
                    type: 'POST'
                });

                submitPromise.done(function () {
                    logDataTable.ajax.reload();
                });

                submitPromise.done($.proxy(function () {
                        if ($logEntryModal) {
                            $logEntryModal.modal('hide');

                            // clear/reset form fields
                            $(this).find('#id_type').val($('#id_type').find('option:first').val());
                            $(this).find('#id_subject').val('');
                            $(this).find('#id_text').val('');
                            $(this).find('#id_attachment').val('');
                        }
                    },
                    this)
                );
            });
        }
    }

    function initCommunicationTable(logListURL, tableSelector) {
        function commaToNewline(s){
             return s.replace(/[,;]/g, '\n');
        }

        var $table = $(tableSelector),
            tableOptions = {
                paging: true,
                info: true,
                searching: true,
                processing: true,
                deferRender: true,
                serverSide: false,
                autowidth: true,
                order: [[0, 'desc']],
                ajax: {
                    url: logListURL
                }
            },
            colDefinitions = [
                {
                    title: 'Date',
                    data: 'created',
                    'render': function (date) {
                        return moment(date).format(DATE_TIME_FORMAT);
                    }
                },
                {
                    title: 'Type',
                    data: 'type'
                },
                {
                    title: 'Reference',
                    data: 'reference'
                },
                {
                    title: 'To',
                    data: 'to',
                    render: commaToNewline
                },
                {
                    title: 'CC',
                    data: 'cc',
                    render: commaToNewline
                },
                {
                    title: 'From',
                    data: 'fromm',
                    render: commaToNewline
                },
                {
                    title: 'Subject/Desc.',
                    data: 'subject'
                },
                {
                    title: 'Text',
                    data: 'text',
                    'render': function (value) {
                        var ellipsis = '...',
                            truncated = _.truncate(value, {
                                length: 100,
                                omission: ellipsis,
                                separator: ' '
                            }),
                            result = '<span>' + truncated + '</span>',
                            popTemplate = _.template('<a href="#" ' +
                                'role="button" ' +
                                'data-toggle="popover" ' +
                                'data-trigger="click" ' +
                                'data-placement="top auto"' +
                                'data-html="true" ' +
                                'data-content="<%= text %>" ' +
                                '>more</a>');
                        if (_.endsWith(truncated, ellipsis)) {
                            result += popTemplate({
                                text: value
                            });
                        }

                        return result;
                    },
                    'createdCell': function (cell) {
                        //TODO why this is not working?
                        // the call to popover is done in the 'draw' event
                        $(cell).popover();
                    }
                },
                {
                    title: 'Documents',
                    data: 'documents',
                    'render': function (values) {
                        var result = '';
                        _.forEach(values, function (value) {
                            // We expect an array [docName, url]
                            // if it's a string it is the url
                            var docName = '',
                                url = '';
                            if (_.isArray(value) && value.length > 1){
                                docName = value[0];
                                url = value[1];
                            }
                            if (typeof s === 'string'){
                                url = value;
                                // display the first  chars of the filename
                                docName = _.last(value.split('/'));
                                docName = _.truncate(docName, {
                                    length: 18,
                                    omission: '...',
                                    separator: ' '
                                });
                            }
                            result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                        });
                        return result;
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

    function initActionLog(options) {
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
        logDataTable = initActionTable(options.logListURL, options.logTableSelector);

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

    function initActionTable(logListURL, tableSelector) {
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
        initCommunicationLog: initCommunicationLog,
        initActionLog: initActionLog
    };
});