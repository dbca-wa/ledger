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
            mockData = {
                dates: ['2016-01-01', '2015-12-11', '2015-04-04', '2015-01-30', '2017-12-24'],
                customers: ['Serge Le Breton', 'Pauline Goodreid', 'Paul Gioia', 'Graham Thompson', 'Tony Prior'],
                statusApplication: ['pending', 'draft', 'issued'],
                licenseTypes: ['reg3', 'reg17', 'reg40', 'reg666'],
                statusLicense: ['submitted', 'granted', 'refused', 'cancelled']
            },
            tableData,
            applicationsTable, licensesTable, returnsTable;

        function generateData() {
            // generate rows from randomly picking values from the mockData
            var nbRows = 30,
                result = {};

            result.applications = (_.times(nbRows, function () {
                return {
                    license_type: _.sample(mockData.licenseTypes),
                    customer: _.sample(mockData.customers),
                    date: _.sample(mockData.dates),
                    status: _.sample(mockData.statusApplication)
                }
            }));

            result.licenses = (_.times(nbRows, function () {
                var row = {
                    license_type: _.sample(mockData.licenseTypes),
                    customer: _.sample(mockData.customers),
                    issue_date: _.sample(mockData.dates),
                    expire_date: _.sample(mockData.dates),
                    status: _.sample(mockData.statusLicense)
                };
                row.license_no = row.license_type + '-' + _.random(1, 100);
                return row;
            }));

            result.returns = (_.times(nbRows, function () {
                var row = {
                    license_type: _.sample(mockData.licenseTypes),
                    customer: _.sample(mockData.customers),
                    due_date: _.sample(mockData.dates),
                    status: _.sample(mockData.statusApplication)
                };
                row.license_no = row.license_type + '-' + _.random(1, 100);
                return row;
            }));
            return result;
        }

        function initTables(options, data) {
            applicationsTable = dt.initTable(
                options.applicationsTableSelector,
                tableOptions,
                applicationsColumns
            );
            applicationsTable.populate(data.applications);

            licensesTable = dt.initTable(
                options.licensesTableSelector,
                tableOptions,
                licensesColumns
            );
            licensesTable.populate(data.licenses);

            returnsTable = dt.initTable(
                options.returnsTableSelector,
                tableOptions,
                returnsColumns
            );
            returnsTable.populate(data.returns);
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
                    return filterData.value === 'all' ? true : row[filterData.column] === filterData.value;
                },
                filter = defaultColumnFilter;
            if (typeof filterData.filter === 'function') {
                filter = filterData.filter;
            }
            if (tableData) {
                if (filterData.type === 'global' || filterData.type === 'applications') {
                    applicationsTable.populate(_.filter(tableData.applications, filter));
                }
                if (filterData.type === 'global' || filterData.type === 'licenses') {
                    licensesTable.populate(_.filter(tableData.licenses, filter));
                }
                if (filterData.type === 'global' || filterData.type === 'returns') {
                    returnsTable.populate(_.filter(tableData.returns, filter));
                }
            }
        }

        function initFilters(options, data) {
            var itemTemplate = _.template('<option><%= title %></option>'),
                $globalLicenseTypeFilter = $(options.globalLicenseTypeFilterSelector),
                $appsLicenseTypeFilter = $(options.applicationsLicenseFilterSelector),
                $appsStatusTypeFilter = $(options.applicationsStatusFilterSelector),
                $returnsDuedateFilter = $(options.returnsDueDateFilterSelector),
                $node;

            //global license type filter
            $node = $(itemTemplate({title: 'All'}));
            $globalLicenseTypeFilter.append($node);
            $node.data({
                type: 'global',
                column: 'license_type',
                value: 'all'
            });
            _.forEach(mockData.licenseTypes, function (type) {
                $node = $(itemTemplate({title: type}));
                $globalLicenseTypeFilter.append($node);
                $node.data({
                    type: 'global',
                    column: 'license_type',
                    value: type
                });
            });
            $globalLicenseTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                filterTable(data)
            });

            // applications license type
            $node = $(itemTemplate({title: 'All'}));
            $appsLicenseTypeFilter.append($node);
            $node.data({
                type: 'applications',
                column: 'license_type',
                value: 'all'
            });
            _.forEach(mockData.licenseTypes, function (type) {
                $node = $(itemTemplate({title: type}));
                $appsLicenseTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    column: 'license_type',
                    value: type
                });
            });
            $appsLicenseTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $appsStatusTypeFilter.val('All');
                filterTable(data)
            });

            // applications status
            $node = $(itemTemplate({title: 'All'}));
            $appsStatusTypeFilter.append($node);
            $node.data({
                type: 'applications',
                column: 'status',
                value: 'all'
            });
            _.forEach(mockData.statusApplication, function (status) {
                $node = $(itemTemplate({title: status}));
                $appsStatusTypeFilter.append($node);
                $node.data({
                    type: 'applications',
                    column: 'status',
                    value: status
                });
            });
            $appsStatusTypeFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                $appsLicenseTypeFilter.val('All');
                filterTable(data)
            });

            // returns due date filter
            $node = $(itemTemplate({title: 'All'}));
            $node.data({
                type: 'returns',
                column: 'due_date',
                value: 'all'
            });
            $returnsDuedateFilter.append($node);

            $node = $(itemTemplate({title: 'Overdue'}));
            $node.data({
                type: 'returns',
                filter: function (row) {
                    var now = moment();
                    return moment(row['due_date']).isBefore(now);
                }
            });
            $returnsDuedateFilter.append($node);
            $returnsDuedateFilter.on('change', function (event) {
                var data = $(event.target).find(':selected').data();
                filterTable(data);
            });

            // necessary when option added dynamically
            $('.selectpicker').selectpicker('refresh');
        }

        return function (options, data) {
            var defaults = {
                applicationsTableSelector: '#applications-table',
                globalLicenseTypeFilterSelector: '#global-filter-license-type',
                applicationsLicenseFilterSelector: '#applications-filter-license-type',
                applicationsStatusFilterSelector: '#applications-filter-status',
                returnsDueDateFilterSelector: '#returns-filter-dueDate'
            };
            options = $.extend({}, options, defaults);
            $(function () {
                $('.selectpicker').selectpicker();
                tableData = data || generateData();
                initTables(options, tableData);
                initFilters(options, tableData);
            })
        };
    }
);
