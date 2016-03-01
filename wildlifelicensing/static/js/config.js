require.config({
    baseUrl: '/static',
    paths: {
        'jQuery': 'https://static.dpaw.wa.gov.au/static/libs/jquery/2.2.0/jquery.min',
        'bootstrap': 'https://static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'datatables.net': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/jquery.dataTables.min',
        'dataTableBootstrap': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/dataTables.bootstrap.min',
        'lodash':'http://static.dpaw.wa.gov.au/static/libs/lodash.js/4.5.1/lodash.min',
        'bsTreeView': 'http://static.dpaw.wa.gov.au/static/libs/bootstrap-treeview/1.2.0/bootstrap-treeview.min'
    },
    shim: {
        'jQuery': {
            exports: '$'
        },
        'bootstrap': {
            deps: ['jQuery']
        },
        'datatables.net': {
            deps: ['jQuery']
        },
        'dataTableBootstrap': {
            deps: ['jQuery']
        },
        'bsTreeView': {
            deps: ['bootstrap']
        }
    }
});