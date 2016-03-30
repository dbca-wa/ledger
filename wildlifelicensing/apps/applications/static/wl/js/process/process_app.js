define(
    [
        'jQuery',
        'lodash',
        'js/deepmerge',
        'bootstrap',
        'select2'
    ],
    function ($, _, merge) {
        var options;

        function initAssignee() {
            var $select = $(options.selectors.selectAssignee),
                 template = _.template('<option value="<%= value %>"><%= title %></option>');
            _.forEach(options.data.selectAssignee, function (option) {
                $select.append($(template({
                    value:option[0],
                    title:option[1]
                })));
            });
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    selectAssignee: '#select-assignee'
                },
                data: {
                    selectAssignee: [['', 'Unassigned'], ['serge@gaiaresources.com.au', 'Serge Le Breton']]
                }
            };
            options = merge(defaults, moduleOptions);
            $(function () {
                initAssignee();
                // things to do when the dom is ready
                $('select').select2()
            });
        }
    });
