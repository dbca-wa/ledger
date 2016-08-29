define(['jQuery', 'select2'], function ($) {
    "use strict";

    return {
        init: function() {
            var $searchCustomer = $('#searchCustomer');

            $searchCustomer.select2({
                minimumInputLength: 2,
                ajax: {
                    url: '/search_customers',
                    dataType: 'json',
                    quietMillis: 250,
                    data: function (term, page) {
                        return {
                            q: term,
                        };
                    },
                    results: function (data, page) {
                        return { results: data };
                    },
                    cache: true
                }
            });

            $searchCustomer.on('change', function(e) {
                $('#select').prop('disabled', false);
            });
        }
    }
});