define(
    [
        'jQuery',
        'bootstrap.treeView'  // jquery plugin. Just for side-effects.
    ],
    function ($) {

        function getData() {
            return [
                {
                    text: "Pending applications",
                    tags: ['15'],
                    href: '/dashboard/tables',
                    nodes: [
                        {
                            text: "Reg3",
                            href: '/dashboard/tables/#applications',
                            tags: ['5']
                        },
                        {
                            text: "Reg17",
                            href: '/dashboard/tables/#applications',
                            tags: ['10'],
                            nodes: [
                                {
                                    text: 'Graham Thompson',
                                    href: '/dashboard/tables/#applications',
                                    tags: ['9']
                                },
                                {
                                    text: 'Pauline Goodreid',
                                    href: '/dashboard/tables/#applications',
                                    tags: ['1']
                                }
                            ]
                        }
                    ]
                },
                {
                    text: "Overdue returns",
                    tags: ['6'],
                    href: '/dashboard',
                    state: {
                        expanded: false
                    },
                    nodes: [
                        {
                            text: "Reg3",
                            href: '/dashboard/tables/#returns',
                            tags: ['1']
                        },
                        {
                            text: "Reg17",
                            href: '/dashboard/tables/#returns',
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