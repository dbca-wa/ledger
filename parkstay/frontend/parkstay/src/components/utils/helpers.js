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
    }
};
