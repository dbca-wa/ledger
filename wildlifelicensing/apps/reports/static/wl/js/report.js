define([
    'jQuery',
    'bootstrap-datetimepicker',
    'select2'
], function($) {
    "use strict";

    function initDatePicker() {
        $("[name$='date']").datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }

    function initRegionSelector(){
        var $select = $('#licence-form').find('select');
        $select.select2({
            placeholder: "Select region(s) or blank for all."
        });
        $select.removeClass('hidden');
    }

    function initPaymentsDatePicker() {
        var $form = $('#payments-form');
        $form.find('input').datetimepicker({
            format: 'DD/MM/YYYY HH:mm:SS'
        });
    }

    return {
        initialise: function() {
            initDatePicker();
            initRegionSelector();
            initPaymentsDatePicker();
        }
    };
});