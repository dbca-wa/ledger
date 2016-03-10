define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'moment',
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
            applicationsColumns = [
                {
                    title: 'Type',
                    data: 'license_type'
                },
                {
                    title: 'Customer',
                    data: 'customer'
                },
                {
                    title: 'Date',
                    data: 'date',
                    type: 'date'
                },
                {
                    title: 'Status',
                    data: 'status'
                }
            ],
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
            applicationsTable, licensesTable, returnsTable;

        function initTables(options, data) {
            applicationsTable = dt.initTable(
                options.applicationsTableSelector,
                tableOptions,
                applicationsColumns
            );
            applicationsTable.populate(data.applications.tableData);

            licensesTable = dt.initTable(
                options.licensesTableSelector,
                tableOptions,
                licensesColumns
            );
            licensesTable.populate(data.licenses.tableData);

            returnsTable = dt.initTable(
                options.returnsTableSelector,
                tableOptions,
                returnsColumns
            );
            returnsTable.populate(data.returns.tableData);
        }

        function filterTable(filterData) {
            /**
             * {
             *  type: <global|applications>,
             *  column: 'license_type',
             *  value: 'reg3'
             *  filter: function (row) { return true;}
             *  }
             */
            var defaultColumnFilter = function (row) {
                    return filterData.value.toLowerCase() === 'all' ? true : row[filterData.column] === filterData.value;
                },
                filter = defaultColumnFilter;
            if (typeof filterData.filter === 'function') {
                filter = filterData.filter;
            }
            if (data) {
                if (filterData.type === 'global' || filterData.type === 'applications') {
                    applicationsTable.populate(_.filter(data.applications.tableData, filter));
                }
                if (filterData.type === 'global' || filterData.type === 'licenses') {
                    licensesTable.populate(_.filter(data.licenses.tableData, filter));
                }
                if (filterData.type === 'global' || filterData.type === 'returns') {
                    returnsTable.populate(_.filter(data.returns.tableData, filter));
                }
            }
        }

        function initFilters(options, data) {
            var optionTemplate = _.template('<option><%= value %></option>'),
                $applicationsLicenseTypeFilter = $(options.applicationsLicenseFilterSelector),
                $applicationsStatusTypeFilter = $(options.applicationsStatusFilterSelector),
                $licensesLicenseTypeFilter = $(options.licensesLicenseFilterSelector),
                $licensesStatusTypeFilter = $(options.licensesStatusFilterSelector),
                $returnsDueDateFilter = $(options.returnsDueDateFilterSelector),
                $node;

            // applications license type
            _.forEach(data.applications.filters.licenseType.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $applicationsLicenseTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    column: 'license_type',
                    value: value
                });
            });
            $applicationsLicenseTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $applicationsStatusTypeFilter.val('All');
                filterTable(data)
            });
            // applications status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $applicationsStatusTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    column: 'status',
                    value: value
                });
            });
            $applicationsStatusTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $applicationsLicenseTypeFilter.val('All');
                filterTable(data)
            });

            // applications license type
            _.forEach(data.licenses.filters.licenseType.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $licensesLicenseTypeFilter.append($node);
                $node.data({
                    type: 'licenses',
                    column: 'license_type',
                    value: value
                });
            });
            $licensesLicenseTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $licensesStatusTypeFilter.val('All');
                filterTable(data)
            });
            // licenses status
            _.forEach(data.licenses.filters.status.values, function (value) {
                $node = $(optionTemplate({value: value}));
                $licensesStatusTypeFilter.append($node);
                $node.data({
                    type: 'licenses',
                    column: 'status',
                    value: value
                });
            });
            $licensesStatusTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $licensesLicenseTypeFilter.val('All');
                filterTable(data)
            });

            // returns due date filter
            $node = $(optionTemplate({value: 'All'}));
            $node.data({
                type: 'returns',
                column: 'due_date',
                value: 'all'
            });
            $returnsDueDateFilter.append($node);

            $node = $(optionTemplate({value: 'Overdue'}));
            $node.data({
                type: 'returns',
                filter: function (row) {
                    var now = moment();
                    return moment(row['due_date']).isBefore(now);
                }
            });
            $returnsDueDateFilter.append($node);
            $returnsDueDateFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                filterTable(data);
            });

            // necessary when option added dynamically
            $('.selectpicker').selectpicker('refresh');
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
                returnsDueDateFilterSelector: '#returns-filter-dueDate',
                data: {
                    'applications': {
                        'tableData': [],
                        'collapsed': false,
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
                        'collapsed': false,
                        'filters': {
                            'licenseType': {
                                'values': ['All'],
                                'selected': 'All'
                            }
                        }
                    },
                    'returns': {
                        'tableData': [],
                        'collapsed': false,
                        'filters': {
                            'licenseType': {
                                'values': ['All'],
                                'selected': 'All'
                            },
                            'dueDate': {
                                'values': ['All', 'Overdue'],
                                'selected': 'All'
                            }
                        }
                    }
                }
            };
            options = $.extend({}, defaults, options);
            $(function () {
                $('.selectpicker').selectpicker();
                data = options.data;
                initTables(options, data);
                initFilters(options, data);
            })
        };
    }
);
