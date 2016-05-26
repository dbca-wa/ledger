define(['jQuery', 'datatables.net', 'datatables.bootstrap', 'datatables.datetime'], function ($) {

    return {
        initTable: function(tableSelector) {
            var $table = $(tableSelector),
                $tbody = $table.find('tbody'),
                $row = $tbody.find('tr:first'),
                table = $table.DataTable({
                    paging: false,
                    ordering: false,
                    searching: false,
                    info: false
                });

            $('#addRow').click(function() {
                $rowCopy = $row.clone();
                $rowCopy.find('input').val('');
                $tbody.append($rowCopy);
            });
        }
    }
});