define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'bootstrap',
        'select2',
        'bootstrap-datetimepicker'
    ],
    function ($, _, dt) {
        "use strict";

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
            applicationsTable,
            licencesTable,
            returnsTable,
            $applicationsLicenceTypeFilter,
            $applicationsStatusTypeFilter,
            $applicationsAssigneeTypeFilter,
            $applicationResetFilterButton,

            $licencesLicenceTypeFilter,
            $licencesStatusFilter,
            $licencesExpireAfterFilter,
            $licencesExpireBeforeFilter,
            $returnsLicenceTypeFilter,
            $returnsStatusTypeFilter;

        function initFilters() {
            initApplicationsFilters();
            initLicencesFilters();
            initReturnsFilters();
        }

        function initTables() {
            if (options.data.applications) {
                initApplicationsTable();
            }
            if (options.data.licences) {
                initLicenceTable();
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
                        error: function (xhr, textStatus, thrownError) {
                            console.log("Error while loading applications data:", thrownError, textStatus, xhr.responseText, xhr.status);
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

            // licence type
            if ($applicationsLicenceTypeFilter.length && data.applications.filters.licenceType) {
                _.forEach(data.applications.filters.licenceType.values, function (value) {

                    $node = createOptionNode(value);
                    $applicationsLicenceTypeFilter.append($node);
                });
                $applicationsLicenceTypeFilter.on('change', function () {
                    applicationsTable.ajax.reload();
                });
            }
            // status
            if ($applicationsStatusTypeFilter.length && data.applications.filters.status) {
                _.forEach(data.applications.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsStatusTypeFilter.append($node);
                });
                $applicationsStatusTypeFilter.on('change', function () {
                    applicationsTable.ajax.reload();
                });
            }
            // assignee filter
            if ($applicationsAssigneeTypeFilter.length && data.applications.filters.assignee) {
                _.forEach(data.applications.filters.assignee.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsAssigneeTypeFilter.append($node);
                });
                $applicationsAssigneeTypeFilter.on('change', function () {
                    applicationsTable.ajax.reload();
                });
            }

            if ($applicationResetFilterButton.length) {
                $applicationResetFilterButton.on('click', function () {
                    resetApplicationsFilters();
                });
            }
        }

        /**
         *
         * @param filters.licenceType
         * @param filters.status
         * @param filters.assignee
         * @param filters.search
         */
        function setApplicationFilters(filters) {
            $('#applications-collapse').collapse('show');
            if (filters.licenceType) {
                $applicationsLicenceTypeFilter.val(filters.licenceType).select2();
            }
            if (filters.status) {
                $applicationsStatusTypeFilter.val(filters.status).select2();
            }
            if (filters.assignee) {
                $applicationsAssigneeTypeFilter.val(filters.assignee).select2();
            }
        }

        function resetApplicationsFilters() {
            $applicationsLicenceTypeFilter.prop('selectedIndex', 0).select2();
            $applicationsStatusTypeFilter.prop('selectedIndex', 0).select2();
            $applicationsAssigneeTypeFilter.prop('selectedIndex', 0).select2();
            applicationsTable.search('').ajax.reload();
        }

        function initLicenceTable() {
            var licencesTableOptions = $.extend({order: [[0, 'desc']]}, tableOptions, {
                    ajax: {
                        url: options.data.licences.ajax.url,
                        data: function (d) {
                            // add filters to the query
                            if ($(options.selectors.licencesFilterForm)) {
                                d.filters = $(options.selectors.licencesFilterForm).serializeArray();
                            }
                        },
                        error: function (xhr, textStatus, thrownError) {
                            console.log("Error while loading licences data:", thrownError, textStatus, xhr.responseText, xhr.status);
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
                                if (params.length > 1){
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
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            // licence type
            if ($licencesLicenceTypeFilter && $licencesLicenceTypeFilter.length && data.licences.filters.licenceType) {
                _.forEach(data.licences.filters.licenceType.values, function (value) {

                    $node = createOptionNode(value);
                    $licencesLicenceTypeFilter.append($node);
                });
                $licencesLicenceTypeFilter.on('change', function () {
                    licencesTable.ajax.reload();
                });
            }
            // status drop down
            if ($licencesStatusFilter && $licencesStatusFilter.length && data.licences.filters.status) {
                _.forEach(data.licences.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $licencesStatusFilter.append($node);
                });
                $licencesStatusFilter.on('change', function () {
                    licencesTable.ajax.reload();
                });
            }
            // expiry dates
            if ($licencesExpireAfterFilter && $licencesExpireAfterFilter.length) {
                $licencesExpireAfterFilter.datetimepicker({
                    format: 'DD/MM/YYYY'
                });
                $licencesExpireAfterFilter.on('dp.change', function () {
                    licencesTable.ajax.reload();
                });
            }
            if ($licencesExpireBeforeFilter && $licencesExpireBeforeFilter.length) {
                $licencesExpireBeforeFilter.datetimepicker({
                    format: 'DD/MM/YYYY'
                });
                $licencesExpireBeforeFilter.on('dp.change', function () {
                    licencesTable.ajax.reload();
                });
            }
        }

        function initReturnsTable() {
            var returnsTableOptions = $.extend({}, tableOptions, {
                    ajax: {
                        url: options.data.returns.ajax.url,
                        data: function (d) {
                            // add filters to the query
                            if ($(options.selectors.returnsFilterForm)) {
                                d.filters = $(options.selectors.returnsFilterForm).serializeArray();
                            }
                        },
                        error: function (xhr, textStatus, thrownError) {
                            //Stop the data table 'Processing'.
                            console.log("Error while loading returns data:", thrownError, textStatus, xhr.responseText, xhr.status);
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

            // licence type
            if ($returnsLicenceTypeFilter && $returnsLicenceTypeFilter.length && data.returns.filters.licenceType) {
                _.forEach(data.returns.filters.licenceType.values, function (value) {

                    $node = createOptionNode(value);
                    $returnsLicenceTypeFilter.append($node);
                });
                $returnsLicenceTypeFilter.on('change', function () {
                    returnsTable.ajax.reload();
                });
            }
            // status drop down
            if ($returnsStatusTypeFilter && $returnsStatusTypeFilter.length && data.returns.filters.status) {
                _.forEach(data.returns.filters.status.values, function (value) {
                    $node = createOptionNode(value);
                    $returnsStatusTypeFilter.append($node);
                });
                $returnsStatusTypeFilter.on('change', function () {
                    returnsTable.ajax.reload();
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

        /**
         *
         * @param filters.applications
         * @param filters.licences
         * @param filters.returns
         */
        function setFilters(filters) {
            if (filters.applications){
                setApplicationFilters(filters.applications);
            }
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
                    applicationResetFilterButton: '#reset-application-filter-button',

                    licencesTable: '#licences-table',
                    licencesAccordion: '#licences-collapse',
                    licencesFilterForm: '#licences-filter-form',
                    licencesLicenceTypeFilter: '#licences-filter-licence-type',
                    licencesStatusFilter: '#licences-filter-status',
                    licencesExpireAfterFilter: '#licences-filter-expiry-after-date',
                    licencesExpireBeforeFilter: '#licences-filter-expiry-before-date',
                    licencesBulkRenewalsButton: '#licences-bulk-renewals',

                    returnsTable: '#returns-table',
                    returnsAccordion: '#returns-collapse',
                    returnsFilterForm: '#returns-filter-form',
                    returnsLicenceTypeFilter: '#returns-filter-licence-type',
                    returnsStatusFilter: '#returns-filter-status'
                },
                data: {
                    'applications': {
                        ajax: {
                            url: "/dashboard/data/applications"
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
                $applicationsStatusTypeFilter = $(options.selectors.applicationsStatusFilter);
                $applicationsAssigneeTypeFilter = $(options.selectors.applicationsAssigneeFilter);
                $applicationResetFilterButton = $(options.selectors.applicationResetFilterButton);

                $licencesLicenceTypeFilter = $(options.selectors.licencesLicenceTypeFilter);
                $licencesStatusFilter = $(options.selectors.licencesStatusFilter);
                $licencesExpireAfterFilter = $(options.selectors.licencesExpireAfterFilter);
                $licencesExpireBeforeFilter = $(options.selectors.licencesExpireBeforeFilter);

                $returnsLicenceTypeFilter = $(options.selectors.returnsLicenceTypeFilter);
                $returnsStatusTypeFilter = $(options.selectors.returnsStatusFilter);

                // show a specific table?
                showTable(_.get(options, 'data.query.show', 'all'));

                // filters need to be set before the tables
                initFilters();
                if (options.data.filters) {
                    // set filters according to query data
                    setFilters(options.data.filters);
                }
                initTables();

                // apply the bootstrap select2 to the filters.
                $(options.selectors.applicationsFilterForm + ' select').select2();
                $(options.selectors.licencesFilterForm + ' select').select2();
                $(options.selectors.returnsFilterForm + ' select').select2();
            });
        };
    }
);
