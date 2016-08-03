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

    return {
        init: function (assessment, application, formStructure) {
            initApplicationDetailsPopover(application, formStructure);
            initDefaultConditions(application.licence_type.default_conditions);
            initAdditionalConditions(assessment);
            initForm();
        }
    }
});
