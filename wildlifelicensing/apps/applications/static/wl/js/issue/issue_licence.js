define(['jQuery', 'bootstrap-datetimepicker'], function($) {
    return {
        initialise: function() {
            var $issueLicenceForm = $('#issueLicenceForm');

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
        }
    }
});