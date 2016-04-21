define(['jQuery', 'lodash', 'js/entry/application_preview', 'select2'], function($, _, applicationPreview) {
    var $conditionsTableBody = $('#conditionsBody'),
        $conditionsEmptyRow = $('#conditionsEmptyRow'),
        $createCustomConditionModal = $('#createCustomConditionModal'),
        $createCustomConditionForm = $('#createConditionForm');

    function initApplicationDetailsPopover(application, formStructure) {
        var $contentContainer = $('<div>'),
            $viewApplicationDetails = $('#viewApplicationDetails');

        applicationPreview.layoutPreviewItems($contentContainer, formStructure, application.data);

        $viewApplicationDetails.popover({container: 'body', content: $contentContainer, html: true});
    }

    function initAssessments(assessments) {
        var $assessments = $('#assessments');

        $.each(assessments, function(assessmentIndex, assessment) {
            var $contentContainer = $('<div>'),
                $assessorRow = $('<tr>');
                $viewDetails = $('<a>').text('View Feedback'),
                $conditionsTable = $('<table>').addClass('table').addClass('table-bordered').addClass('popover-conditions-table').
                    append($('<thead>')).append($('<tbody>'));

            $contentContainer.append($('<label>').text("Assessor's Conditions"));

            $conditionsTable.find('thead').append($('<tr>').append($('<th>').text('Code')).append($('<th>').text('Condition')));
            $.each(assessment.conditions, function(conditionIndex, condition) {
                var $conditionRow = $('<tr>').addClass('assessor');
                $conditionRow.append($('<td>').text(condition.code));
                $conditionRow.append($('<td>').text(condition.text));
                $conditionsTable.append($conditionRow);
            });

            $contentContainer.append($conditionsTable);
            $contentContainer.append($('<label>').text("Assessor's Comments"));
            $contentContainer.append($('<p>').text(assessment.comment));

            $viewDetails.popover({
                container: 'body',
                title: 'Conditions / Comments from ' + assessment.assessor_department.name,
                content: $contentContainer,
                html: true
            });

            $assessorRow.append($('<td>').html(assessment.assessor_department.name));
            $assessorRow.append($('<td>').html($viewDetails));

            $assessments.append($assessorRow);
        });
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
            } else if (_.some(assessorConditions, ['id', condition.id])) {
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

    function initAssessorsConditions(assessments) {
        $.each(assessments, function(assessmentIndex, assessment) {
            $.each(assessment.conditions, function(conditionIndex, condition) {
                createConditionTableRow(condition, 'assessor');
            });
        });
    }

    function initAdditionalConditions() {
        var conditions = {},
            $searchConditions = $('#searchConditions'),
            $addCondition = $('#addCondition'),
            $conditionsForm = $('#conditionsForm');

        $searchConditions.select2({
            dropdownCssClass : 'conditions-dropdown',
            minimumInputLength: 3,
            ajax: {
                url: '/applications/search_conditions',
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
                window.alert('The specified condition has already been entered.')
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
        $('#issueLicence').click(function(e) {
            var $conditionsForm = $('#conditionsForm');
            $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'submissionType').val(this.id));
            $conditionsForm.submit();
        });

        $('#backToProcessing').click(function(e) {
            var $conditionsForm = $('#conditionsForm');
            $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'submissionType').val(this.id));
            $conditionsForm.submit();
        });
    }

    return {
        init: function(application, assessments, formStructure) {
            initApplicationDetailsPopover(application, formStructure);
            if(assessments.length) {
                initAssessments(assessments);
            }

            if(application.conditions.length) {
                initExistingConditions(application, assessments);
            } else {
                initDefaultConditions(application.licence_type.default_conditions);
                initAssessorsConditions(assessments);
            }

            initAdditionalConditions();
            initCustomConditions();
            initForm();
        }
    }
});