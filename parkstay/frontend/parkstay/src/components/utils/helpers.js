module.exports = {
    apiError: function(resp){
        var error_str = '';
        if (resp.status === 400) {
            try {
                obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[\[\]"]/g,'');
            } catch(e) {
                error_str = resp.responseText.replace(/[\[\]"]/g,'');
            }
        }
        else if ( resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        return error_str;
    },
    goBack:function(vm){
        vm.$router.go(window.history.back());
    },
    getCookie: function(name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1).trim() === (name + '=')) {
                    value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return value;
    },
    namePopover:function ($,vmDataTable) {
        vmDataTable.on('mouseover','.name_popover',function (e) {
            $(this).popover('show');
            $(this).on('mouseout',function () {
                $(this).popover('hide');
            });
        });
    }
};
