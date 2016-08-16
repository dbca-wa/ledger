define([
    'jQuery',
    'bootstrap-datetimepicker',
    'select2'
], function($) {
    "use strict";

    return {
        initialise: function() {
            var $issueLicenceForm = $('#issueLicenceForm'),
                $issueButton = $('#issue'),
				$regionSelect = $issueLicenceForm.find('select');

            // initialise all datapickers
            $("input[id$='date']").each(function() {
                $(this).datetimepicker({
                    format: 'DD/MM/YYYY'
                });
            });

            $issueButton.click(function(e) {
                if(!$(this).hasClass('disabled')) {
                    $issueLicenceForm.submit();
                }
            });

            if($issueButton.hasClass('disabled')) {
                $issueButton.tooltip({});
            }

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