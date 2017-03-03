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

        $conditionsTableBody.append($row);
    }

    function initDefaultConditions(defaultConditions) {
        $.each(defaultConditions, function(index, condition) {
            createConditionTableRow(condition, 'default');
        });
    }

    function initAdditionalConditions(assessment) {
        $.each(assessment.conditions, function(index, condition) {
            createConditionTableRow(condition, 'additional');
        });
    }

    function initForm() {
        $('#assessmentDone').click(function() {
            var $conditionsForm = $('#conditionsForm');
            $conditionsForm.submit();
        });
    }

    function initDeclineStatus(reason) {
        var $declinedReasonContainer = $('<div>'),
            $status = $('#status');

        if ($status) {
            if (!reason) {
                $declinedReasonContainer.append($('<p>').html("No reason"))
            } else {
                reason.split('\n').forEach(function (reason) {
                    $declinedReasonContainer.append($('<p>').html(reason));
                });
            }
            $status.html('').append('<a>Declined</a>');
            $status.popover({container: 'body', content: $declinedReasonContainer, html: true});
        }
    }

    return {
        init: function (assessment, application, formStructure, otherAssessments) {
            initApplicationDetailsPopover(application, formStructure);
            initOtherAssessorsCommentsPopover(otherAssessments);
            initDefaultConditions(application.licence_type.default_conditions);
            initAdditionalConditions(assessment);
            initForm();
            if (application['processing_status'].toLowerCase() === 'declined') {
                initDeclineStatus(application['declined_reason'] || '')
            }
        }
    }
});
