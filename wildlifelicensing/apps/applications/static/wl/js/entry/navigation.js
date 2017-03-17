define(['jQuery'], function($) {
    return {setupNavigateAway: function(message) {
        var $lastClicked;

        $('a, :button').click(function(e) {
            $lastClicked = $(this); 
        });

        window.onbeforeunload = function (e) {
            // if we haven't been passed the event get the window.event
            e = e || window.event;

            // if link is for current page or has data-entry-link
            if(!$lastClicked.attr('href') ||
               ($lastClicked.attr('href').indexOf(window.location.href) > -1 ||
                $lastClicked.attr('data-entry-link'))) {
                return;
            };

            // Note: You cannot change the custom message for onbeforeunload in Chrome / Firefox
            
            // for IE6-8 and Firefox prior to version 4
            if (e) {
                e.returnValue = message;
            }

            // for Safari, IE8+ and Opera 12+
            return message;
        };
    }}
});