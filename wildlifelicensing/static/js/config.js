require.config({
    baseUrl: '/static',
    paths: {
        'jQuery': 'https://static.dpaw.wa.gov.au/static/libs/jquery/2.2.0/jquery.min',
        'bootstrap': 'https://static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'datatables.net': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/jquery.dataTables.min',
        'datatables.bootstrap': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/dataTables.bootstrap.min',
        'lodash':'http://static.dpaw.wa.gov.au/static/libs/lodash.js/4.5.1/lodash.min',
        'bootstrapSelect': 'http://static.dpaw.wa.gov.au/static/libs/bootstrap-select/1.9.4/js/bootstrap-select.min',
        'bsTreeView': 'http://static.dpaw.wa.gov.au/static/libs/bootstrap-treeview/1.2.0/bootstrap-treeview.min',
        'moment': 'http://static.dpaw.wa.gov.au/static/libs/moment.js/2.9.0/moment.min',
        //'datatables.sort.moment': 'cdn.datatables.net/plug-ins/1.10.11/sorting/datetime-moment'
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
        'datatables.bootstrap': {
            deps: ['jQuery']
        },
        'bootstrapSelect': {
            deps: ['jQuery']
        },
        'bsTreeView': {
            deps: ['bootstrap']
        },
        //'datatables.sort.moment': {
        //    deps: ['jQuery', 'moment']
        //}

    }
});