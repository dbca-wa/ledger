require(['jQuery', 'bootstrap'], function ($) { // bootstrap returns nothing so must go last in required modules
    $('body').on('click', function (e) {
        $('[data-toggle="popover"]').each(function () {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $(e.target).parents('.popover').length === 0 
                    && $.contains(document, e.target)) {
                $(this).popover('hide');
            }
        });
    });

    // fix for bootstrap 3.3.6 bug for when popovers don't reshow after hiding via popover('hide).
    // see https://github.com/twbs/bootstrap/issues/16732
    $('body').on('hidden.bs.popover', function (e) {
        $(e.target).data("bs.popover").inState.click = false;
    });
});