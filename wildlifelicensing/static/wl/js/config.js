require.config({
    baseUrl: '/static/wl',
    paths: {
        'jQuery': 'https://static.dpaw.wa.gov.au/static/libs/jquery/2.2.0/jquery.min',
        'bootstrap': 'https://static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'bootstrap-datetimepicker': 'https://static.dpaw.wa.gov.au/static/libs/bootstrap-datetimepicker/4.7.14/js/bootstrap-datetimepicker.min',
        'bootstrap-typeahead': 'https://static.dpaw.wa.gov.au/static/libs/bootstrap-3-typeahead/4.0.0/bootstrap3-typeahead.min',
        'handlebars': 'https://static.dpaw.wa.gov.au/static/libs/handlebars.js/4.0.5/handlebars.amd.min',
        'moment': 'https://static.dpaw.wa.gov.au/static/libs/moment.js/2.9.0/moment.min',
        'parsley': 'https://static.dpaw.wa.gov.au/static/libs/parsley.js/2.3.5/parsley.min',
        'datatables.net': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/jquery.dataTables.min',
        'datatables.bootstrap': 'http://static.dpaw.wa.gov.au/static/libs/datatables/1.10.10/js/dataTables.bootstrap.min',
        'lodash':'http://static.dpaw.wa.gov.au/static/libs/lodash.js/4.5.1/lodash.min',
        'bootstrap.select': 'http://static.dpaw.wa.gov.au/static/libs/bootstrap-select/1.9.4/js/bootstrap-select.min',
        'bootstrap.treeView': 'http://static.dpaw.wa.gov.au/static/libs/bootstrap-treeview/1.2.0/bootstrap-treeview.min'
    },
    shim: {
        'jQuery': {
            exports: '$'
        },
        'bootstrap': {
            deps: ['jQuery']
        },
        'bootstrap-datetimepicker': {
            deps: ['jQuery', 'bootstrap', 'moment']
        },
        'bootstrap-typeahead': {
            deps: ['jQuery', 'bootstrap']
        },
        'parsley': {
            deps: ['jQuery']
        },
        'datatables.net': {
            deps: ['jQuery']
        },
        'datatables.bootstrap': {
            deps: ['jQuery']
        },
        'bootstrap.select': {
            deps: ['jQuery']
        },
        'bootstrap.treeView': {
            deps: ['bootstrap']
        }
    }
});
