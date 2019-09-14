<template lang="html">
    <div>
        <div class="row form-group">
            <div class="col-sm-4">
                <label for="entity-selector">Select entity</label>
                <select :disabled="readonlyForm" class="form-control" v-model="selectedEntity" id="entity-selector">
                    <option value="call_email">Call / Email</option>
                    <option value="inspection">Inspection</option>
                    <option value="offence">Offence</option>
                    <option value="sanction_outcome">Sanction Outcome</option>
                </select>
            </div>
            <div class="col-sm-4">
                <input :id="elemId" class="form-control no-label" :readonly="readonlyForm" placeholder="Begin typing to search"/>
            </div>
            <div class="col-sm-3 no-label" v-if="!readonlyForm">
                <a ref="add_weak_link" @click="callCreateWeakLink" class="btn btn-primary btn-block">Add</a>
            </div>
        </div>
        <div class="row form-group">
            <div class="col-sm-8">
                <label for="comment">Add comment</label>
                <input id="comment" :readonly="readonlyForm" class="form-control" v-model="comment"/>
            </div>
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
            second_object_id: null,
            second_content_type: null,
            comment: '',
        }
    },
    props: {
       //  classNames: {
       //      type: String,
       //      required: false,
       //      default: "form-control no-label"
       //  },
       maxItems: {
           required: false,
           default: 10
       },
       //  search_type: {
       //      required: false,
       //  },
        readonlyForm: {
            required: false,
            default: false
        }
    },
    computed: {
        csrf_token: function() {
          return helpers.getCookie("csrftoken");
        },
    },
    methods: {
        markMatchedText(original_text, input) {
            if (original_text) {
                let ret_text = original_text.replace(new RegExp(input, "gi"), function( a, b) {
                    return "<mark>" + a + "</mark>";
                });
                return ret_text;
            } else {
                return '';
            }
        },
        callCreateWeakLink: function() {
            this.$nextTick(async () => {
                await this.$parent.createWeakLink();
            });
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
                    let item_identifier_marked = this.markMatchedText(item.item_identifier, input);
                    let item_description_marked = this.markMatchedText(item.item_description, input);
                    
                    let myLabel = [
                        item_identifier_marked,
                        item_description_marked,
                    ].filter(Boolean).join("<br />");
                    myLabel = "<div data-item-id=" + item.id + " data-type=" + item.model_name + ">" + myLabel + "</div>";
                    return {
                        label: myLabel,
                        //value: [name, abn].filter(Boolean).join(", "),
                        value: [item.item_identifier, item.item_description].filter(Boolean).join(", "),
                        id: item.id
                    };
                }
            });
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

                this.$nextTick(() => {
                    this.second_object_id = data_item_id;
                    this.second_content_type = data_type;
                });
            });
        },
        // Match typed searchTerm against available human-readable object identifiers (get_related_items_identifier) 
        search_available_object_identifiers(searchText) {
            let suggested_weak_links = [];
            suggested_weak_links.length = 0;
            this.awesomplete_obj.list = [];

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
                    if (data) {
                        let limit = Math.min(this.maxItems, data.length);
                        for (var i = 0; i < limit; i++) {
                        suggested_weak_links.push(data[i]);
                        }
                    }
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
.no-label {
    margin-top: 25px;
}
.awesomplete > ul {
    margin-top: 2.5em;
}
.awesomplete > ul > li {
    border-bottom: 1px solid lightgray;
    margin: 5px 10px 5px 10px;
}
</style>
