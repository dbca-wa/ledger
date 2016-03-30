define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'js/deepmerge',
        'bootstrap'
    ],
    function ($, _, dt, merge) {
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
            $applicationsLicenceTypeFilter,
            $applicationsStatusTypeFilter;

        function initTables() {
            var applicationTableOptions = $.extend({}, tableOptions, {
                    ajax: {
                        url: options.data.applications.ajax.url,
                        data: function (d) {
                            // add filters to the query
                            d.filters = $(options.selectors.applicationsFilterForm).serializeArray();
                        },
                        error: function () {
                            console.log("error");
                            //TODO Stop the data table 'Processing' and show an error.
                        }
                    }
                }),
                applicationsColumns = options.data.applications.columnDefinitions;

            applicationsTable = dt.initTable(
                options.selectors.applicationsTable,
                applicationTableOptions,
                applicationsColumns
            );
        }

        function initFilters() {
            var data = options.data,
                optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            // applications licence type
            _.forEach(data.applications.filters.licenceType.values, function (value) {

                $node = createOptionNode(value);
                $applicationsLicenceTypeFilter.append($node);
            });
            $applicationsLicenceTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });
            // applications status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = createOptionNode(value);
                $applicationsStatusTypeFilter.append($node);
            });
            $applicationsStatusTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });

        }

        function setFilters(data) {
            if (data.model) {
                if (data.model === 'application') {
                    $('#applications-collapse').collapse('show');
                    if (data.status) {
                        $applicationsStatusTypeFilter.val(data.status);
                    }
                    if (data.licence_type) {
                        $applicationsLicenceTypeFilter.val(data.licence_type);
                    }
                }
            }
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    applicationsTable: '#applications-table',
                    applicationsAccordion: '#applications-collapse',
                    applicationsFilterForm: '#applications-filter-form',
                    applicationsLicenceFilter: '#applications-filter-licence-type',
                    applicationsStatusFilter: '#applications-filter-status'
                },
                data: {
                    'applications': {
                        ajax: {
                            url: "/dashboard/data/applications"
                        },
                        'columnDefinitions': [
                        ],
                        'filters': {
                            'licenceType': {
                                'values': []
                            },
                            'status': {
                                'values': []
                            }
                        }
                    }
                }
            };
            options = merge(defaults, moduleOptions);
            $(function () {
                $applicationsLicenceTypeFilter = $(options.selectors.applicationsLicenceFilter);
                $applicationsStatusTypeFilter = $(options.selectors.applicationsStatusFilter);

                $(options.selectors.applicationsAccordion).collapse('show');

                initFilters();
                if (options.data.query) {
                    // set filter according to query data
                    setFilters(options.data.query);
                }
                initTables();
            })
        };
    }
);
