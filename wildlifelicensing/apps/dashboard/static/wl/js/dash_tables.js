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
                serverside: true,
                autowidth: true

            },
            licencesColumns = [
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
            applicationsTable, licencesTable, returnsTable,
            $applicationsLicenseTypeFilter,
            $applicationsStatusTypeFilter,
            $licencesLicenseTypeFilter,
            $licencesStatusTypeFilter,
            $returnsDueDateFilter,
            $returnsLicenseTypeFilter;

        function initTables(options) {
            var applicationTableOptions = $.extend({}, tableOptions, {
                    ajax: {
                        url: options.ajax.applications,
                        error: function () {
                            console.log("error");
                            //TODO Stop the data table 'Processing' and show an error.
                        }
                    }
                }),
                applicationsColumns = [
                    {
                        title: 'License Type'
                    },
                    {
                        title: 'Applicant'
                    },
                    {
                        title: 'Status'
                    }
                ];

            applicationsTable = dt.initTable(
                options.applicationsTableSelector,
                applicationTableOptions,
                applicationsColumns
            );

            licencesTable = dt.initTable(
                options.licencesTableSelector,
                tableOptions,
                licencesColumns
            );
            filterLicenses();

            returnsTable = dt.initTable(
                options.returnsTableSelector,
                tableOptions,
                returnsColumns
            );
            filterReturns();
        }

        function filterApplications() {
        }

        function filterLicenses() {
        }

        function filterReturns() {
        }

        function initFilters(data) {
            var optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            // applications license type
            _.forEach(data.applications.filters.licenseType.values, function (value) {

                $node = createOptionNode(value);
                $applicationsLicenseTypeFilter.append($node);
            });
            $applicationsLicenseTypeFilter.on('change', function () {
                filterApplications();
            });
            // applications status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = createOptionNode(value);
                $applicationsStatusTypeFilter.append($node);
            });
            $applicationsStatusTypeFilter.on('change', function (event) {
                filterApplications();
            });

            // licences
            _.forEach(data.licences.filters.licenseType.values, function (value) {
                $node = createOptionNode(value);
                $licencesLicenseTypeFilter.append($node);
            });
            $licencesLicenseTypeFilter.on('change', function () {
                filterLicenses();
            });
            // licences status
            _.forEach(data.licences.filters.status.values, function (value) {
                $node = createOptionNode(value);
                $licencesStatusTypeFilter.append($node);
            });
            $licencesStatusTypeFilter.on('change', function () {
                filterLicenses();
            });

            // returns license type
            _.forEach(data.returns.filters.licenseType.values, function (value) {
                $node = createOptionNode(value);
                $returnsLicenseTypeFilter.append($node);
            });
            $returnsLicenseTypeFilter.on('change', function () {
                filterReturns()
            });
            // returns due date filter
            _.forEach(data.returns.filters.dueDate.values, function (value) {
                $node = createOptionNode(value);
                $returnsDueDateFilter.append($node);
            });
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
                    $('#licences-collapse').collapse('hide');
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
                    $('#licences-collapse').collapse('show');
                    $('#returns-collapse').collapse('hide');
                    if (data.status) {
                        $licencesStatusTypeFilter.val(data.status);
                    }
                    if (data.license_type) {
                        $licencesLicenseTypeFilter.val(data.license_type);
                    }
                }
                if (data.model === 'return') {
                    $('#applications-collapse').collapse('hide');
                    $('#licences-collapse').collapse('hide');
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
                licencesTableSelector: '#licences-table',
                returnsTableSelector: '#returns-table',

                applicationsLicenseFilterSelector: '#applications-filter-license-type',
                applicationsStatusFilterSelector: '#applications-filter-status',

                licencesLicenseFilterSelector: '#licences-filter-license-type',
                licencesStatusFilterSelector: '#licences-filter-status',

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
                    'licences': {
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
                $licencesLicenseTypeFilter = $(options.licencesLicenseFilterSelector);
                $licencesStatusTypeFilter = $(options.licencesStatusFilterSelector);
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
