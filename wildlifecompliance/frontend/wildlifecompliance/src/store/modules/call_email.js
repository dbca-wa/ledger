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
            location: {
                geometry: {
                    "type": "Point",
                    "coordinates": []
                },
                properties: {},
                },
            report_type: {},
        },
        classification_types: [],
    },
    getters: {
        call_email: state => state.call_email,
        //call_id: state => state.call_email.id,
        //call_classification: state => state.call_email.classification.name,
        //location: state => state.call_email.location,
        report_type: state => state.call_email.report_type.report_type,
        classification_types: state => state.classification_types,
        call_coordinates: state => state.call_email.location.geometry.coordinates,
        
        call_email_form_url: state => {
            return state.call_email
              ? `/api/call_email/${state.call_email.id}/form_data.json`
              : "";
          },
          
         /*
         call_email_form_url: state => {
            if (state.call_email) {
                return `/api/call_email/${state.call_email.id}/form_data.json`;
            }
            return "";
          },
          */
    },
    mutations: {
        updateCallEmail(state, call_email) {
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
        },
        updateLocation(state, location) {
            console.log("location");
            console.log(location);
            Vue.set(state.call_email, 'location', location);
        },
        updateLocationPoint(state, point) {
            console.log("point");
            console.log(point);
            //
            state.call_email.location.geometry.coordinates = point;
        },
        updateGeoJSONData(state, GeoJSONData) {
            console.log("GeoJSONData");
            console.log(GeoJSONData);
            Vue.set(state.call_email, 'GeoJSONData', GeoJSONData);
        },
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
                        console.log("setCallEmail");
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
            commit("updateClassification", classification_entry);
        },

        setCallEmail({
            commit,
        }, call_email) {
            commit("updateCallEmail", call_email);
        },

        saveCallEmail({ dispatch, state, getters}, {location, renderer, route}) {
            console.log("saveCallEmail");

            if (location) {
                console.log("saveLocation");
                dispatch("saveLocation");
            }
            if (renderer) {
                console.log("saveFormData");
                console.log(getters.call_email_form_url);
                dispatch("saveFormData", {
                    url: getters.call_email_form_url,
                    }
                , {
                    root: true
                });
            }
            return new Promise((resolve, reject) => {
                Vue.http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email, 
                    state.call_email.id + "/call_email_save/"
                    ), 
                    /*
                    {
                        classification_id: state.call_email.classification.id,
                        number: state.call_email.number,
                        caller: state.call_email.caller,
                        assigned_to: state.call_email.assigned_to,
                    }
                    */
                    {...state.call_email}
                   
                    )
                    .then(res => {
                        resolve();
                        },
                        err => {
                            //swal("Error", "There was an error saving the record", "error");
                            console.log(err);
                            reject();
                        });
            });
        },

        saveLocation({
            state
        }) {
            const instance = state.call_email.location;
            
            console.log("instance");
            console.log(instance);
            return new Promise((resolve, reject) => {
                Vue.http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email, 
                    state.call_email.id + "/update_location/"
                    ), {
                        town_suburb: state.call_email.location.properties.town_suburb,
                        street: instance.properties.street,
                        state: instance.properties.state,
                        postcode: instance.properties.postcode,
                        wkb_geometry: instance.geometry,
                    }).then(res => {
                            console.log(res.body.results);
                            console.log("success");
                            resolve();
                        },
                        err => {
                            console.log(err);
                            reject();
                        });
            });
        },
        setLocation({
            commit,
        }, location) {
            console.log("setLocation");
            commit("updateLocation", location);
        },
        setLocationPoint({
            commit,
        }, point) {
            console.log("setLocationPoint");
            commit("updateLocationPoint", point);
        },
        setGeoJSONData({
            commit,
        }, GeoJSONData) {
            console.log("setGeoJSONData");
            commit("updateGeoJSONData", GeoJSONData);
        },
    },
        
};