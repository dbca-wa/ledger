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
                    text: "Parent 1",
                    nodes: [
                        {
                            text: "Child 1",
                            nodes: [
                                {
                                    text: "Grandchild 1"
                                },
                                {
                                    text: "Grandchild 2"
                                }
                            ]
                        },
                        {
                            text: "Child 2"
                        }
                    ]
                },
                {
                    text: "Parent 2"
                },
                {
                    text: "Parent 3"
                },
                {
                    text: "Parent 4"
                },
                {
                    text: "Parent 5"
                }
            ];
        }

        return function (treeSelector) {
            $(function () {
                $(treeSelector).treeview({data: getData()});
            });
        }
    }
);