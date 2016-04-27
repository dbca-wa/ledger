define([
    'jQuery',
    'lodash',
    'js/entry/application_preview',
    'select2'
], function ($, _, applicationPreview) {
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

        var $clone = $('<a>Clone</a>');
        $clone.click(function(e) {
            $createCustomConditionForm.find('h4').text('Create Custom Condition from ' + condition.code);
            $createCustomConditionForm.find('textarea').val(condition.text);
            $createCustomConditionModal.modal('show');
        });

        if(!readonly) {
            $action = $('<div>').append($remove).append($('<hr>')).append($clone);

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
            $action = $('<div>').append($clone);
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
                window.alert('The specified ondition has already been entered.')
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
        $('#assessmentDone').click(function() {
            var $conditionsForm = $('#conditionsForm');
            $conditionsForm.submit();
        });
    }

    return {
        init: function (application, formStructure) {
            initApplicationDetailsPopover(application, formStructure);
            initDefaultConditions(application.licence_type.default_conditions);
            initAdditionalConditions();
            initCustomConditions();
            initForm();
        }
    }
});
