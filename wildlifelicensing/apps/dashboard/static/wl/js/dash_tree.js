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
                        expandIcon: 'glyphicon glyphicon-plus',
                        collapseIcon: 'glyphicon glyphicon-minus',
                        emptyIcon: '',
                        highlightSelected: true,
                        onhoverColor: '#FFFFFF',
                        showTags: true
                    });
            });
        };
    }
);