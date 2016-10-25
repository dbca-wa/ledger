define([
    'jQuery',
    'datatables.net',
    'datatables.bootstrap',
    'datatables.datetime',
    'bootstrap-3-typeahead'
], function ($) {
    "use strict";

    function querySpecies(speciesType, search, callback) {
        var url = '/taxonomy/species_name',
            params = {},
            promise;
        if (speciesType) {
            params.type = speciesType;
        }
        if (search) {
            params.search = search;
        }
        url += '?' + $.param(params);
        promise = $.get(url);
        if (typeof callback === 'function') {
            promise.then(callback);
        }
        return promise;
    }

    function setSpeciesValid($field, valid) {
        var validClass = 'text-success';
        if (valid) {
            $field.addClass(validClass);
        } else {
            $field.removeClass(validClass);
        }
    }

    function initSpeciesFields($parent) {
        var $species_fields = $parent.find('input[data-species]');
        if ($species_fields.length > 0) {
            $species_fields.each(function () {
                var $node = $(this),
                    speciesType = $node.attr('data-species'),
                    value;
                $node.typeahead({
                    minLength: 3,
                    items: 'all',
                    source: function (query, process) {
                        querySpecies(speciesType, query, function (data) {
                            return process(data);
                        });
                    }
                });
                value = $node.val();
                if (value) {
                    // already some data. We try to validate.
                    // Rules: if only one species is returned from the api we consider the name to be valid.
                    querySpecies(speciesType, value, function (data) {
                        var valid = data && data.length === 1;
                        setSpeciesValid($node, valid);
                    });
                }
            });
        }
    }

    return {
        initTables: function () {
            var $tables = $('.return-table'),
                $curationForm = $('#curationForm');

            $tables.DataTable({
                paging: false,
                ordering: false,
                searching: false,
                info: false
            });

            initSpeciesFields($tables);

            $('.add-return-row').click(function () {
                var $tbody = $(this).parent().find('table').find('tbody'),
                    $row = $tbody.find('tr:first');
                // clone the top row
                var $rowCopy = $row.clone();

                // clear any values/errors in the cloned row
                $rowCopy.find('input').val('');
                $rowCopy.find('.text-danger').parent().remove();

                // append cloned row
                $tbody.append($rowCopy);
                initSpeciesFields($rowCopy);
            });

            $('#accept').click(function () {
                $curationForm.append($('<input>').attr('name', 'accept').addClass('hidden'));
                $curationForm.submit();
            });

            $('#decline').click(function () {
                $curationForm.append($('<input>').attr('name', 'decline').addClass('hidden'));
                $curationForm.submit();
            });
        }
    };
});