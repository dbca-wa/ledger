define(['jQuery', 'bootstrap.treeView'], function ($) {
    "use strict";

    function _convertToSlug(text) {
        return text.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'');
    }

    function _init(categories) {
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

    return {
        init: _init
    }
});