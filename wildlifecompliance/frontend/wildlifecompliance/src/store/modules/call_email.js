import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
//import { getField, updateField } from 'vuex-map-fields';

export const callemailStore = {
    state: {
        call_email: {},
        call_id: '',
        display_call_email: {},
        count: 1,
        stored_renderer_data: {},
    },
    namespaced: true,
    getters: {
        call_email: state => state.call_email,
        call_email_id: state => state.call_email.id,
        stored_renderer_data: state => state.call_email.data,
        //getField, 

    },
    mutations: {
        updateCallEmail (state, call_email) {
            state.call_email = call_email;
        },
        updateClassification (state, classification) {
            state.call_email.classification = classification;
        },
        updateNumber (state, number) {
            state.call_email.number = number;
        },
        updateCaller (state, caller) {
            state.call_email.caller = caller;
        },
        updateAssignedTo (state, assigned_to) {
            state.call_email.assigned_to = assigned_to;
        },
        //updateField,
    },
    actions: {
        loadCallEmail({ dispatch, commit }, { call_email_id }) {
            console.log("loadCallEmail");
            return new Promise((resolve, reject) => {
                Vue.http.get(
                    helpers.add_endpoint_json(api_endpoints.call_email, call_email_id)
                    ).then(res => {
                        console.log("res.body");
                        console.log(res.body);
                        resolve();
                    commit('updateCallEmail', res.body);
                },
                err => {
                    console.log(err);
                    reject();
                });
            });
        },
    }
};
