import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';

export const callemailStore = {
    namespaced: true,
    state: {
        call_email: {
            schema: [],
        },
        call_id: '',
        display_call_email: {},
        count: 1,
    },
    getters: {
        call_email: state => state.call_email,
        call_id: state => state.call_id,

    },
    mutations: {
        updateCallEmail(state, call_email) {
            console.log(call_email);
            Vue.set(state, 'call_email', {
                ...call_email
            });
        },
        updateClassification(state, classification) {
            state.call_email.classification = classification;
        },
        updateNumber(state, number) {
            state.call_email.number = number;
        },
        updateCaller(state, caller) {
            state.call_email.caller = caller;
        },
        updateAssignedTo(state, assigned_to) {
            state.call_email.assigned_to = assigned_to;
        },
    },
    actions: {

        loadCallEmail({
            dispatch,
            commit
        }, {
            call_email_id
        }) {
            console.log("loadCallEmail");
            console.log(call_email_id);
            return new Promise((resolve, reject) => {
                Vue.http.get(
                    helpers.add_endpoint_json(api_endpoints.call_email, call_email_id)

                ).then(res => {
                        //console.log("res.body");
                        //console.log(res.body);
                        dispatch("setCallEmail", {
                            call_email: res.body
                        });
                        for (let form_data_record of res.body.data) {
                            dispatch("setFormValue", {
                                key: form_data_record.field_name,
                                value: {
                                    "value": form_data_record.value,
                                    "comment_value": form_data_record.comment,
                                    "deficiency_value": form_data_record.deficiency,
                                }
                            }, {
                                root: true
                            });
                        }
                        resolve();
                    },
                    err => {
                        console.log(err);
                        reject();
                    });
            });
        },

        setCallEmail({
            commit,
        }, {
            call_email
        }) {
            console.log(call_email);
            commit("updateCallEmail", call_email);
        },

    },

};