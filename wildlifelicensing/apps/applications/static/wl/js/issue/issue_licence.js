define(['jQuery', 'bootstrap-datetimepicker'], function($) {
    return {
        initialise: function() {
            // initialise all datapickers
            $("input[id$='date']").each(function() {
                $(this).datetimepicker({
                    format: 'DD/MM/YYYY'
                });
            });

            $('#issue').click(function(e) {
                var $issueLicenceForm = $('#issueLicenceForm');
                $issueLicenceForm.submit();
            });
        }
    }
});