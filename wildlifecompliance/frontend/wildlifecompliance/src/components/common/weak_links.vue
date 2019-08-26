<template lang="html">
    <div>
        <div class="col-sm-4">
            <label for="entity-selector">Select entity</label>
            <select class="form-control" v-model="selectedEntity" id="entity-selector">
                <!--option disabled value="">Select entity</option-->
                <option value="call_email">Call / Email</option>
                <option value="inspection">Inspection</option>
                <option value="offence">Offence</option>
                <option value="sanction_outcome">Sanction Outcome</option>
            </select>
        </div>
        <div class="col-sm-4">
            
            <label for="elemId" class="transparent">Enter search text </label>
            <!--div class="row"></div-->
            <input :id="elemId" :class="classNames" :readonly="!isEditable" placeholder="Begin typing to search"/>
        </div>
    </div>
</template>

<script>
import Awesomplete from "awesomplete";
import $ from "jquery";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";

export default {
    name: "weak-links",
    data: function(){
        this.awesomplete_obj = null;
        return {
            elemId: 'create_weak_link_' + this._uid,
            selectedEntity: null,
        }
    },
    props: {
        // This prop is not used any more.  Instead elemId in the data is used.
        //elementId: {
          //  required: false
        //},
        classNames: {
            required: false,
            default: "form-control",
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
    computed: {
        csrf_token: function() {
          return helpers.getCookie("csrftoken");
        },
    },
    methods: {
        //clearInput: function(){
        //    document.getElementById(this.elemId).value = "";
        //},
        //setInput: function(weak_link_str){
        //    document.getElementById(this.elemId).value = weak_link_str;
        //},
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
                item: (text, input) => {
                    let ret = Awesomplete.ITEM(text, ""); // Not sure how this works but this doesn't add <mark></mark>
                    return ret;
                },
                data: (item, input) => {
                    //if (this.search_type == "individual") {
                    //    let f_name = item.first_name ? item.first_name : "";
                    //    let l_name = item.last_name ? item.last_name : "";
            
                    //    let full_name = [f_name, l_name].filter(Boolean).join(" ");
                    //    let email = item.email ? "E:" + item.email : "";
                    //    let p_number = item.phone_number ? "P:" + item.phone_number : "";
                    //    let m_number = item.mobile_number ? "M:" + item.mobile_number : "";
                    //    let dob = item.dob ? "DOB:" + item.dob : "DOB: ---";
            
                    //    let full_name_marked = "<strong>" + this.markMatchedText(full_name, input) + "</strong>";
                    //    let email_marked = this.markMatchedText(email, input);
                    //    let p_number_marked = this.markMatchedText(p_number, input);
                    //    let m_number_marked = this.markMatchedText(m_number, input);
                    //    let dob_marked = this.markMatchedText(dob, input);
            
                    //    let myLabel = [
                    //        full_name_marked,
                    //        email_marked,
                    //        p_number_marked,
                    //        m_number_marked,
                    //        dob_marked
                    //    ].filter(Boolean).join("<br />");
                    //    myLabel = "<div data-item-id=" + item.id + ' data-type="individual">' + myLabel + "</div>";
            
                    //    return {
                    //        label: myLabel, // Displayed in the list below the search box
                    //        value: [full_name, dob].filter(Boolean).join(", "), // Inserted into the search box once selected
                    //        id: item.id
                    //    };
                    //} else {
                    //    let name = item.name ? item.name : "";
                    //    let abn = item.abn ? "ABN:" + item.abn : "";
            
                    //    let name_marked = "<strong>" + this.markMatchedText(name, input) + "</strong>";
                    //    let abn_marked = this.markMatchedText(abn, input);
            
                    //    let myLabel = [name_marked, abn_marked].filter(Boolean).join("<br />");
                    //    myLabel = "<div data-item-id=" + item.id + ' data-type="organisation">' + myLabel + "</div>";
            
                    //    return {
                    //        label: myLabel,
                    //        value: [name, abn].filter(Boolean).join(", "),
                    //        id: item.id
                    //    };
                    //}
                    
                    let item_identifier_marked = this.markMatchedText(item.item_identifier, input);
                    let item_description_marked = this.markMatchedText(item.item_description, input);
                    
                    let myLabel = [
                        item_identifier_marked,
                        item_description_marked,
                    ].filter(Boolean).join("<br />");
                    //myLabel = "<div data-item-id=" + item.id + ' data-type="weak-link">' + myLabel + "</div>";
                    myLabel = "<div data-item-id=" + item.id + " data-type=" + item.model_name + ">" + myLabel + "</div>";
                    return {
                        label: myLabel,
                        //value: [name, abn].filter(Boolean).join(", "),
                        value: item.item_identifier,
                        id: item.id
                    };
                }
            });
            console.log(this.awesomplete_obj);
            $(element_search)
                .on("keyup", (ev) => {
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90) || (96 <= keyCode && keyCode <= 105) || keyCode == 8 || keyCode == 46) {
                    if (this.selectedEntity) {
                        this.search_available_object_identifiers(ev.target.value);
                    }
                    return false;
                }
            })
                .on("awesomplete-selectcomplete", (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                return false;
            })
                .on("awesomplete-select", (ev) => {
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
                this.$emit('weak-link-selected', { id: data_item_id, data_type: data_type });
            });
        },
        // Match typed searchTerm against available human-readable object identifiers (get_related_items_identifier) 
        search_available_object_identifiers(searchText) {
            console.log(searchText)
            let suggested_weak_links = [];
            suggested_weak_links.length = 0;
            this.awesomplete_obj.list = [];

            console.log(this.awesomplete_obj);

            /* Cancel all the previous requests */
            if (this.ajax_weak_links != null) {
                this.ajax_weak_links.abort();
                this.ajax_weak_links = null;
            }

            let search_url = "/api/search_weak_links/";
            let payload = {
                    'csrfmiddlewaretoken': this.csrf_token,
                    'selectedEntity': this.selectedEntity,
                    'searchText': searchText
            }

            this.ajax_weak_links = $.ajax({
                type: "POST",
                url: search_url,
                dataType: "json",
                //data: JSON.stringify(payload),
                data: payload,
                //contentType: "application/json",
                success: (data) => {
                    console.log(data)
                    if (data) {
                        //let weak_link_results = data.results;
                        let limit = Math.min(this.maxItems, data.length);
                        for (var i = 0; i < limit; i++) {
                        suggested_weak_links.push(data[i]);
                        }
                    }
                    console.log(suggested_weak_links)
                    //Object.assign(this.awesomplete_obj.weak_links, suggested_weak_links);
                    this.awesomplete_obj.list = suggested_weak_links;
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
