define(
    [
        'jQuery',
        'lodash',
        'bootstrap',
        'select2'
    ],
    function ($, _) {
        var options;

        function initAssignee() {
            var $select = $(options.selectors.selectAssignee),
                 template = _.template('<option value="<%= value %>"><%= title %></option>');
            _.forEach(options.data.selectAssignee.values, function (option) {
                $select.append($(template({
                    value:option[0],
                    title:option[1]
                })));
            });
            $select.val(options.data.selectAssignee.selected);
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    selectAssignee: '#select-assignee'
                },
                data: {
                    selectAssignee: {
                        values: [],
                        selected: ''
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
                initAssignee();
                // things to do when the dom is ready
                $('select').select2()
            });
        }
    });
