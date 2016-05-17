define(['jQuery', 'js/wl.dataTable'], function($, dataTable) {
    return {
        initProfilesTable: function(tableSelector, data, editURL) {
            dataTable.initTable($(tableSelector), {
                paging: false,
            }, [
                {title: 'Display Name', data: 'name'},
                {title: 'Email', data: 'email'},
                /*
                {title: 'Auth Identity', data: 'auth_identity',render:function(data,type,row) {
                    if (data) {
                        return '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span'
                    } else {
                        return '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span'
                    }
                }},
                */
                {title: 'Institution', data: 'institution'},
                {title: 'Postal Address', data: 'postal_address.search_text'},
                {title: 'Action', data: 'id', render: function(data, type, row) {
                	return '<a href="' + editURL + data + '">Edit</a>';
                }}
            ]).populate(data);
        }
    }
});
