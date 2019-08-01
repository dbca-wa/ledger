define([
    'jQuery',
    'js/return_table',
    'bootstrap'
], function ($, returnTable) {
    'use strict';
    var amendmentRequests;

    function prepareAmendmentRequestsPopover ($showPopover) {
        var $content = $('<ul>').addClass('popover-checklist'),
            popover = $showPopover.data('bs.popover');
        $.each(amendmentRequests, function (index, value) {
            $content.append($('<li>').text(value.reason));
        });
        // check if popover created yet
        if (popover === undefined) {
            $showPopover.popover({container: 'body', content: $content.prop('outerHTML'), html: true});
            $showPopover.removeClass('hidden');
        } else {
            popover.options.content = $content;
        }
    }

    return {
        init: function (options) {
            var $requestAmendmentBtn = $(options.selectors['requestAmendmentBtn']),
                $requestAmendmentModal = $(options.selectors['requestAmendmentModal']),
                $requestAmendmentForm = $requestAmendmentModal.find('form'),
                $showAmendmentRequests = $(options.selectors['showAmendmentRequests']);

            amendmentRequests = options.data['amendmentRequests'];
            returnTable.initTables();
            //  Events
            $requestAmendmentBtn.on('click', function () {
                $requestAmendmentModal.modal('show');
            });
            $requestAmendmentForm.submit(function (e) {
                $.ajax({
                    type: $(this).attr('method'),
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function (data) {
                        $requestAmendmentModal.modal('hide');
                        if (data.hasOwnProperty('amendment_request')) {
                            amendmentRequests.push(data['amendment_request']);
                            prepareAmendmentRequestsPopover($showAmendmentRequests);
                        }
                    },
                    error: function (data) {
                        window.console.log('error', data);
                    }
                });
                e.preventDefault();
            });

            // amendments
            if (amendmentRequests.length > 0) {
                prepareAmendmentRequestsPopover($showAmendmentRequests);
                $showAmendmentRequests.removeClass('hidden');
            }
        }
    };
});