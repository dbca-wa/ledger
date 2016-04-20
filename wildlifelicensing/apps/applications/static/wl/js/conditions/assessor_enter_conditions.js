define([
    'jQuery',
    'lodash',
    'js/conditions/enter_conditions'
], function ($, _, conditions) {

    function initForm() {
        $('#assessmentDone').click(function() {
            var $conditionsForm = $('#conditionsForm');
            $conditionsForm.submit();
        });
    }


    return {
        init: function (application, formStructure) {
            conditions.init(application, formStructure);
            initForm();
        }
    }
});
