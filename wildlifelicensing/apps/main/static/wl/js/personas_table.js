define(['jQuery', 'js/wl.dataTable'], function($, dataTable) {
    return {
        initPersonasTable: function(tableSelector, data) {
            dataTable.initTable($(tableSelector), {
                paging: false,
                fnRowCallback: function( nRow, aData, iDisplayIndex ) {
                    $(nRow).click(function() {
                        document.location.href = "/personas/edit/" + aData.id;
                    });
                },
            }, [
                {title: 'Display Name', data: 'name'},
                {title: 'Email', data: 'email'},
                {title: 'Institution', data: 'institution'},
                {title: 'Postal Address', data: 'postal_address.search_text'}
            ]).populate(data);
        }
    }
});