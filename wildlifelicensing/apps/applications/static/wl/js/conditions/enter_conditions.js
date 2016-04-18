define(['jQuery', 'lodash', 'select2'], function($, _) {
    var $createCustomConditionModal = $('#createCustomConditionModal'),
        $createCustomConditionForm = $('#createConditionForm'),
        $conditionsForm = $('#conditionsForm');

    function createConditionTableRow(condition, $table, $emptyRow) {
        var $row = $('<tr>');

        $row.append($('<td>').html(condition.code));
        $row.append($('<td>').html(condition.text));

        var $remove = $('<a>Remove</a>');
        $remove.click(function(e) {
            $row.remove();

            if($table.find('tr').length == 2) {
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
        $table.append($row);

        $conditionsForm.append($('<input>').attr('type', 'hidden').attr('name', 'conditionID').val(condition.id));
    }

    function initDefaultConditions(defaultConditions) {
        var $defaultConditions = $('#defaultConditions'),
            $defaultConditionsEmptyRow = $defaultConditions.find('#defaultConditionsEmptyRow');

        $.each(defaultConditions, function(index, condition) {
            createConditionTableRow(condition, $defaultConditions, $defaultConditionsEmptyRow);
        });
    }

    function initAdditionalConditions() {
        var conditions = {},
            $searchConditions = $('#searchConditions'),
            $addCondition = $('#addCondition'),
            $additionalConditions = $('#additionalConditions'),
            $additionalConditionsEmptyRow = $additionalConditions.find('#additionalConditionsEmptyRow');

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

            createConditionTableRow(condition, $additionalConditions, $additionalConditionsEmptyRow);
        });
    }

    function initCustomConditions() {
        var $additionalConditions = $('#additionalConditions'),
            $additionalConditionsEmptyRow = $additionalConditions.find('#additionalConditionsEmptyRow');

        $('#createCustomCondition').click(function(e) {
            $createCustomConditionModal.modal('show');
        });

        $createCustomConditionForm.submit(function(e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    createConditionTableRow(data, $additionalConditions, $additionalConditionsEmptyRow);

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