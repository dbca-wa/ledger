require.config({
    baseUrl: '/static/wl',
    paths: {
        'jQuery': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.0/jquery.min',
        'bootstrap': '//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'bootstrap-datetimepicker': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.37/js/bootstrap-datetimepicker.min',
        'select2': '//cdnjs.cloudflare.com/ajax/libs/select2/3.5.4/select2.min',
        'handlebars': '//cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.0.5/handlebars.amd',
        'handlebars.runtime': '//cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.0.5/handlebars.runtime.amd',
        'moment': '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.9.0/moment.min',
        'parsley': '//cdnjs.cloudflare.com/ajax/libs/parsley.js/2.3.5/parsley.min',
        'datatables.net': '//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.11/js/jquery.dataTables.min',
        'datatables.bootstrap': '//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.11/js/dataTables.bootstrap.min',
        'lodash':'//cdnjs.cloudflare.com/ajax/libs/lodash.js/4.5.1/lodash.min',
        'bootstrap.treeView': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-treeview/1.2.0/bootstrap-treeview.min',
        'bootstrap-3-typeahead': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-3-typeahead/4.0.1/bootstrap3-typeahead.min',
        'datatables.datetime': '//cdn.datatables.net/plug-ins/1.10.11/sorting/datetime-moment'
    },
    map: {
        '*': {
            'jquery': 'jQuery',
            'datatables': 'datatables.net'
        }
    },
    shim: {
        'jQuery': {
            exports: '$'
        },
        'lodash': {
            exports: '_'
        },
        'bootstrap': {
            deps: ['jQuery']
        },
        'bootstrap-datetimepicker': {
            deps: ['jQuery', 'bootstrap', 'moment']
        },
        'select2': {
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
        'bootstrap.treeView': {
            deps: ['bootstrap']
        },
        'bootstrap-3-typeahead': {
            deps: ['bootstrap']
        }
    }
});
