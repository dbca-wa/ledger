define([
    'jQuery',
    'bootstrap-datetimepicker',
    'select2',
    'bootstrap-3-typeahead'
], function($) {
    "use strict";

    return {
        initialise: function() {
            var $issueLicenceForm = $('#issueLicenceForm'),
                $issueButton = $('#issue'),
                $regionSelect = $issueLicenceForm.find('#id_regions'),
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
                var url = this.href + '?' + $issueLicenceForm.serialize();
                window.open(url);
                return false;
            });

            $regionSelect.select2({
                placeholder: "Select applicable regions."
            });
            $regionSelect.removeClass('hidden');

            $('.species').each(function() {
                var speciesTypeArg = '';
                if($(this).attr('data-species-type') !== undefined) {
                    speciesTypeArg = '&type=' + $(this).attr('data-species-type');
                }

                // initialise species typeahead
                $(this).typeahead({
                    minLength: 3,
                    items: 'all',
                    source: function (query, process) {
                        return $.get('/taxonomy/species_name?search=' + query + speciesTypeArg, function (data) {
                            return process(data);
                        });
                    }
                });
            });

            $addAttachment.on('click', function (e) {
                var inputNode = $('<input class="top-buffer" id="id_attach" name="attachments" type="file" multiple>');
                e.preventDefault();
                $(e.target).parent().append(inputNode);
                inputNode.click();
            });

        }
    };
});