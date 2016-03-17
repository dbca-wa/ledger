require.config({
    baseUrl: '/static',
    paths: {
        'jQuery': 'https://static.dpaw.wa.gov.au/static/libs/jquery/2.2.0/jquery.min',
        'bootstrap': 'https://static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'bootstrap-datetimepicker': 'https://static.dpaw.wa.gov.au/static/libs/bootstrap-datetimepicker/4.7.14/js/bootstrap-datetimepicker.min',
        'select2': 'https://static.dpaw.wa.gov.au/static/libs/select2/3.5.4/select2.min',
        'handlebars': 'https://static.dpaw.wa.gov.au/static/libs/handlebars.js/4.0.5/handlebars.amd.min',
        'moment': 'https://static.dpaw.wa.gov.au/static/libs/moment.js/2.9.0/moment.min',
        'parsley': 'https://static.dpaw.wa.gov.au/static/libs/parsley.js/2.3.5/parsley.min'
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
        'select2': {
            deps: ['jQuery', 'bootstrap']
        },
        'parsley': {
            deps: ['jQuery']
        }
    }
});