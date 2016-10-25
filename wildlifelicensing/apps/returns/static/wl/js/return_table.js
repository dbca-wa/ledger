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

    function validateSpeciesField($field, speciesType) {
        // Rules: if only one species is returned from the api we consider the name to be valid.
        // Trick: the species can be recorded as: species_name (common name) in this case the search will fail
        // (species_name or common name but not both). We get rid of anything in parenthesis.
        var value = $field.val();
        if (value) {
            value = value.replace(/\s?\(.*\)/, '');
            querySpecies(speciesType, value.trim(), function (data) {
                var valid = data && data.length === 1;
                setSpeciesValid($field, valid);
            });
        }
    }

    function initSpeciesFields($parent) {
        var $species_fields = $parent.find('input[data-species]');
        if ($species_fields.length > 0) {
            $species_fields.each(function () {
                var $field = $(this),
                    speciesType = $field.attr('data-species'),
                    value;
                $field.typeahead({
                    minLength: 2,
                    items: 'all',
                    source: function (query, process) {
                        querySpecies(speciesType, query, function (data) {
                            return process(data);
                        });
                    }
                });
                value = $field.val();
                if (value) {
                    // already some data. We try to validate.
                    validateSpeciesField($field, speciesType);
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