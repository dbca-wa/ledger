define(
    'js/officers_dashboard',
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable'
    ],
    function ($, _, dt) {
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
                    data: 'date'
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
            applicationsTable, licensesTable, returnsTable;


        function mockData() {
            var dates = ['01/01/2016', '12/11/2015', '23/04/2015', '01/03/2016'],
                customers = ['Serge Le Breton', 'Pauline Goodreid', 'Paul Gioia', 'Graham Thompson', 'Tony Prior'],
                statusApplication = ['pending', 'draft', 'issued'],
                licenseTypes = ['reg17', 'reg4', 'reg666', 'reg40'],
                statusLicense = ['submitted', 'granted', 'refused', 'cancelled'];


            applicationsTable.populate(_.times(30, function () {
                return {
                    license_type: _.sample(licenseTypes),
                    customer: _.sample(customers),
                    date: _.sample(dates),
                    status: _.sample(statusApplication)
                }
            }));
            licensesTable.populate(_.times(30, function () {
                var row = {
                    license_type: _.sample(licenseTypes),
                    customer: _.sample(customers),
                    issue_date: _.sample(dates),
                    expire_date: _.sample(dates),
                    status: _.sample(statusLicense)
                };
                row.license_no = row.license_type + '-' + _.random(1, 100);
                return row;
            }));
            returnsTable.populate(_.times(30, function () {
                var row = {
                    license_type: _.sample(licenseTypes),
                    customer: _.sample(customers),
                    due_date: _.sample(dates),
                    status: _.sample(statusApplication)
                };
                row.license_no = row.license_type + '-' + _.random(1, 100);
                return row;
            }));
        }


        function initTables(options) {
            applicationsTable = dt.initTable(
                options.applicationsTableSelector,
                tableOptions,
                applicationsColumns
            );

            licensesTable = dt.initTable(
                options.licensesTableSelector,
                tableOptions,
                licensesColumns
            );
            returnsTable = dt.initTable(
                options.returnsTableSelector,
                tableOptions,
                returnsColumns
            );
        }


        return function (options) {
            var defaults = {
                applicationsTableSelector: '#applications-table',
                licensesTableSelector: '#licenses-table',
                returnsTableSelector: '#returns-table'
            };
            options = $.extend({}, options, defaults);
            $(function () {
                initTables(options);
                mockData();
            })
        };
    }
);
