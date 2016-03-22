define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'moment',
        'bootstrap',
        'bootstrap.select'
    ],
    function ($, _, dt, moment) {
        var tableOptions = {
                paging: true,
                info: true,
                searching: true,
                scrollCollapse: true,
                processing: true,
                deferRender: true,
                autowidth: true

            },
            licensesColumns = [
                {
                    title: 'License #',
                    data: 'license_no'
                },
                {
                    title: 'Type',
                    data: 'license_type'
                },
                {
                    title: 'Customer',
                    data: 'customer'
                },
                {
                    title: 'Issue Date',
                    data: 'issue_date'
                },
                {
                    title: 'Expire Date',
                    data: 'expire_date'
                },
                {
                    title: 'Status',
                    data: 'status'
                }
            ],
            returnsColumns = [
                {
                    title: 'License #',
                    data: 'license_no'
                },
                {
                    title: 'Type',
                    data: 'license_type'
                },
                {
                    title: 'Customer',
                    data: 'customer'
                },
                {
                    title: 'Due Date',
                    data: 'due_date'
                },
                {
                    title: 'Status',
                    data: 'status'
                }
            ],
            data,
            applicationsTable, licensesTable, returnsTable,
            $applicationsLicenseTypeFilter,
            $applicationsStatusTypeFilter,
            $licensesLicenseTypeFilter,
            $licensesStatusTypeFilter,
            $returnsDueDateFilter,
            $returnsLicenseTypeFilter;

        function initTables(options) {
            var applicationTableOptions = $.extend({}, tableOptions, {
                    serverSide: true,
                    ajax: {
                        url: options.ajax.applications,
                        error: function () {
                            console.log("error");
                            //TODO Stop the data table 'Processing' and show an error.
                        }
                    }
                }),
                applicationsColumns = [
                    //{
                    //    title: 'Type',
                    //    data: 'license_type'
                    //},
                    //{
                    //    title: 'Customer',
                    //    data: 'customer'
                    //},
                    //{
                    //    title: 'Date',
                    //    data: 'date',
                    //    type: 'date'
                    //},
                    {
                        title: 'Status'
                    }
                ];

            applicationsTable = dt.initTable(
                options.applicationsTableSelector,
                applicationTableOptions,
                applicationsColumns
            ).yadcf([
                {
                    column_number: 0
                }
            ]);

            licensesTable = dt.initTable(
                options.licensesTableSelector,
                tableOptions,
                licensesColumns
            );
            filterLicenses();

            returnsTable = dt.initTable(
                options.returnsTableSelector,
                tableOptions,
                returnsColumns
            );
            filterReturns();
        }

        function filterTable(table, filters) {
            function andFilter(filters) {
                return function (row) {
                    for (var i = 0; i < filters.length; i++) {
                        if (!filters[i](row)) {
                            return false;
                        }
                    }
                    return true;
                }
            }

            if (table === 'applications') {
                applicationsTable.populate(_.filter(data.applications.tableData, andFilter(filters)));
            }
            if (table === 'licenses') {
                licensesTable.populate(_.filter(data.licenses.tableData, andFilter(filters)));
            }
            if (table === 'returns') {
                returnsTable.populate(_.filter(data.returns.tableData, andFilter(filters)));
            }

        }

        function filterApplications() {
            filterTable('applications', [
                $applicationsLicenseTypeFilter.find(':selected').data().filter,
                $applicationsStatusTypeFilter.find(':selected').data().filter
            ]);
        }

        function filterLicenses() {
            filterTable('licenses', [
                $licensesLicenseTypeFilter.find(':selected').data().filter,
                $licensesStatusTypeFilter.find(':selected').data().filter
            ]);
        }

        function filterReturns() {
            filterTable('returns', [
                $returnsLicenseTypeFilter.find(':selected').data().filter,
                $returnsDueDateFilter.find(':selected').data().filter
            ]);
        }

        function initFilters(data) {
            var optionTemplate = _.template('<option><%= value %></option>'),
                $node;

            // applications license type
            _.forEach(data.applications.filters.licenseType.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $applicationsLicenseTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    filter: function (row) {
                        return value.toLowerCase() === 'all' ? true : row['license_type'] === value;
                    }
                });
            });
            $applicationsLicenseTypeFilter.on('change', function () {
                filterApplications();
            });
            // applications status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $applicationsStatusTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    filter: function (row) {
                        return value.toLowerCase() === 'all' ? true : row['status'] === value;
                    }
                });
            });
            $applicationsStatusTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                filterApplications(data);
            });

            // licenses license type
            _.forEach(data.licenses.filters.licenseType.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $licensesLicenseTypeFilter.append($node);
                $node.data({
                    type: 'licenses',
                    filter: function (row) {
                        return value.toLowerCase() === 'all' ? true : row['license_type'] === value;
                    }
                });
            });
            $licensesLicenseTypeFilter.on('change', function () {
                filterLicenses(data);
            });
            // licenses status
            _.forEach(data.licenses.filters.status.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $licensesStatusTypeFilter.append($node);
                $node.data({
                    type: 'licenses',
                    filter: function (row) {
                        return value.toLowerCase() === 'all' ? true : row['status'] === value;
                    }
                });
            });
            $licensesStatusTypeFilter.on('change', function () {
                filterLicenses();
            });

            // returns license type
            _.forEach(data.returns.filters.licenseType.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $returnsLicenseTypeFilter.append($node);
                $node.data({
                    type: 'returns',
                    filter: function (row) {
                        return value.toLowerCase() === 'all' ? true : row['license_type'] === value;
                    }
                });
            });
            $returnsLicenseTypeFilter.on('change', function () {
                filterReturns()
            });
            // returns due date filter
            $node = $(optionTemplate({value: 'All'}));
            $node.data({
                type: 'returns',
                filter: function () {
                    return true;
                }
            });
            $returnsDueDateFilter.append($node);

            $node = $(optionTemplate({value: 'overdue'}));
            $node.data({
                type: 'returns',
                filter: function (row) {
                    var now = moment();
                    return row['status'] === 'pending' && moment(row['due_date']).isBefore(now);
                }
            });
            $returnsDueDateFilter.append($node);
            $returnsDueDateFilter.on('change', function () {
                filterReturns();
            });

            // necessary when option added dynamically
            $('.selectpicker').selectpicker('refresh');

        }

        function setFilters(data) {
            if (data.model) {
                if (data.model === 'application') {
                    $('#applications-collapse').collapse('show');
                    $('#licenses-collapse').collapse('hide');
                    $('#returns-collapse').collapse('hide');
                    if (data.status) {
                        $applicationsStatusTypeFilter.val(data.status);
                    }
                    if (data.license_type) {
                        $applicationsLicenseTypeFilter.val(data.license_type);
                    }
                }
                if (data.model === 'license') {
                    $('#applications-collapse').collapse('hide');
                    $('#licenses-collapse').collapse('show');
                    $('#returns-collapse').collapse('hide');
                    if (data.status) {
                        $licensesStatusTypeFilter.val(data.status);
                    }
                    if (data.license_type) {
                        $licensesLicenseTypeFilter.val(data.license_type);
                    }
                }
                if (data.model === 'return') {
                    $('#applications-collapse').collapse('hide');
                    $('#licenses-collapse').collapse('hide');
                    $('#returns-collapse').collapse('show');
                    if (data.due_date) {
                        $returnsDueDateFilter.val(data.due_date);
                    }
                    if (data.license_type) {
                        $returnsLicenseTypeFilter.val(data.license_type);
                    }
                }
            }

        }

        return function (options) {
            var defaults = {
                applicationsTableSelector: '#applications-table',
                licensesTableSelector: '#licenses-table',
                returnsTableSelector: '#returns-table',

                applicationsLicenseFilterSelector: '#applications-filter-license-type',
                applicationsStatusFilterSelector: '#applications-filter-status',

                licensesLicenseFilterSelector: '#licenses-filter-license-type',
                licensesStatusFilterSelector: '#licenses-filter-status',

                returnsLicenseFilterSelector: '#returns-filter-license-type',
                returnsDueDateFilterSelector: '#returns-filter-dueDate',
                ajax: {
                    applications: "/dashboard/data/applications"
                },
                data: {
                    'applications': {
                        'tableData': [],
                        'filters': {
                            'licenseType': {
                                'values': ['All'],
                                'selected': 'All'
                            },
                            'status': {
                                'values': ['All'],
                                'selected': 'All'
                            }
                        }
                    },
                    'licenses': {
                        'tableData': [],
                        'filters': {
                            'licenseType': {
                                'values': ['All'],
                                'selected': 'All'
                            }
                        }
                    },
                    'returns': {
                        'tableData': [],
                        'filters': {
                            'licenseType': {
                                'values': ['All'],
                                'selected': 'All'
                            },
                            'dueDate': {
                                'values': ['All', 'overdue'],
                                'selected': 'All'
                            }
                        }
                    }
                }
            };
            options = $.extend({}, defaults, options);
            $(function () {
                data = options.data;
                $applicationsLicenseTypeFilter = $(options.applicationsLicenseFilterSelector);
                $applicationsStatusTypeFilter = $(options.applicationsStatusFilterSelector);
                $licensesLicenseTypeFilter = $(options.licensesLicenseFilterSelector);
                $licensesStatusTypeFilter = $(options.licensesStatusFilterSelector);
                $returnsDueDateFilter = $(options.returnsDueDateFilterSelector);
                $returnsLicenseTypeFilter = $(options.returnsLicenseFilterSelector);

                initFilters(data);
                if (data.query) {
                    // set filter according to query data
                    setFilters(data.query);
                }
                initTables(options, data);
            })
        };
    }
);
