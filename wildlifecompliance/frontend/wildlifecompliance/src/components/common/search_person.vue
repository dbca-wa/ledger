<template lang="html">
    <div class="">
        <input :id="elementId" :class="classNames" :readonly="!isEditable" />
    </div>
</template>

<script>
import Awesomplete from "awesomplete";
import $ from "jquery";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";

export default {
    name: "search-person",
    data: function(){
        let vm = this;
        vm.awesomplete_obj = null;

        return {

        }
    },
    props: {
        elementId: {
            required: true
        },
        classNames: {
            required: false
        },
        maxItems: {
            required: false,
            default: 10
        },
        search_type: {
            required: false,
            default: 'individual'
        },
        isEditable: {
            required: false,
            default: true
        }
    },
    methods: {
        clearInput: function(){
            document.getElementById(this.elementId).value = "";
        },
        markMatchedText(original_text, input) {
            let ret_text = original_text.replace(new RegExp(input, "gi"), function( a, b) {
                return "<mark>" + a + "</mark>";
            });
            return ret_text;
        },
        initAwesomplete: function() {
            let vm = this;

            let element_search = document.getElementById(vm.elementId);
            vm.awesomplete_obj = new Awesomplete(element_search, {
                maxItems: vm.maxItems,
                sort: false,
                filter: () => {
                    return true;
                }, 
                item: function(text, input) {
                    let ret = Awesomplete.ITEM(text, ""); // Not sure how this works but this doesn't add <mark></mark>
                    return ret;
                },
                data: function(item, input) {
                    if (vm.search_type == "individual") {
                        let f_name = item.first_name ? item.first_name : "";
                        let l_name = item.last_name ? item.last_name : "";
            
                        let full_name = [f_name, l_name].filter(Boolean).join(" ");
                        let email = item.email ? "E:" + item.email : "";
                        let p_number = item.phone_number ? "P:" + item.phone_number : "";
                        let m_number = item.mobile_number ? "M:" + item.mobile_number : "";
                        let dob = item.dob ? "DOB:" + item.dob : "DOB: ---";
            
                        let full_name_marked = "<strong>" + vm.markMatchedText(full_name, input) + "</strong>";
                        let email_marked = vm.markMatchedText(email, input);
                        let p_number_marked = vm.markMatchedText(p_number, input);
                        let m_number_marked = vm.markMatchedText(m_number, input);
                        let dob_marked = vm.markMatchedText(dob, input);
            
                        let myLabel = [
                            full_name_marked,
                            email_marked,
                            p_number_marked,
                            m_number_marked,
                            dob_marked
                        ].filter(Boolean).join("<br />");
                        myLabel = "<div data-item-id=" + item.id + ' data-type="individual">' + myLabel + "</div>";
            
                        return {
                            label: myLabel, // Displayed in the list below the search box
                            value: [full_name, dob].filter(Boolean).join(", "), // Inserted into the search box once selected
                            id: item.id
                        };
                    } else {
                        let name = item.name ? item.name : "";
                        let abn = item.abn ? "ABN:" + item.abn : "";
            
                        let name_marked = "<strong>" + vm.markMatchedText(name, input) + "</strong>";
                        let abn_marked = vm.markMatchedText(abn, input);
            
                        let myLabel = [name_marked, abn_marked].filter(Boolean).join("<br />");
                        myLabel = "<div data-item-id=" + item.id + ' data-type="organisation">' + myLabel + "</div>";
            
                        return {
                            label: myLabel,
                            value: [name, abn].filter(Boolean).join(", "),
                            id: item.id
                        };
                    }
                }
            });
            $(element_search)
            .on("keyup", function(ev) {
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90) || (96 <= keyCode && keyCode <= 105) || keyCode == 8 || keyCode == 46) {
                    vm.search_offender(ev.target.value);
                    return false;
                }
            })
            .on("awesomplete-selectcomplete", function(ev) {
                ev.preventDefault();
                ev.stopPropagation();
                return false;
            })
            .on("awesomplete-select", function(ev) {
                let origin = $(ev.originalEvent.origin);
                let originTagName = origin[0].tagName;
                if (originTagName != "DIV") {
                    // Assuming origin is a child element of <li>
                    origin = origin.parent();
                }
                let data_item_id = origin[0].getAttribute("data-item-id");
                let data_type = origin[0].getAttribute("data-type");

                vm.$emit('person-selected', { id: data_item_id, data_type: data_type });
            });
        },
        search_offender(searchTerm){
            var vm = this;
            let suggest_list_offender = [];
            suggest_list_offender.length = 0;
            vm.awesomplete_obj.list = [];

            /* Cancel all the previous requests */
            if (vm.ajax_for_offender != null) {
                vm.ajax_for_offender.abort();
                vm.ajax_for_offender = null;
            }

            let search_url = "";
            if (vm.search_type == "individual") {
                search_url = "/api/search_user/?search=";
            } else {
                search_url = "/api/search_organisation/?search=";
            }

            vm.ajax_for_offender = $.ajax({
                type: "GET",
                url: search_url + searchTerm,
                success: function(data) {
                    if (data && data.results) {
                        let persons = data.results;
                        let limit = Math.min(vm.maxItems, persons.length);
                        for (var i = 0; i < limit; i++) {
                        suggest_list_offender.push(persons[i]);
                        }
                    }
                    vm.awesomplete_obj.list = suggest_list_offender;
                    vm.awesomplete_obj.evaluate();
                },
                error: function(e) {}
            });
        },
    },
    created: function() {
        let vm = this;
        vm.$nextTick(()=>{
            vm.initAwesomplete();
        });
    }
}
</script>

<style>
</style>
