define(['jQuery'], function($) {
    var edit_address = function(address_type,edit) {
        $("#" + address_type + "_address_section .panel-body :input").prop('disabled',!edit);
        if (edit) {
            $("#" + address_type + "_address_edit").html('<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>');
        } else {
            $("#" + address_type + "_address_edit").html('<span class="glyphicon glyphicon-edit" aria-hidden="true"></span>');
        }
    }

    var _residential_edit_status = false;
    var _postal_edit_status = false;
    var _billing_edit_status = false;
    return {
        init: function() {
            $("#residential_address_edit").click(
                function() {
                    _residential_edit_status = !_residential_edit_status;
                    edit_address("residential",_residential_edit_status);
                }
            );

            $("#postal_address_edit").click(
                function() {
                    _postal_edit_status = !_postal_edit_status;
                    edit_address("postal",_postal_edit_status);
                }
            );

            $("#billing_address_edit").click(
                function() {
                    _billing_edit_status = !_billing_edit_status;
                    edit_address("billing",_billing_edit_status);
                }
            );

            $("#residential_address_section .panel-body :input").each(function() {
                if ($(this).tagName == "input" || $(this).value().trim() != "") {
                    _residential_edit_status = true;
                }
            });

            $("#postal_address_section .panel-body :input").each(function() {
                if ($(this).tagName == "input" || $(this).value().trim() != "") {
                    _postal_edit_status = true;
                }
            });

            $("#billing_address_section .panel-body :input").each(function() {
                if ($(this).tagName == "input" || $(this).value().trim() != "") {
                    _billing_edit_status = true;
                }
            });

            edit_address("residential",_residential_edit_status);
            edit_address("postal",_postal_edit_status);
            edit_address("billing",_billing_edit_status);
        }
    }
});
