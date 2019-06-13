import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import moment from 'moment';

export const offenceStore = {
    namespaced: true,
    state: {
        offence: {
            id: null,
            identifier: '',
            status: 'draft',
            offenders: [],
            alleged_offences: [],
            location: {
                type: "Feature",
                properties: {
                    town_suburb: null,
                    street: null,
                    state: 'WA',
                    postcode: null,
                    country: 'Australia',
                    details: ''
                },
                geometry: {
                    "type": "Point",
                    "coordinates": [],
                },
            },
            occurrence_from_to: true,
            occurrence_date_from: null,
            occurrence_date_to: null,
            occurrence_time_from: null,
            occurrence_time_to: null,
            details: '',
        },
    },
    getters: {
        offence: state => state.offence,
    },
    mutations: {
        updateOffence(state, offence) {
            Vue.set(state, 'offence', offence);
        },
    },
    actions: {
        async loadOffence({ dispatch, }, { offence_id }) {
            try {
                const returnedOffence = await Vue.http.get(
                    helpers.add_endpoint_json(
                        api_endpoints.offence, 
                        offence_id
                    )
                );

                await dispatch("setOffence", returnedOffence.body);

            } catch (err) {
                console.log(err);
            }
        },
        setOffence({ commit, }, offence) {
            commit("updateOffence", offence);
        },
    },
};
