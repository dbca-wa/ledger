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
                $regionSelect = $issueLicenceForm.find('select'),
                $addAttachment = $('#add_attachment');

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

            $addAttachment.on('click', function (e) {
                var inputNode = $('<input class="top-buffer" id="id_attach" name="attachments" type="file" multiple>');
                e.preventDefault();
                $(e.target).parent().append(inputNode);
                inputNode.click();

            });

        }
    };
});