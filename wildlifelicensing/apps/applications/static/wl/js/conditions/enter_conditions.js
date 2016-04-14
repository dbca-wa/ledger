define(['jQuery', 'bootstrap-3-typeahead'], function($) {
    function initDefaultCondition(defaultConditions) {
        $defaultConditions = $('#defaultConditions');
        $.each(defaultConditions, function(index, condition) {
            $row = $('<tr>');
            $row.append($('<td>').html(condition.code));
            $row.append($('<td>').html(condition.text));

            $remove = $('<a>Remove</a>');
            $remove.click(function(e) {
                $(this).parent().parent().remove();
            });

            $row.append($('<td>').html($remove));
            $defaultConditions.append($row);
        });
    }

    function initSelectConditions() {
        var conditions = {},
            $selectConditions = $('#selectConditions');

        $selectConditions.typeahead({
            source: function (query, process) {
                return $.get('/applications/search_conditions?q=' + query, function (data) {
                    condition_texts = [];
                    $.each(data, function(index, condition) {
                        conditions[condition.text] = condition;
                        condition_texts.push(condition.text);
                    });
                    return process(condition_texts);
                });
            },
            afterSelect: function(condition_text) {
                var condition = conditions[condition_text];
                
                $row = $('<tr>');
                $row.append($('<td>').html(condition.code));
                $row.append($('<td>').html(condition.text));

                $remove = $('<a>Remove</a>');
                $remove.click(function(e) {
                    $(this).parent().parent().remove();
                });

                $row.append($('<td>').html($remove));
                $('#additionalConditions').append($row);

                $selectConditions.val('');
            }
        })
    }

    return {
        init: function(application) {
            initDefaultCondition(application.licence_type.default_conditions);
            initSelectConditions();
        }
    }
});