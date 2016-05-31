define(['jQuery', 'datatables.net', 'datatables.bootstrap', 'datatables.datetime'], function ($) {

    return {
        initTables: function() {
            var $tables = $('.return-table');

            $tables.DataTable({
                paging: false,
                ordering: false,
                searching: false,
                info: false
            });

            $('.add-return-row').click(function() {
                var $tbody = $(this).parent().find('table').find('tbody'),
                    $row = $tbody.find('tr:first');

                $rowCopy = $row.clone();
                $rowCopy.find('input').val('');
                $tbody.append($rowCopy);
            });

            $('#conclude').click(function() {
                $('form').submit();
            })
        }
    }
});