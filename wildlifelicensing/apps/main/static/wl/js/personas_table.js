define(['jQuery', 'js/wl.dataTable'], function($, dataTable) {
    return {
        initPersonasTable: function(tableSelector, data, editURL) {
            dataTable.initTable($(tableSelector), {
                paging: false,
            }, [
                {title: 'Display Name', data: 'name'},
                {title: 'Email', data: 'email'},
                {title: 'Institution', data: 'institution'},
                {title: 'Postal Address', data: 'postal_address.search_text'},
                {title: 'Action', data: 'id', render: function(data, type, row) {
                	return '<a href="' + editURL + data + '">Edit</a>';
                }}
            ]).populate(data);
        }
    }
});