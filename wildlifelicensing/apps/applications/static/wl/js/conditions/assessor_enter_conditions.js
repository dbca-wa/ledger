define([
    'jQuery',
    'lodash',
    'js/conditions/enter_conditions'
], function ($, _, conditions) {

    function initForm() {
        $('#assessmentDone').click(function(e) {
            console.log("Assessment Done");
        });
    }


    return {
        init: function (application, formStructure) {
            conditions.init(application, formStructure);
            initForm();
        }
    }
});
