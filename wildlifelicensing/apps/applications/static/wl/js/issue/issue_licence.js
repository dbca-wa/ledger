define([
    'jQuery',
    'bootstrap-datetimepicker',
    'select2'
], function($) {
    "use strict";

    return {
        initialise: function(options) {
            var $issueLicenceForm = $('#issueLicenceForm'),
                $regionSelect = $issueLicenceForm.find('select');

            // initialise all datapickers
            $("input[id$='date']").each(function() {
                $(this).datetimepicker({
                    format: 'DD/MM/YYYY'
                });
            });

            $('#issue').click(function(e) {
                $issueLicenceForm.submit();
            });

            $('#previewLicence').click(function(e) {
                $(this).attr("href", this.href + '?' + $issueLicenceForm.serialize());
            });

            $regionSelect.select2({
                placeholder: "Select applicable regions."
            });
            $regionSelect.removeClass('hidden');
        }
    };
});