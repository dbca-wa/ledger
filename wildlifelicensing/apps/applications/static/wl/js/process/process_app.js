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
            $('#assignee').select2({
                ajax: {
                    url: "/applications/list_staff/",
                    dataType: 'json',
                    data: function (name) {
                        return {
                            name: name
                        };
                    },
                    results: function (data) {
                        return {
                            results: data
                        }
                    }
                },
                initSelection: function(element, callback) {
                    $.ajax('/applications/list_staff/', {
                        dataType: 'json'
                    }).done(function(data) {
                        // set initial selection to first (and theoretically only) element
                        callback(data[0]);
                    });
                }
            });
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    selectAssignee: '#assignee'
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
            });
        }
    });
