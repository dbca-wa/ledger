define(['jQuery', 'datatables.net', 'datatables.bootstrap', 'datatables.datetime'], function ($) {

    return {
        initTables: function() {
            var $tables = $('.return-table'),
                $curationForm = $('#curationForm');

            $tables.DataTable({
                paging: false,
                ordering: false,
                searching: false,
                info: false
            });

            $('.add-return-row').click(function() {
                var $tbody = $(this).parent().find('table').find('tbody'),
                    $row = $tbody.find('tr:first');

                // clone the top row
                $rowCopy = $row.clone();

                // clear any values/errors in the cloned row
                $rowCopy.find('input').val('');
                $rowCopy.find('.text-danger').parent().remove();

                // append cloned row
                $tbody.append($rowCopy);
            });

            $('#accept').click(function() {
                $curationForm.append($('<input>').attr('name', 'accept').addClass('hidden'));
                $curationForm.submit();
            })

            $('#decline').click(function() {
                $curationForm.append($('<input>').attr('name', 'decline').addClass('hidden'));
                $curationForm.submit();
            })
        }
    }
});