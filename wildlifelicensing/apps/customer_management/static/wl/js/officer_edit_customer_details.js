define([
    'jQuery'
], function ($) {
    "use strict";

    function init() {
        var $uploadID = $('#upload_id'),
            $formID = $('#id_form'),
            $uploadSenior = $('#upload_senior_card'),
            $formSenior = $('#senior_form');

        $uploadID.on('click', function (e) {
            var $fileNode = $('<input class="top-buffer hidden" id="id" name="id" type="file" multiple>');
            e.preventDefault();
            $fileNode.change(function (e) {
                $formID.append($fileNode);
                $formID.submit();
            });
            $fileNode.click();
        });

        $uploadSenior.on('click', function (e) {
            var $fileNode = $('<input class="top-buffer hidden" id="senior_card" name="senior_card" type="file" multiple>');
            e.preventDefault();
            $fileNode.change(function (e) {
                $formSenior.append($fileNode);
                $formSenior.submit();
            });
            $fileNode.click();
        });
    }

    return {
        init: init
    };
});