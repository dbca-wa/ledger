define(['jQuery', 'bootstrap-datetimepicker'], function($) {
    return {
        initialise: function() {
            var $issueLicenceForm = $('#issueLicenceForm'),
                $issueButton = $('#issue');

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
        }
    }
});