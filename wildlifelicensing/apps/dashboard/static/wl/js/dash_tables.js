define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'bootstrap'
    ],
    function ($, _, dt) {
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
            $applicationsStatusTypeFilter,
            $applicationsAssigneeTypeFilter;

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
            _.forEach(data.applications.filters.licenceType.values, function (value) {

                $node = createOptionNode(value);
                $applicationsLicenceTypeFilter.append($node);
            });
            $applicationsLicenceTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });
            // status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = createOptionNode(value);
                $applicationsStatusTypeFilter.append($node);
            });
            $applicationsStatusTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });

            // assignee filter
            if ($applicationsAssigneeTypeFilter && data.applications.filters.assignee.values) {
                _.forEach(data.applications.filters.assignee.values, function (value) {
                    $node = createOptionNode(value);
                    $applicationsAssigneeTypeFilter.append($node);
                });
                $applicationsAssigneeTypeFilter.on('change', function () {
                    applicationsTable.ajax.reload();
                });
            }

        }

        function setFilters(query) {
            $('#applications-collapse').collapse('show');
            if (query['application_status']) {
                $applicationsStatusTypeFilter.val(query['application_status']);
            }
            if (query['application_assignee']) {
                $applicationsAssigneeTypeFilter.val(query['application_assignee'])
            }
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    applicationsTable: '#applications-table',
                    applicationsAccordion: '#applications-collapse',
                    applicationsFilterForm: '#applications-filter-form',
                    applicationsLicenceFilter: '#applications-filter-licence-type',
                    applicationsStatusFilter: '#applications-filter-status',
                    applicationsAssigneeFilter: '#applications-filter-assignee'
                },
                data: {
                    'applications': {
                        ajax: {
                            url: "/dashboard/data/applications"
                        },
                        'columnDefinitions': [],
                        'filters': {
                            'licenceType': {
                                'values': []
                            },
                            'status': {
                                'values': []
                            },
                            'assignee': {
                                'values': []
                            }
                        }
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
                $applicationsLicenceTypeFilter = $(options.selectors.applicationsLicenceFilter);
                $applicationsStatusTypeFilter = $(options.selectors.applicationsStatusFilter);
                $applicationsAssigneeTypeFilter = $(options.selectors.applicationsAssigneeFilter);

                $(options.selectors.applicationsAccordion).collapse('show');

                initApplicationsFilters();
                if (options.data.query) {
                    // set filter according to query data
                    setFilters(options.data.query);
                }
                initTables();
            })
        };
    }
);
