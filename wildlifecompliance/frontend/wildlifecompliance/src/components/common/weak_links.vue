<template lang="html">
    <div class="">
        <input :id="elemId" :class="classNames" :readonly="!isEditable" />
    </div>
</template>

<script>
import Awesomplete from "awesomplete";
import $ from "jquery";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";

export default {
    name: "weak-links",
    data: function(){
        this.awesomplete_obj = null;

        return {
            elemId: 'create_weak_link_' + this._uid,
        }
    },
    props: {
        // This prop is not used any more.  Instead elemId in the data is used.
        //elementId: {
          //  required: false
        //},
        classNames: {
            required: false
        },
        maxItems: {
            required: false,
            default: 10
        },
        search_type: {
            required: false,
            //default: 'individual' // 'individual' or 'organisation'
                                  //  This variable can be changed dynamically, for example, by the selection of radio buttons
        },
        isEditable: {
            required: false,
            default: true
        }
    },
    methods: {
        clearInput: function(){
            document.getElementById(this.elemId).value = "";
        },
        setInput: function(weak_link_str){
            document.getElementById(this.elemId).value = weak_link_str;
        },
        markMatchedText(original_text, input) {
            let ret_text = original_text.replace(new RegExp(input, "gi"), function( a, b) {
                return "<mark>" + a + "</mark>";
            });
            return ret_text;
        },
        initAwesomplete: function() {

            let element_search = document.getElementById(this.elemId);
            this.awesomplete_obj = new Awesomplete(element_search, {
                maxItems: this.maxItems,
                sort: false,
                filter: () => {
                    return true;
                }, 
                item: function(text, input) {
                    let ret = Awesomplete.ITEM(text, ""); // Not sure how this works but this doesn't add <mark></mark>
                    return ret;
                },
                data: function(item, input) {
                    if (this.search_type == "individual") {
                        let f_name = item.first_name ? item.first_name : "";
                        let l_name = item.last_name ? item.last_name : "";
            
                        let full_name = [f_name, l_name].filter(Boolean).join(" ");
                        let email = item.email ? "E:" + item.email : "";
                        let p_number = item.phone_number ? "P:" + item.phone_number : "";
                        let m_number = item.mobile_number ? "M:" + item.mobile_number : "";
                        let dob = item.dob ? "DOB:" + item.dob : "DOB: ---";
            
                        let full_name_marked = "<strong>" + this.markMatchedText(full_name, input) + "</strong>";
                        let email_marked = this.markMatchedText(email, input);
                        let p_number_marked = this.markMatchedText(p_number, input);
                        let m_number_marked = this.markMatchedText(m_number, input);
                        let dob_marked = this.markMatchedText(dob, input);
            
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
            
                        let name_marked = "<strong>" + this.markMatchedText(name, input) + "</strong>";
                        let abn_marked = this.markMatchedText(abn, input);
            
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
                    this.search_available_object_identifiers(ev.target.value);
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

                // Emit an event so that the parent vue component can subscribe to the event: 'person-selected' 
                // and receive the data user selected.
                // 
                // id is an Emailuser.id when data_type is 'individual' or 
                // an Organisation.id when data_type is 'organisation'
                this.$emit('weak-link-created', { id: data_item_id, data_type: data_type });
            });
        },
        // Match typed searchTerm against available human-readable object identifiers (get_related_items_identifier) 
        search_available_object_identifiers(searchTerm){
            let suggest_list_offender = [];
            suggest_list_offender.length = 0;
            this.awesomplete_obj.list = [];

            /* Cancel all the previous requests */
            if (this.ajax_for_offender != null) {
                this.ajax_for_offender.abort();
                this.ajax_for_offender = null;
            }

            let search_url = "";
            if (this.search_type == "individual") {
                search_url = "/api/search_user/?search=";
            } else {
                search_url = "/api/search_organisation/?search=";
            }

            this.ajax_for_offender = $.ajax({
                type: "GET",
                url: search_url + searchTerm,
                success: function(data) {
                    if (data && data.results) {
                        let persons = data.results;
                        let limit = Math.min(this.maxItems, persons.length);
                        for (var i = 0; i < limit; i++) {
                        suggest_list_offender.push(persons[i]);
                        }
                    }
                    this.awesomplete_obj.list = suggest_list_offender;
                    this.awesomplete_obj.evaluate();
                },
                error: function(e) {}
            });
        },
    },
    created: function() {
        this.$nextTick(()=>{
            this.initAwesomplete();
        });
    }
}
</script>

<style>
.awesomplete > ul {
    margin-top: 2.5em;
}
.awesomplete > ul > li {
    border-bottom: 1px solid lightgray;
    margin: 5px 10px 5px 10px;
}
</style>
