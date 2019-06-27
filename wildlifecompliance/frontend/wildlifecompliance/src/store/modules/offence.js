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
            call_email_id: null,
            identifier: '',
            status: 'draft',
            offenders: [],
            alleged_offences: [],
            location: {
                type: 'Feature',
                properties: {
                    town_suburb: null,
                    street: null,
                    state: 'WA',
                    postcode: null,
                    country: 'Australia',
                    details: ''
                },
                geometry: {
                    'type': 'Point',
                    'coordinates': []
                }
            },
            occurrence_from_to: true,
            occurrence_date_from: null,
            occurrence_date_to: null,
            occurrence_time_from: null,
            occurrence_time_to: null,
            details: ''
        }
    },
    getters: {
        offence: state => state.offence,
        offence_latitude(state) {
            if (state.offence.location) {
                if (state.offence.location.geometry) {
                    if (state.offence.location.geometry.coordinates.length > 0) {
                        return state.offence.location.geometry.coordinates[1];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
        offence_longitude(state) {
            if (state.offence.location) {
                if (state.offence.location.geometry) {
                    if (state.offence.location.geometry.coordinates.length > 0) {
                        return state.offence.location.geometry.coordinates[0];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
    },
    mutations: {
        updateAllegedOffenceIds(state, ids) {
            Vue.set(state.offence, 'alleged_offences', ids);
        },
        updateOffenders(state, offenders) {
            Vue.set(state.offence, 'offenders', offenders);
        },
        updateCallEmailId(state, id) {
            state.offence.call_email_id = id;
        },
        updateOffence(state, offence) {
            Vue.set(state, 'offence', offence);
        },
        updateOffenceEmpty(state){
            console.log('updateOffenceEmpty');
            let offence = {
                id: null,
                call_email_id: null,
                identifier: '',
                status: 'draft',
                offenders: [],
                alleged_offences: [],
                location: {
                    type: 'Feature',
                    properties: {
                        town_suburb: null,
                        street: null,
                        state: 'WA',
                        postcode: null,
                        country: 'Australia',
                        details: ''
                    },
                    geometry: {
                        'type': 'Point',
                        'coordinates': []
                    }
                },
                occurrence_from_to: true,
                occurrence_date_from: null,
                occurrence_date_to: null,
                occurrence_time_from: null,
                occurrence_time_to: null,
                details: ''
            };
            Vue.set(state, 'offence', offence);
        },
        updateLocationPoint(state, point) {
            state.offence.location.geometry.coordinates = point;
        },
        updateLocationAddress(state, location_properties) {
            state.offence.location.properties = location_properties;
        },
        updateLocationAddressEmpty(state) {
            state.offence.location.properties.town_suburb = "";
            state.offence.location.properties.street = "";
            state.offence.location.properties.state = "";
            state.offence.location.properties.postcode = "";
            state.offence.location.properties.country = "";
        },
        updateLocationDetailsFieldEmpty(state) {
            state.offence.location.properties.details = "";
        }
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
        async saveOffence({dispatch, state}){
            console.log('saveOffence');
            console.log(state.offence);

            try{
                let fetchUrl = helpers.add_endpoint_json(api_endpoints.offence, 'offence_save');
                const savedOffence = await Vue.http.post(fetchUrl, state.offence);
                await swal("Saved", "The record has been saved", "success");
            } catch (err) {
                if (err.body.non_field_errors){
                    await swal("Error", err.body.non_field_errors[0], "error");
                } else {
                    await swal("Error", "There was an error saving the record", "error");
                }
            }
        },
        setOffence({ commit, }, offence) {
            commit("updateOffence", offence);
        },
        setOffenceEmpty({ commit, }){
            console.log('setOffenceEmpty');
            commit("updateOffenceEmpty");
        },
        setLocationPoint({ commit, }, point) {
            commit("updateLocationPoint", point);
        },
        setLocationAddress({ commit, }, location_properties) {
            commit("updateLocationAddress", location_properties);
        },
        setLocationAddressEmpty({ commit, }) {
            commit("updateLocationAddressEmpty");
        },
        setLocationDetailsFieldEmpty({ commit, }) {
            commit("updateLocationDetailsFieldEmpty");
        },
        setAllegedOffenceIds({ commit, }, ids){
            commit("updateAllegedOffenceIds", ids);
        },
        setOffenders({ commit, }, offenders){
            commit("updateOffenders", offenders);
        },
        setCallEmailId({ commit, }, id){
            commit("updateCallEmailId", id);
        },
    },
};
