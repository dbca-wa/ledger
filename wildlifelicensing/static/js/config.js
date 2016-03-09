require.config({
    baseUrl: '/static',
    paths: {
        'jQuery': 'https://static.dpaw.wa.gov.au/static/libs/jquery/2.2.0/jquery.min',
        'bootstrap': 'https://static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/js/bootstrap.min',
        'handlebars': 'https://static.dpaw.wa.gov.au/static/libs/handlebars.js/4.0.5/handlebars.amd.min'
    },
    shim: {
        'jQuery': {
            exports: '$'
        },
        'bootstrap': {
            deps: ['jQuery']
        }
    }
});