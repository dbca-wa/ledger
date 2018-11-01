/*
 * Name : Vue Validator
 * Author : Tawanda Nyakudjga
 * Date : November 2016
 * Description : A bootsrap and jquery form validation library
 **/

if (!window.$) {
    var $ = require('jquery');
} else {
    var $ = window.$;
}


var vd = module.exports = {
    addError: (field, errMsg) => {
        $(field).closest('.form-group').addClass('has-error');
        $(field).focus();
        $(field).select();
        $(field).addClass('tooltip-err');
        $(field).tooltip()
            .attr("data-original-title", errMsg)
        vd.errors.push(errMsg);
    },

    removeError: (field) => {
        $(field).removeClass('tooltip-err');
        $(field).closest('.form-group').removeClass('has-error');
    },

    isNotEmpty: (field) => {
        var inputStr = $(field).val();
        vd.removeError(field);
        if (inputStr == "" || inputStr == null) {
            var errMsg = $(field).attr('data-error-msg') ? $(field).attr('data-error-msg') : "Field is required";
            vd.addError(field, errMsg);
            return false;
        }
        return true;

    },
    isNumber: (field) => {
        if (isNotEmpty(field)) {
            var inputStr = field.value;
            vd.removeError(field);
            for (var i = 0; i < inputStr.length; i++) {
                var oneChar = inputStr.substring(i, i + 1);
                if (oneChar < "0" || oneChar > "9") {
                    var errMsg = $(field).attr('data-error-msg') ? $(field).attr('data-error-msg') : "Field is not a number";
                    vd.addError(field, errMsg);
                    vd.errors.push(errMsg);
                    return false;
                }
            }
            if (field.value.length < 9) {
                var errMsg = $(field).attr('data-error-msg') ? $(field).attr('data-error-msg') : "Field is not a number";
                vd.addError(field, errMsg);
                vd.errors.push(errMsg);
                return false;
            }
            return true;
        }
        return false;
    },

    validate: (form) => {
        vd.errors = [];
        vd.isValid = true;
        $('.tooltip-err').tooltip("destroy");
        var fields = $(form).find(':input');
        $.each(fields, function(i, field) {
            if ($(field).attr('required') == 'required' || $(field).attr('required') == 'true') {
                if (!vd.isNotEmpty(field)) {
                    vd.isValid = false;
                }
            }
            if ($(field).attr('number')) {
                if (!vd.isNumber(field)) {
                    vd.isValid = false;
                }
            }
        });
        return vd;
    },
    errors: Array(),
    isValid: true
}
exports.formValidate = vd;