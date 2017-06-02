define(['jQuery', 'js/wl.bootstrap-treeview'], function ($) {
    "use strict";

    function _convertToSlug(text) {
        return text.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'');
    }

    function _initCategories(categories) {
        $.each(categories, function(index, value) {
            var $tree = $('#' + _convertToSlug(value.name));

            $tree.treeview({
                data: value.licence_types,
                color: '#337ab7',
                levels: 1,
                showBorder: false,
                enableLinks: true,
                expandIcon: 'glyphicon glyphicon-triangle-right',
                collapseIcon: 'glyphicon glyphicon-triangle-bottom',
                nodeIcon: '',
                highlightSelected: false,
                onhoverColor: '#FFFFFF'
            }).on('nodeSelected', function(event, data) {
                if(data.href === undefined) {
                    $(this).treeview('toggleNodeExpanded', [ data.nodeId, { levels: 1, silent: true } ]);

                    // need to unselectNode (without triggering events) so that it will respond to the next
                    // click on itself (i.e. next click yields another selection, rather than deselection)
                    $(this).treeview('unselectNode', [ data.nodeId, { silent: true } ]);
                }
            });
        });
    }

    function _initNavigateAway(deleteApplicationSessionURL, applicationId, csrfToken, categoryContainerSelector) {
        var $categoryContainer = $(categoryContainerSelector),
            isLinkLicenceSelection = false;

        $('a').click(function(e) {
            isLinkLicenceSelection = $categoryContainer.find(this).length > 0;
        });

        window.onunload = function (e) {
            if(!isLinkLicenceSelection) {
                $.post(deleteApplicationSessionURL, {
                        applicationId: applicationId,
                        csrfmiddlewaretoken: csrfToken
                    }
                );
            }
        };
    }

    function _init(options) {
        _initCategories(options.categories);
        _initNavigateAway(options.deleteApplicationSessionURL, options.applicationId, options.csrfToken,
                options.categoryContainerSelector);
    }

    return {
        init: _init
    }
});