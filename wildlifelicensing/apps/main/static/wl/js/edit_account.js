define(['jQuery'], function($) {
    var choose_address_source_type = function(address_type,button) {
        if ($(button).hasClass("active")) {
            //already in active status
            return;
        }

        $("#" + address_type + "_address-source_types :button").removeClass("active");
        $(button).addClass("active");
        $("#" + address_type + "_address-source_type").val($(button).val());
        if ($(button).val() == "removed") {
            $("#" + address_type + "_address_panel #" + address_type + "_address_body").appendTo("#" + address_type + "_address_cache");
        } else if ($(button).val() == "added") {
            $("#" + address_type + "_address_cache #" + address_type + "_address_body").appendTo("#" + address_type + "_address_panel .panel-body");
        } else if ($(button).val() == "residential_address") {
            $("#" + address_type + "_address_panel #" + address_type + "_address_body").appendTo("#" + address_type + "_address_cache");
        } else if ($(button).val() == "postal_address") {
            $("#" + address_type + "_address_panel #" + address_type + "_address_body").appendTo("#" + address_type + "_address_cache");
        } 
    }
    return {
        init: function() {
            /* disable address maintenance feature
            $("#residential_address-source_types :button").click(
                function() {
                    choose_address_source_type("residential",this);
                }
            );

            $("#postal_address-source_types :button").click(
                function() {
                    choose_address_source_type("postal",this);
                }
            );

            $("#billing_address-source_types :button").click(
                function() {
                    choose_address_source_type("billing",this);
                }
            );
            //set initial status to "removed"
            $("#residential_address-source_types :button[value='removed']").addClass("active");
            $("#postal_address-source_types :button[value='removed']").addClass("active");
            $("#billing_address-source_types :button[value='removed']").addClass("active");
            $.each(["residential","postal","billing"],function(index,address_type){
                var source_type = $("#" + address_type + "_address-source_type").val();
                $("#" + address_type + "_address-source_types :button[value='" + source_type + "']").click();
            });
            */
            
        }

    }
});
