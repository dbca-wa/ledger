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
            classification: {},
            location: {},
            report_type: {},
        },
        call_id: '',
        display_call_email: {},
        count: 1,
        call_classification: '',
        classification_types: [],
    },
    getters: {
        call_email: state => state.call_email,
        call_id: state => state.call_email.id,
        call_classification: state => state.call_email.classification.name,
        location: state => state.call_email.location.street,
        report_type: state => state.call_email.report_type.report_type,
        classification_types: state => state.classification_types,

    },
    mutations: {
        updateCallEmail(state, call_email) {
            console.log(call_email);
            Vue.set(state, 'call_email', {
                ...call_email
            });
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
        updateClassification(state, classification_entry) {
            //Vue.set(state.classification_types, classification_entry.id, classification_entry.name);
            state.classification_types.push(classification_entry);
        }
    },
    actions: {

        loadCallEmail({
            dispatch,
        }, {
            call_email_id
        }) {
            console.log("loadCallEmail");
            console.log(call_email_id);
            return new Promise((resolve, reject) => {
                Vue.http.get(
                    helpers.add_endpoint_json(api_endpoints.call_email, call_email_id)

                ).then(res => {
                        dispatch("setCallEmail", res.body);
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
        loadClassification({
            dispatch,
        }) {
            console.log("loadClassification");
            return new Promise((resolve, reject) => {
                Vue.http.get(api_endpoints.classification)
                    .then(res => {
                            console.log(res.body.results);
                            for (let classification_entry of res.body.results) {
                                dispatch("setClassificationEntry", classification_entry);
                                resolve();
                            }
                        },
                        err => {
                            console.log(err);
                            reject();
                        });
            });
        },
        setClassificationEntry({
                commit,
            },
            classification_entry
        ) {
            console.log(classification_entry);
            commit("updateClassification", classification_entry);
        },

        setCallEmail({
            commit,
        }, call_email) {
            console.log(call_email);
            commit("updateCallEmail", call_email);
        },

    },

};