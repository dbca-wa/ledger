define(
    [
        'jQuery',
        'bootstrap.treeView'  // jquery plugin. Just for side-effects.
    ],
    function ($) {

        "use strict";

        return function (options) {
            var defaults = {
                treeSelector: '#applications-table',
                treeData: []
            };

            options = $.extend({}, defaults, options);
            $(function () {
                var $tree = $(options.treeSelector);
                $tree.treeview(
                    {
                        data: options.treeData,
                        showBorder: false,
                        enableLinks: true,
                        expandIcon: 'glyphicon glyphicon-arrow-down',
                        collapseIcon: 'glyphicon glyphicon-arrow-up',
                        emptyIcon: 'glyphicon glyphicon-minus',
                        highlightSelected: true,
                        onhoverColor: '#FFFFFF',
                        showTags: true
                    });
            });
        };
    }
);