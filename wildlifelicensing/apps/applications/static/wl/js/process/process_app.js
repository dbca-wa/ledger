define(
    [
        'jQuery',
        'lodash',
        'bootstrap',
        'select2'
    ],
    function ($, _) {
        var options;

        function initAssignee(options) {
            var $assignee = $(options.selectors.selectAssignee);

            $assignee.select2({
                ajax: {
                    url: "/applications/list_officers/",
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
                    if(options.data.application.assigned_officer) {
                        callback({id: options.data.application.assigned_officer.id, text: options.data.application.assigned_officer.first_name + ' ' +
                                 options.data.application.assigned_officer.last_name});
                    } else {
                        callback({id: 0, text: 'Unassigned'});
                    }
                }
            });

            $assignee.on('change', function(e) {
                $.post('/applications/assign_officer/', {
                        applicationID: options.data.application.id,
                        csrfmiddlewaretoken: options.data.csrf_token,
                        userID: e.val
                    }
                );
            });

            $(options.selectors.assignToMeLink).click(function() {
                $.post('/applications/assign_officer/', {
                        applicationID: options.data.application.id,
                        csrfmiddlewaretoken: options.data.csrf_token,
                        userID: options.data.user.id
                    }, 
                    function(data) {
                        $assignee.select2('data', data);
                    }
                );
            });
        }

        function initActions(options) {
        	$('.processing-action-group').find('button').click(function(e) {
        		$(this).parent().parent().find('span').removeClass('hidden');
        		$(this).parent().hide();
        	});
        }

        return function (moduleOptions) {
            var defaults = {
                selectors: {
                    selectAssignee: '#assignee',
                    assignToMeLink: '#assignToMe'
                },
                data: {}
            };

            // merge the defaults options, and the options passed in parameter.
            // This is a deep merge but the array are not merged
            options = _.mergeWith({}, defaults, moduleOptions, function (objValue, srcValue) {
                if (_.isArray(objValue)) {
                    return srcValue;
                }
            });

            $(function () {
                initAssignee(options);
                initActions(options);
            });
        }
    });
