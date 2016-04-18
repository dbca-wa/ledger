define(['jQuery', 'lodash', 'select2'], function($, _) {
    var $createCustomConditionModal = $('#createCustomConditionModal'),
        $createCustomConditionForm = $('#createConditionForm'),
        $conditionsForm = $('#conditionsForm');

    function createConditionTableRow(condition, $tableBody, $emptyRow) {
        var $row = $('<tr>');

        $row.append($('<td>').html(condition.code));
        $row.append($('<td>').html(condition.text));

        var $remove = $('<a>Remove</a>');
        $remove.click(function(e) {
            $row.remove();

            if($tableBody.find('tr').length == 1) {
                $emptyRow.removeClass('hidden');
            }

            $conditionsForm.find('input[value="' + condition.id + '"]').remove();
        });

        var $clone = $('<a>Clone</a>');
        $clone.click(function(e) {
            $createCustomConditionForm.find('input[type=text]').val(condition.code);
            $createCustomConditionForm.find('textarea').val(condition.text);
            $createCustomConditionModal.modal('show');
        });

        $action = $('<div>').append($remove).append($('<hr>')).append($clone);

        $row.append($('<td>').css('vertical-align', 'middle').html($action));
        $tableBody.append($row);

        $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'conditionID').val(condition.id));
    }

    function initDefaultConditions(defaultConditions) {
        var $defaultConditionsBody = $('#defaultConditions').find('tbody');
            $defaultConditionsEmptyRow = $defaultConditionsBody.find('#defaultConditionsEmptyRow');

        $.each(defaultConditions, function(index, condition) {
            createConditionTableRow(condition, $defaultConditionsBody, $defaultConditionsEmptyRow);
        });

        $('#resetDefaultConditions').click(function(e) {
            $defaultConditionsBody.empty();

            $.each(defaultConditions, function(index, condition) {
                createConditionTableRow(condition, $defaultConditionsBody, $defaultConditionsEmptyRow);
            });

            $defaultConditionsEmptyRow.addClass('hidden');

            $defaultConditionsBody.append($defaultConditionsEmptyRow);
        });
    }

    function initAdditionalConditions() {
        var conditions = {},
            $searchConditions = $('#searchConditions'),
            $addCondition = $('#addCondition'),
            $additionalConditionsBody = $('#additionalConditions').find('tbody'),
            $additionalConditionsEmptyRow = $additionalConditionsBody.find('#additionalConditionsEmptyRow');

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

                $additionalConditionsEmptyRow.addClass('hidden');

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

            createConditionTableRow(condition, $additionalConditionsBody, $additionalConditionsEmptyRow);
        });
    }

    function initCustomConditions() {
        var $additionalConditionsBody = $('#additionalConditions').find('tbody'),
            $additionalConditionsEmptyRow = $additionalConditionsBody.find('#additionalConditionsEmptyRow');

        $('#createCustomCondition').click(function(e) {
            $createCustomConditionModal.modal('show');
        });

        $createCustomConditionForm.submit(function(e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    createConditionTableRow(data, $additionalConditionsBody, $additionalConditionsEmptyRow);
                    $additionalConditionsEmptyRow.addClass('hidden');
                    $createCustomConditionModal.modal('hide');
                }
            });

            e.preventDefault();
        });

        $createCustomConditionModal.on('hidden.bs.modal', function(e) {
            $createCustomConditionForm.find('input[type=text], textarea').val('');
        });
    }

    return {
        init: function(application) {
            initDefaultConditions(application.licence_type.default_conditions);
            initAdditionalConditions();
            initCustomConditions();
        }
    }
});