define([
    'jQuery',
    'datatables.net',
    'datatables.bootstrap',
    'datatables.datetime',
    'bootstrap-3-typeahead'
], function ($) {
    "use strict";

    function initSpeciesFields($parent) {
        var $species_fields = $parent.find('input[data-species]');
        if ($species_fields.length > 0) {
            $species_fields.each(function () {
                var $node = $(this),
                    speciesType = $node.attr('data-species');
                $node.typeahead({
                    minLength: 3,
                    items: 'all',
                    source: function (query, process) {
                        var url = '/taxonomy/species_name?search=' + query;
                        if (speciesType) {
                            url += '&type=' + speciesType;
                        }
                        return $.get(url, function (data) {
                            return process(data);
                        });
                    }
                });
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