define(
    'js/officers_dashboard_tree',
    [
        'jQuery',
        'bsTreeView'  // jquery plugin. Just for side-effects.
    ],
    function ($) {

        function getData() {
            return [
                {
                    text: "Pending applications",
                    tags: ['15'],
                    href: '/officers/dashboard',
                    nodes: [
                        {
                            text: "Reg3",
                            href: '/officers/dashboard',
                            tags: ['5']
                        },
                        {
                            text: "Reg17",
                            href: '/officers/dashboard',
                            tags: ['10'],
                            nodes: [
                                {
                                    text: 'Graham Thompson',
                                    href: '/officers/dashboard',
                                    tags: ['9']
                                },
                                {
                                    text: 'Pauline Goodreid',
                                    href: '/officers/dashboard',
                                    tags: ['1']
                                }
                            ]
                        }
                    ]
                },
                {
                    text: "Pending returns",
                    tags: ['6'],
                    href: '/officers/dashboard',
                    state: {
                        expanded: false
                    },
                    nodes: [
                        {
                            text: "Reg3",
                            href: '/officers/dashboard',
                            tags: ['1']
                        },
                        {
                            text: "Reg17",
                            href: '/officers/dashboard',
                            tags: ['5']
                        }
                    ]
                }
            ];
        }

        return function (treeSelector) {
            $(function () {
                var $tree = $(treeSelector);
                $tree.treeview(
                    {
                        data: getData(),
                        showBorder: false,
                        enableLinks: true,
                        emptyIcon: 'glyphicon glyphicon-stop',
                        showTags: true
                    });
                $tree.treeview('collapseAll', {silent: true});
            });
        }
    }
);