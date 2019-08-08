define(['jQuery', 'lodash', 'js/entry/application_preview', 'select2'], function($, _, applicationPreview) {
    var $conditionsForm = $('#conditionsForm'),
        $conditionsTableBody = $('#conditionsBody'),
        $conditionsEmptyRow = $('#conditionsEmptyRow'),
        $createCustomConditionModal = $('#createCustomConditionModal'),
        $createCustomConditionForm = $('#createConditionForm');

    function initApplicationDetailsPopover(application, formStructure) {
        var $contentContainer = $('<div>'),
            $viewApplicationDetails = $('#viewApplicationDetails');

        applicationPreview.layoutPreviewItems($contentContainer, formStructure, application.data);

        $viewApplicationDetails.popover({container: 'body', content: $contentContainer, html: true});
    }

    function initAssessments(assessments, csrfToken) {
        var $assessments = $('#assessments'),
            showAssessmentsTable = false;

        $.each(assessments, function(assessmentIndex, assessment) {
            if(assessment.status === 'Assessed') {
                showAssessmentsTable = true;

                var $contentContainer = $('<div>'),
                    $assessorRow = $('<tr>'),
                    $viewFeedback = $('<p>').addClass('center').addClass('no-margin').append(
                            $('<a>').text('View Feedback').attr('data-toggle', 'popover'));

                $contentContainer.append($('<label>').text("Assessor's Suggested Conditions"));

                if(assessment.conditions.length > 0) {
                    var $assessorsConditionsTable = $('<table>').addClass('table').addClass('table-bordered').addClass('popover-conditions-table'),
                        $assessorsConditionsTableHead = $('<thead>').addClass('popover-conditions-table-head'),
                        $assessorsConditionsTableBody = $('<tbody>').addClass('conditions-table-body');

                    $assessorsConditionsTable.append($assessorsConditionsTableHead).append($assessorsConditionsTableBody);

                    $assessorsConditionsTableHead.append($('<tr>').append($('<th>').addClass('code').text('Code')).
                        append($('<th>').addClass('condition').text('Condition')).
                        append($('<th>').addClass('action-status').text('Action / Status')));

                    $.each(assessment.conditions, function(conditionIndex, assessmentCondition) {
                        var $conditionRow = $('<tr>').addClass('assessor'),
                            $actionCell = $('<td>');

                        $conditionRow.append($('<td>').text(assessmentCondition.condition.code));
                        $conditionRow.append($('<td>').text(assessmentCondition.condition.text));

                        if (assessmentCondition.acceptance_status === 'Not Specified') {
                            var $accept = $('<a>').text('Accept'),
                                $decline = $('<a>').text('Decline');

                            $accept.click(function(e) {
                                var existingConditions = $conditionsForm.find('input[type=hidden]');

                                // only add condition if it hasn't already been entered
                                if(!_.includes(_.map(existingConditions, function(condition) {return $(condition).val()}),
                                        String(assessmentCondition.condition.id), 1)) {
                                    $.post('/applications/set-assessment-condition-state/',  {
                                        assessmentConditionID: assessmentCondition.id,
                                        acceptanceStatus: 'accepted',
                                        csrfmiddlewaretoken: csrfToken
                                    }, function(acceptanceStatus) {
                                        assessmentCondition.acceptance_status = acceptanceStatus;
                                        createConditionTableRow(assessmentCondition.condition, 'assessor');
                                        $actionCell.html($('<p>').text(assessmentCondition.acceptance_status));
                                        $conditionsEmptyRow.addClass('hidden');
                                    });
                                } else {
                                    window.alert('The specified condition has already been entered.');
                                }
                            });

                            $decline.click(function(e) {
                                $.post('/applications/set-assessment-condition-state/', {
                                    assessmentConditionID: assessmentCondition.id,
                                    acceptanceStatus: 'declined',
                                    csrfmiddlewaretoken: csrfToken
                                }, function(acceptanceStatus) {
                                    assessmentCondition.acceptance_status = acceptanceStatus;
                                    $actionCell.html($('<p>').text(assessmentCondition.acceptance_status));
                                });
                            });

                            $actionCell.html($('<div>').append($accept).append($('<hr>')).append($decline));
                        } else {
                            $actionCell.html($('<p>').text(assessmentCondition.acceptance_status));
                        }

                        $conditionRow.append($actionCell);

                        $assessorsConditionsTableBody.append($conditionRow);
                    });

                    $contentContainer.append($assessorsConditionsTable);
                } else {
                    $contentContainer.append($('<p>').append($('<em>').text('No conditions specified')));
                }

                $contentContainer.append($('<label>').text("Assessor's Comment"));

                if(assessment.comment.length > 0) {
                    $contentContainer.append($('<p>').text(assessment.comment));
                } else {
                    $contentContainer.append($('<p>').append($('<em>').text('No comment')));
                }

                $viewFeedback.popover({
                    container: 'body',
                    title: 'Conditions / Comments from ' + assessment.assessor_group.name,
                    content: $contentContainer,
                    html: true
                });

                $assessorRow.append($('<td>').html(assessment.assessor_group.name));
                $assessorRow.append($('<td>').html($viewFeedback));

                $assessments.append($assessorRow);
            }
        });

        if(showAssessmentsTable) {
            $assessments.removeClass('hidden');
        } else {
            $assessments.after($('<p>').append($('<em>').text('No assessments available')));
        }
    }

    function createConditionTableRow(condition, rowClass) {
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

        var $clone = $('<a>Clone</a>');
        $clone.click(function(e) {
            $createCustomConditionForm.find('h4').text('Create Custom Condition from ' + condition.code);
            $createCustomConditionForm.find('textarea').val(condition.text);
            $createCustomConditionModal.modal('show');
        });

        $action = $('<div>').append($remove).append($('<hr>')).append($clone);
        $row.append($('<td>').css('vertical-align', 'middle').html($action));

        var $moveUp = $('<a>').append($('<span>').addClass('glyphicon').addClass('glyphicon-chevron-up'));
        $moveUp.click(function(e) {
            $row.insertBefore($row.prev());
        });

        var $moveDown = $('<a>').append($('<span>').addClass('glyphicon').addClass('glyphicon-chevron-down'));
        $moveDown.click(function(e) {
            $row.insertAfter($row.next());
        });

        $ordering = $('<div>').css('text-align', 'center').append($moveUp).append($('<hr>')).append($moveDown);
        $row.append($('<td>').css('vertical-align', 'middle').html($ordering));

        $conditionsTableBody.append($row);

        $row.append($('<input>').attr('type', 'hidden').attr('name', 'conditionID').val(condition.id));
    }

    function initExistingConditions(application, assessments) {
        var assessorConditions = [];

        $.each(assessments, function(index, assessment) {
            $.merge(assessorConditions, assessment.conditions);
        });

        $.each(application.conditions, function(index, condition) {
            if(_.some(application.licence_type.default_conditions, ['id', condition.id])) {
                createConditionTableRow(condition, 'default');
            } else if (_.some(_.map(assessorConditions, function(assessorCondition) {
                        return assessorCondition.condition
                    }), ['id', condition.id])) {
                createConditionTableRow(condition, 'assessor');
            } else if(condition.one_off) {
                createConditionTableRow(condition, 'custom');
            } else {
                createConditionTableRow(condition, 'additional');
            }
        });
    }

    function initDefaultConditions(defaultConditions) {
        $.each(defaultConditions, function(index, condition) {
            createConditionTableRow(condition, 'default');
        });
    }

    function initAdditionalConditions() {
        var conditions = {},
            $searchConditions = $('#searchConditions'),
            $addCondition = $('#addCondition');

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
                $conditionsEmptyRow.addClass('hidden');
            } else {
                window.alert('The specified condition has already been entered.');
            }

            $searchConditions.select2('val', '');
        });
    }

    function initCustomConditions() {
        var $createConditionError = $('#createConditionError');

        $('#createCustomCondition').click(function(e) {
            $createCustomConditionModal.find('h4').text('Create Custom Condition');
            $createCustomConditionModal.modal('show');
        });

        $createCustomConditionForm.submit(function(e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    if(typeof data === "string" || data instanceof String) {
                        $createConditionError.find('span').text(data);
                        $createConditionError.removeClass('hidden');
                    } else {
                        createConditionTableRow(data, 'custom');
                        $conditionsEmptyRow.addClass('hidden');
                        $createCustomConditionModal.modal('hide');
                    }
                }
            });

            e.preventDefault();
        });

        $createCustomConditionModal.on('hidden.bs.modal', function(e) {
            $createCustomConditionForm.find('input[type=text], textarea').val('');
            $createCustomConditionForm.find('input[type=checkbox]').attr('checked', false);
            $createConditionError.addClass('hidden');
        });
    }

    function initForm() {
        var $conditionsForm = $('#conditionsForm');

        function _submitForm(e) {
            $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'submissionType').val(this.id));
            $conditionsForm.submit();
        }

        $('#issueLicence').click(_submitForm);
        $('#save').click(_submitForm);
        $('#backToProcessing').click(_submitForm);
    }

    return {
        init: function(application, assessments, formStructure, csrfToken) {
            initApplicationDetailsPopover(application, formStructure);
            if(assessments.length) {
                initAssessments(assessments, csrfToken);
            }

            if(application.conditions.length) {
                initExistingConditions(application, assessments);
            } else {
                initDefaultConditions(application.licence_type.default_conditions);
            }

            if($conditionsTableBody.find('tr').length > 1) {
                $conditionsEmptyRow.addClass('hidden');
            }

            initAdditionalConditions();
            initCustomConditions();

            initForm();
        }
    }
});