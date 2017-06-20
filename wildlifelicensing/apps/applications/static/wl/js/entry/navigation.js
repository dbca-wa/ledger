define(['jQuery'], function($) {
    return {
        init: function(message, applicationId, navigationElementSelector, contentContainerSelector, csrfToken) {
            var $contentContainer = $(contentContainerSelector),
                isExpectedNavigationAction = false;

            $(navigationElementSelector).click(function(e) {
                isExpectedNavigationAction = $contentContainer.find(this).length > 0;
            });

            window.onbeforeunload = function (e) {
                // if we haven't been passed the event get the window.event
                e = e || window.event;

                if(!isExpectedNavigationAction) {
                    // Note: You cannot change the custom message for onbeforeunload in Chrome / Firefox

                    // for IE6-8 and Firefox prior to version 4
                    if (e) {
                        e.returnValue = message;
                    }

                    // for Safari, IE8+ and Opera 12+
                    return message;
                }
            };

            window.onunload = function (e) {
                if(!isExpectedNavigationAction) {
                    $.ajax({
                        type: 'POST',
                        url: '/applications/delete-application-session/',
                        async: false,
                        data: { 
                            applicationId: applicationId,
                            csrfmiddlewaretoken: csrfToken
                        }
                    });
                }
            };
        }
    }
});