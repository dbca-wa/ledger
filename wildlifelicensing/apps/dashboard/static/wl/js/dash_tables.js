define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'moment',
        'bootstrap',
        'select2',
        'bootstrap-datetimepicker'
    ],
    function ($, _, dt, moment) {
        'use strict';

        var options,
            tableOptions = {
                paging: true,
                info: true,
                searching: true,
                scrollCollapse: true,
                processing: true,
                deferRender: true,
                serverSide: true,
                autowidth: true
            },
            dateFormat = 'DD/MM/YYYY',
            applicationsTable,
            licencesTable,
            returnsTable,
            $applicationsLicenceTypeFilter,
            $applicationsStatusFilter,
            $applicationsAssigneeFilter,
            $applicationsResetFilterButton,

            $licencesLicenceTypeFilter,
            $licencesStatusFilter,
            $licencesExpireAfterFilter,
            $licencesExpireBeforeFilter,
            $licencesResetFilterButton,

            $returnsLicenceTypeFilter,
            $returnsStatusFilter,
            $returnsResetFilterButton;

        function initFilters() {
            if (options.data.applications && options.data.applications.filters) {
                initApplicationsFilters();
            }
            if (options.data.licences && options.data.licences.filters) {
                initLicencesFilters();
            }
            if (options.data.returns && options.data.returns.filters) {
                initReturnsFilters();
            }
        }

        function initTables() {
            if (options.data.applications) {
                initApplicationsTable();
            }
            if (options.data.licences) {
                initLicencesTable();
            }
            if (options.data.returns) {
                initReturnsTable();
            }
        }

        function initApplicationsTable() {
            var applicationsTableOptions = $.extend({order: [[0, 'desc']]}, tableOptions, {
                    ajax: {
                        url: options.data.applications.ajax.url,
                        data: function (d) {
                            // add filters to the query
                            d.filters = $(options.selectors.applicationsFilterForm).serializeArray();
                        },
                        dataSrc: function (data) {
                            // intercept the returned data to display (console) error if any.
                            if (data['error']) {
                                window.console.error('Applications error:', data['error']);
                            }
                            return data['data'] || [];
                        },
                        error: function (xhr, textStatus, thrownError) {
                            window.console.log('Error while loading applications data:',
                                thrownError, textStatus, xhr.responseText, xhr.status);
                            //Stop the data table 'Processing'.
                            $(options.selectors.applicationsTable + '_processing').hide();
                        }
                    }
                }),
                applicationsColumns = options.data.applications.columnDefinitions;

            if (options.data.applications.tableOptions) {
                $.extend(applicationsTableOptions, options.data.applications.tableOptions);
            }
            applicationsTable = dt.initTable(
                options.selectors.applicationsTable,
                applicationsTableOptions,
                applicationsColumns
            );
        }

        function initApplicationsFilters() {
            var data = options.data,
                optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            function resetFilters() {
                $applicationsLicenceTypeFilter.prop('selectedIndex', 0).select2();
                $applicationsStatusFilter.prop('selectedIndex', 0).select2();
                $applicationsAssigneeFilter.prop('selectedIndex', 0).select2();
                if (applicationsTable) {
                    applicationsTable.search('').ajax.reload();
                }
            }

            // licence type
            if ($applicationsLicenceTypeFilter.length && data.applications.filters.licence_type) {
                _.forEach(data.applications.filters.licence_type.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsLicenceTypeFilter.append($node);
                });
                if (data.applications.filters.licence_type.selected) {
                    $applicationsLicenceTypeFilter.val(data.applications.filters.licence_type.selected);
                }
                $applicationsLicenceTypeFilter.on('change', function () {
                    if (applicationsTable) {
                        applicationsTable.ajax.reload();
                    }
                });
            }
            // status
            if ($applicationsStatusFilter.length && data.applications.filters.status) {
                _.forEach(data.applications.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsStatusFilter.append($node);
                });
                if (data.applications.filters.status.selected) {
                    $applicationsStatusFilter.val(data.applications.filters.status.selected);
                }
                $applicationsStatusFilter.on('change', function () {
                    if (applicationsTable) {
                        applicationsTable.ajax.reload();
                    }
                });
            }
            // assignee filter
            if ($applicationsAssigneeFilter.length && data.applications.filters.assignee) {
                _.forEach(data.applications.filters.assignee.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsAssigneeFilter.append($node);
                });
                if (data.applications.filters.assignee.selected) {
                    $applicationsAssigneeFilter.val(data.applications.filters.assignee.selected);
                }
                $applicationsAssigneeFilter.on('change', function () {
                    if (applicationsTable) {
                        applicationsTable.ajax.reload();
                    }
                });
            }

            if ($applicationsResetFilterButton.length) {
                $applicationsResetFilterButton.on('click', function () {
                    resetFilters();
                });
            }
        }

        function initLicencesTable() {
            var licencesTableOptions = $.extend({order: [[0, 'desc']]}, tableOptions, {
                    ajax: {
                        url: options.data.licences.ajax.url,
                        data: function (d) {
                            // add filters to the query
                            if ($(options.selectors.licencesFilterForm)) {
                                d.filters = $(options.selectors.licencesFilterForm).serializeArray();
                            }
                        },
                        dataSrc: function (data) {
                            // intercept the returned data to display (console) error if any.
                            if (data['error']) {
                                window.console.error('Licences error:', data['error']);
                            }
                            return data['data'] || [];
                        },
                        error: function (xhr, textStatus, thrownError) {
                            window.console.log('Error while loading licences data:',
                                thrownError, textStatus, xhr.responseText, xhr.status);
                            //Stop the data table 'Processing'.
                            $(options.selectors.licencesTable + '_processing').hide();
                        },
                        complete: function () {
                            // Trick. Set the url for the bulk renewal. The bulk renewal View uses the same parameters
                            // for filtering than the server side licence datatable. Using these parameters will
                            // ensure consistency between the table result and the bulk renewal.
                            var $button = $(options.selectors.licencesBulkRenewalsButton),
                                url,
                                params;
                            if ($button && $button.length) {
                                url = options.data.licences.bulkRenewalURL;
                                params = this.url.split('?', 2);
                                if (params.length > 1) {
                                    url += '?' + params[1];
                                }
                                $button.attr('href', url);
                            }
                        }
                    }
                }),
                licencesColumns = options.data.licences.columnDefinitions;

            if (options.data.licences.tableOptions) {
                $.extend(licencesTableOptions, options.data.licences.tableOptions);
            }

            licencesTable = dt.initTable(
                options.selectors.licencesTable,
                licencesTableOptions,
                licencesColumns
            );
        }

        function initLicencesFilters() {
            var data = options.data,
                optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                date,
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            function resetFilters() {
                $licencesLicenceTypeFilter.prop('selectedIndex', 0).select2();
                $licencesStatusFilter.prop('selectedIndex', 0).select2();
                $licencesExpireAfterFilter.data('DateTimePicker').clear();
                $licencesExpireBeforeFilter.data('DateTimePicker').clear();
                if (licencesTable) {
                    licencesTable.search('').ajax.reload();
                }
            }

            // licence type
            if ($licencesLicenceTypeFilter && $licencesLicenceTypeFilter.length && data.licences.filters.licence_type) {
                _.forEach(data.licences.filters.licence_type.values, function (value) {

                    $node = createOptionNode(value);
                    $licencesLicenceTypeFilter.append($node);
                });
                if (data.licences.filters.licence_type.selected) {
                    $licencesLicenceTypeFilter.val(data.licences.filters.licence_type.selected);
                }
                $licencesLicenceTypeFilter.on('change', function () {
                    if (licencesTable) {
                        licencesTable.ajax.reload();
                    }
                });
            }
            // status drop down
            if ($licencesStatusFilter && $licencesStatusFilter.length && data.licences.filters.status) {
                _.forEach(data.licences.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $licencesStatusFilter.append($node);
                });
                if (data.licences.filters.status.selected) {
                    $licencesStatusFilter.val(data.licences.filters.status.selected);
                }
                $licencesStatusFilter.on('change', function () {
                    if (licencesTable) {
                        licencesTable.ajax.reload();
                    }
                });
            }
            // expiry dates
            if ($licencesExpireAfterFilter && $licencesExpireAfterFilter.length) {
                $licencesExpireAfterFilter.datetimepicker({
                    format: dateFormat
                });
                if (data.licences.filters.expiry_after.selected) {
                    date = moment(data.licences.filters.expiry_after.selected, dateFormat);
                    $licencesExpireAfterFilter.data('DateTimePicker').date(date);
                }
                $licencesExpireAfterFilter.on('dp.change', function () {
                    if (licencesTable) {
                        licencesTable.ajax.reload();
                    }
                });
            }
            if ($licencesExpireBeforeFilter && $licencesExpireBeforeFilter.length) {
                $licencesExpireBeforeFilter.datetimepicker({
                    format: dateFormat
                });
                if (data.licences.filters.expiry_before.selected) {
                    date = moment(data.licences.filters.expiry_before.selected, dateFormat);
                    $licencesExpireBeforeFilter.data('DateTimePicker').date(date);
                }
                $licencesExpireBeforeFilter.on('dp.change', function () {
                    if (licencesTable) {
                        licencesTable.ajax.reload();
                    }
                });
            }
            if ($licencesResetFilterButton.length) {
                $licencesResetFilterButton.on('click', function () {
                    resetFilters();
                });
            }
        }

        function initReturnsTable() {
            var returnsTableOptions = $.extend({}, tableOptions, {
                    ajax: {
                        url: options.data.returns.ajax.url,
                        dataSrc: function (data) {
                            // intercept the returned data to display (console) error if any.
                            if (data['error']) {
                                window.console.error('Returns error:', data['error']);
                            }
                            return data['data'] || [];
                        },
                        data: function (d) {
                            // add filters to the query
                            if ($(options.selectors.returnsFilterForm)) {
                                d.filters = $(options.selectors.returnsFilterForm).serializeArray();
                            }
                        },
                        error: function (xhr, textStatus, thrownError) {
                            //Stop the data table 'Processing'.
                            window.console.log('Error while loading returns data:',
                                thrownError, textStatus, xhr.responseText, xhr.status);
                            $(options.selectors.returnsTable + '_processing').hide();
                        }
                    }
                }),
                returnsColumns = options.data.returns.columnDefinitions;

            if (options.data.returns.tableOptions) {
                $.extend(returnsTableOptions, options.data.returns.tableOptions);
            }

            returnsTable = dt.initTable(
                options.selectors.returnsTable,
                returnsTableOptions,
                returnsColumns
            );
        }

        function initReturnsFilters() {
            var data = options.data,
                optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            function resetFilters() {
                $returnsLicenceTypeFilter.prop('selectedIndex', 0).select2();
                $returnsStatusFilter.prop('selectedIndex', 0).select2();
                if (returnsTable) {
                    returnsTable.search('').ajax.reload();
                }
            }

            // licence type
            if ($returnsLicenceTypeFilter && $returnsLicenceTypeFilter.length && data.returns.filters.licence_type) {
                _.forEach(data.returns.filters.licence_type.values, function (value) {

                    $node = createOptionNode(value);
                    $returnsLicenceTypeFilter.append($node);
                });
                if (data.returns.filters.licence_type.selected) {
                    $returnsLicenceTypeFilter.val(data.returns.filters.licence_type.selected);
                }
                $returnsLicenceTypeFilter.on('change', function () {
                    if (returnsTable) {
                        returnsTable.ajax.reload();
                    }
                });
            }
            // status drop down
            if ($returnsStatusFilter && $returnsStatusFilter.length && data.returns.filters.status) {
                _.forEach(data.returns.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $returnsStatusFilter.append($node);
                });
                if (data.returns.filters.status.selected) {
                    $returnsStatusFilter.val(data.returns.filters.status.selected);
                }
                $returnsStatusFilter.on('change', function () {
                    if (returnsTable) {
                        returnsTable.ajax.reload();
                    }
                });
            }
            if ($returnsResetFilterButton.length) {
                $returnsResetFilterButton.on('click', function () {
                    resetFilters();
                });
            }
        }

        function showTable(table) {
            if (table === 'applications') {
                $(options.selectors.applicationsAccordion).collapse('show');
                $(options.selectors.licencesAccordion).collapse('hide');
                $(options.selectors.returnsAccordion).collapse('hide');
            } else if (table === 'licences') {
                $(options.selectors.applicationsAccordion).collapse('hide');
                $(options.selectors.licencesAccordion).collapse('show');
                $(options.selectors.returnsAccordion).collapse('hide');
            } else if (table === 'returns') {
                $(options.selectors.applicationsAccordion).collapse('hide');
                $(options.selectors.licencesAccordion).collapse('hide');
                $(options.selectors.returnsAccordion).collapse('show');
            } else if (table === 'none') {
                $(options.selectors.applicationsAccordion).collapse('hide');
                $(options.selectors.licencesAccordion).collapse('hide');
                $(options.selectors.returnsAccordion).collapse('hide');
            } else {
                $(options.selectors.applicationsAccordion).collapse('show');
                $(options.selectors.licencesAccordion).collapse('show');
                $(options.selectors.returnsAccordion).collapse('show');
            }
        }

        function setFilters(query) {
            /**
             * @param query.application_licence_type
             * @param query.application_status
             * @param query.application_assignee
             */
            function setApplicationsFilters(query) {
                var $collapse = $('#applications-collapse');
                if (query.application_licence_type) {
                    $collapse.collapse('show');
                    $applicationsLicenceTypeFilter.val(query.application_licence_type);
                }
                if (query.application_status) {
                    $collapse.collapse('show');
                    $applicationsStatusFilter.val(query.application_status);
                }
                if (query.application_assignee) {
                    $applicationsAssigneeFilter.val(query.application_assignee);
                }
            }

            /**
             * @param query.licence_licence_type
             * @param query.licence_status
             * @param query.licence_assignee
             * @param query.licence_expiry_after
             * @param query.licence_expiry_before
             */
            function setLicencesFilters(query) {
                var $collapse = $('#licences-collapse'),
                    date;
                if (query.licence_licence_type) {
                    $collapse.collapse('show');
                    $licencesLicenceTypeFilter.val(query.licence_licence_type);
                }
                if (query.licence_status) {
                    $collapse.collapse('show');
                    $licencesStatusFilter.val(query.licence_status);
                }
                if (query.licence_expiry_after) {
                    date = moment(query.licence_expiry_after, dateFormat);
                    $licencesExpireAfterFilter.data('DateTimePicker').date(date);
                }
                if (query.licence_expiry_before) {
                    date = moment(query.licence_expiry_before, dateFormat);
                    $licencesExpireBeforeFilter.data('DateTimePicker').date(date);
                }
            }

            /**
             * @param query.return_licence_type
             * @param query.return_status
             */
            function setReturnsFilters(query) {
                var $collapse = $('#returns-collapse');

                if (query.return_licence_type) {
                    $collapse.collapse('show');
                    $returnsLicenceTypeFilter.val(query.return_licence_type);
                }
                if (query.return_status) {
                    $collapse.collapse('show');
                    $returnsStatusFilter.val(query.return_status);
                }
            }

            setApplicationsFilters(query);
            setLicencesFilters(query);
            setReturnsFilters(query);
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    applicationsTable: '#applications-table',
                    applicationsAccordion: '#applications-collapse',
                    applicationsFilterForm: '#applications-filter-form',
                    applicationsLicenceTypeFilter: '#applications-filter-licence-type',
                    applicationsStatusFilter: '#applications-filter-status',
                    applicationsAssigneeFilter: '#applications-filter-assignee',
                    applicationsResetFilterButton: '#reset-applications-filter-button',

                    licencesTable: '#licences-table',
                    licencesAccordion: '#licences-collapse',
                    licencesFilterForm: '#licences-filter-form',
                    licencesLicenceTypeFilter: '#licences-filter-licence-type',
                    licencesStatusFilter: '#licences-filter-status',
                    licencesExpireAfterFilter: '#licences-filter-expiry-after-date',
                    licencesExpireBeforeFilter: '#licences-filter-expiry-before-date',
                    licencesBulkRenewalsButton: '#licences-bulk-renewals',
                    licencesResetFilterButton: '#reset-licences-filter-button',

                    returnsTable: '#returns-table',
                    returnsAccordion: '#returns-collapse',
                    returnsFilterForm: '#returns-filter-form',
                    returnsLicenceTypeFilter: '#returns-filter-licence-type',
                    returnsStatusFilter: '#returns-filter-status',
                    returnsResetFilterButton: '#reset-returns-filter-button'
                },
                data: {
                    'applications': {
                        ajax: {
                            url: '/dashboard/data/applications'
                        },
                        'columnDefinitions': [],
                        'filters': {}
                    }
                }
            };
            // merge the defaults options, and the options passed in parameter.
            // This is a deep merge but the array are not merged
            options = _.mergeWith({}, defaults, moduleOptions, function (objValue, srcValue) {
                if (_.isArray(objValue)) {
                    return srcValue;
                }
            });
            $(function () {
                $applicationsLicenceTypeFilter = $(options.selectors.applicationsLicenceTypeFilter);
                $applicationsStatusFilter = $(options.selectors.applicationsStatusFilter);
                $applicationsAssigneeFilter = $(options.selectors.applicationsAssigneeFilter);
                $applicationsResetFilterButton = $(options.selectors.applicationsResetFilterButton);

                $licencesLicenceTypeFilter = $(options.selectors.licencesLicenceTypeFilter);
                $licencesStatusFilter = $(options.selectors.licencesStatusFilter);
                $licencesExpireAfterFilter = $(options.selectors.licencesExpireAfterFilter);
                $licencesExpireBeforeFilter = $(options.selectors.licencesExpireBeforeFilter);
                $licencesResetFilterButton = $(options.selectors.licencesResetFilterButton);

                $returnsLicenceTypeFilter = $(options.selectors.returnsLicenceTypeFilter);
                $returnsStatusFilter = $(options.selectors.returnsStatusFilter);
                $returnsResetFilterButton = $(options.selectors.returnsResetFilterButton);

                // show a specific table?
                showTable(_.get(options, 'data.query.show', 'all'));

                // filters need to be init and set before the tables
                initFilters();
                if (options.data.query) {
                    // set filter according to query data
                    setFilters(options.data.query);
                }
                initTables();
                $applicationsResetFilterButton.removeClass('hidden');
                $licencesResetFilterButton.removeClass('hidden');
                $returnsResetFilterButton.removeClass('hidden');

                // apply the bootstrap select2 to the filters.
                $(options.selectors.applicationsFilterForm + ' select').select2();
                $(options.selectors.licencesFilterForm + ' select').select2();
                $(options.selectors.returnsFilterForm + ' select').select2();
            });
        };
    }
);
