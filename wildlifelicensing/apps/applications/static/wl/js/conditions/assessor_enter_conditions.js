define([
    'jQuery',
    'lodash',
    'js/entry/application_preview',
    'select2'
], function ($, _, applicationPreview) {
    var $conditionsTableBody = $('#conditionsBody'),
    $conditionsEmptyRow = $('#conditionsEmptyRow'),
    $createCustomConditionModal = $('#createCustomConditionModal');

    function initApplicationDetailsPopover(application, formStructure) {
        var $contentContainer = $('<div>'),
            $viewApplicationDetails = $('#viewApplicationDetails');

        applicationPreview.layoutPreviewItems($contentContainer, formStructure, application.data);

        $viewApplicationDetails.popover({container: 'body', content: $contentContainer, html: true});
    }

    function initAssignee(assessment, csrfToken, assessorsList, userID) {
        var $assignee = $('#assignee');

        $assignee.select2({
            data: assessorsList,
            initSelection: function (element, callback) {
                if (assessment.assigned_assessor) {
                    callback({
                        id: assessment.assigned_assessor.id, text: assessment.assigned_assessor.first_name + ' ' +
                        assessment.assigned_assessor.last_name
                    });
                } else {
                    callback({id: 0, text: 'Unassigned'});
                }
            }
        });

        $assignee.on('change', function (e) {
            $.post('/applications/assign-assessor/', {
                assessmentID: assessment.id,
                    csrfmiddlewaretoken: csrfToken,
                    userID: e.val
                },
                function (data) {
                    $assignee.select2('data', data.assigned_assessor);
                }
            );
        });

        $('#assignToMe').click(function () {
            $.post('/applications/assign-assessor/', {
                    assessmentID: assessment.id,
                    csrfmiddlewaretoken: csrfToken,
                    userID: userID
                },
                function (data) {
                    $assignee.select2('data', data.assigned_assessor);
                }
            );
        });
    }

    function initOtherAssessorsCommentsPopover(assessments) {
        var $contentContainer = $('<div>'),
            $viewOtherAssessorsComments = $('#viewOtherAssessorsComments');

        if(assessments.length) {
            $.each(assessments, function(index, assessment) {
                if(assessment.status === 'Assessed') {
                    var assessorGroupName = '<strong>' + assessment.assessor_group.name + ': </strong>';
                    $contentContainer.append($('<p>').html(assessorGroupName + assessment.comment));
                }
            })
        }

        if ($contentContainer.children().length) {
            $contentContainer.find(':last-child').addClass('no-margin');
        } else {
            $contentContainer.append($('<p>').addClass('no-margin').text("No other assessors' comments available"));
        }

        $viewOtherAssessorsComments.popover({container: 'body', content: $contentContainer, html: true});
    }

    function createConditionTableRow(condition, rowClass, readonly) {
        var $row = $('<tr>').addClass(rowClass);

        $row.append($('<td>').html(condition.code));
        $row.append($('<td>').html(condition.text));

        var $remove = $('<a>Remove</a>');
        $remove.click(function(e) {
            $row.remove();

            if($conditionsTableBody.find('tr').length == 1) {
                $conditionsEmptyRow.removeClass('hidden');
            }

            $conditionsTableBody.find('input[value="' + condition.id + '"]').remove();
        });

        if(!readonly) {
            $action = $('<div>').append($remove);

            var $moveUp = $('<a>').append($('<span>').addClass('glyphicon').addClass('glyphicon-chevron-up'));
            $moveUp.click(function(e) {
                if(!$row.prev().hasClass('default')) {
                    $row.insertBefore($row.prev());
                }
            });

            var $moveDown = $('<a>').append($('<span>').addClass('glyphicon').addClass('glyphicon-chevron-down'));
            $moveDown.click(function(e) {
                $row.insertAfter($row.next());
            });

            $ordering = $('<div>').css('text-align', 'center').append($moveUp).append($('<hr>')).append($moveDown);
        } else {
            $action = $('<div>');
            $ordering = $('<div>');
        }

        $row.append($('<td>').css('vertical-align', 'middle').html($action));
        $row.append($('<td>').css('vertical-align', 'middle').html($ordering));

        $conditionsTableBody.append($row);

        if(!readonly) {
            $row.append($('<input>').attr('type', 'hidden').attr('name', 'conditionID').val(condition.id));
        }
    }

    function initDefaultConditions(defaultConditions) {
        $.each(defaultConditions, function(index, condition) {
            createConditionTableRow(condition, 'default', true);
        });
    }

    function initAdditionalConditions(assessment) {
        var conditions = {},
            $searchConditions = $('#searchConditions'),
            $addCondition = $('#addCondition'),
            $conditionsForm = $('#conditionsForm');

        $searchConditions.select2({
            dropdownCssClass : 'conditions-dropdown',
            minimumInputLength: 3,
            ajax: {
                url: '/applications/search-conditions',
                dataType: 'json',
                quietMillis: 250,
                data: function (term, page) {
                    return {
                        q: term,
                    };
                },
                results: function (data, page) {
                    conditions = data;

                    conditions = _.chain(data).keyBy('id').value();

                    return { results: data };
                },
                cache: true
            },
            formatResult: function(object) {
                var $container = $('<table>'),
                    $row = $('<tr>');

                $row.append($('<td>').html(object.code));
                $row.append($('<td>').html(object.text));

                $container.append($row);

                return $container;
            },
            formatResultCssClass: function(object) {
                return 'conditions-option';
            }
        });

        $searchConditions.on('change', function(e) {
            $addCondition.prop('disabled', false);
        });

        $addCondition.click(function(e) {
            var condition = conditions[$searchConditions.val()];
                existingConditions = $conditionsForm.find('input[type=hidden]');

            // only add condition if it hasn't already been entered
            if(!_.includes(_.map(existingConditions, function(condition) {return $(condition).val()}), String(condition.id), 1)) {
                    createConditionTableRow(condition, 'additional');
            } else {
                window.alert('The specified condition has already been entered.');
            }

            $searchConditions.select2('val', '');
        });

        $.each(assessment.conditions, function(index, condition) {
            createConditionTableRow(condition, 'additional', false);
        });
    }

    function initForm() {
        $('#save, #conclude').click(function() {
            var $conditionsForm = $('#conditionsForm');

            if($(this).attr('id') === 'conclude') {
                $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'conclude'));
            }

            $conditionsForm.submit();
        });
    }

    return {
        init: function (assessment, application, formStructure, otherAssessments, csrfToken, assessors, userID) {
            initApplicationDetailsPopover(application, formStructure);
            initAssignee(assessment, csrfToken, assessors, userID);
            initOtherAssessorsCommentsPopover(otherAssessments);
            initDefaultConditions(application.licence_type.default_conditions);
            initAdditionalConditions(assessment);
            initForm();
        }
    }
});
