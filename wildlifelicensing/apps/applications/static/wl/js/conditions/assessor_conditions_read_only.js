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
        $.each(assessment.conditions, function(index, condition) {
            createConditionTableRow(condition, 'additional', true);
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
