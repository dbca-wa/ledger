define(['jQuery', 'js/wl.dataTable'], function($, dataTable) {
    return {
        initDocumentsTable: function(tableSelector, data, editURL,deleteURL) {
            dataTable.initTable($(tableSelector), {
                paging: false,
            }, [
                {title: 'Name', data: 'name'},
                {title: 'Description', data: 'description'},
                {title: 'File', data: 'file'},
                {title: 'Uploaded Date', data: 'uploaded_date'},
                {title: 'Action', data: 'id', render: function(data, type, row) {
                	return '<a href="' + editURL + data + '">Edit</a> &nbsp;&nbsp;<a href="' + deleteURL + data + '">Delete</a>';
                }}
            ]).populate(data);
        }
    }
});
