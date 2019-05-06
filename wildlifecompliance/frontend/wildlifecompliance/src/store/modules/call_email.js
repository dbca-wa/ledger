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
            //id: 0,
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
        report_types: [],
    },
    getters: {
        call_email: state => state.call_email,
        report_type: state => state.call_email.report_type.report_type,
        classification_types: state => state.classification_types,
        report_types: state => state.report_types,
        call_coordinates: state => state.call_email.location.geometry.coordinates,
        call_email_form_url: state => {
            return state.call_email
              ? `/api/call_email/${state.call_email.id}/form_data.json`
              : "";
          },
          
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
        updateCallID(state, id) {
            //state.call_email.id = id;
            Vue.set(state.call_email, 'id', id);
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
        updateReportType(state, report_type_entry) {
            //Vue.set(state.classification_types, classification_entry.id, classification_entry.name);
            state.report_types.push(report_type_entry);
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
        async loadCallEmail({
            dispatch,
        }, {
            call_email_id
        }) {
            console.log("loadCallEmail");
            console.log(call_email_id);
            try {

                const returnedCallEmail = await Vue.http.get(
                    helpers.add_endpoint_json(
                        api_endpoints.call_email, 
                        call_email_id)
                        );
                        
                console.log("returnedCallEmail.body");
                console.log(returnedCallEmail.body);
                dispatch("setCallEmail", returnedCallEmail.body);
                
                for (let form_data_record of returnedCallEmail.body.data) {
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
                dispatch("setLocation", returnedCallEmail.body);

            } catch (err) {
                console.error(err);
            }
        },

        async loadClassification({
            dispatch,
        }) {
            console.log("loadClassification");
            try {
            const returnedClassification = await Vue.http.get(
                api_endpoints.classification
                );
            
            for (let classification_entry of returnedClassification.body.results) {
                dispatch("setClassificationEntry", classification_entry);
            }
            } catch (err) {
                console.error(err);
            }
        },

        async loadReportTypes({
            dispatch,
        }) {
            console.log("loadReportTypes");
            try {
            const returnedReportTypes = await Vue.http.get(
                api_endpoints.report_types
                );
            
            for (let report_type_entry of returnedReportTypes.body.results) {
                dispatch("setReportTypeEntry", report_type_entry);
            }
            } catch (err) {
                console.error(err);
            }
        },

        setClassificationEntry({
                commit,
            },
            classification_entry
        ) {
            commit("updateClassification", classification_entry);
        },
        
        setReportTypeEntry({
            commit,
        },
        report_type_entry
        ) {
            commit("updateReportType", report_type_entry);
        },


        setCallEmail({
            commit,
        }, call_email) {
            commit("updateCallEmail", call_email);
        },

        async saveCallEmail({ dispatch, state, getters}, {route}) {
            console.log("saveCallEmail");

            try {
                const savedCallEmail = await Vue.http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email, 
                    state.call_email.id + "/call_email_save/"
                    ), 
                    {...state.call_email}
                    )

                if (state.call_email.location.geometry.coordinates > 0) {
                    dispatch("saveLocation");
                    console.log("saveLocation - done");
                }
                if (state.call_email.schema.length > 0) {
                    dispatch("saveFormData", { url: getters.call_email_form_url }
                    , {
                        root: true
                    });
                    console.log("saveFormData - done");
                }
                
            } catch (err) {
                console.error(err);
            }
            await swal("Saved", "The record has been saved", "success");
                if (route) {
                    window.location.href = route;
                    }
        },

        async createCallEmail({ dispatch, state, getters}) {
            console.log("createCallEmail");
            console.log({...state.call_email});
            
            try {
                const newCallEmail = await Vue.http.post(api_endpoints.call_email, 
                    {...state.call_email});
                await dispatch("setCallID", newCallEmail.body.id);
                    // Call/Email pk must be loaded into Vuex before Location and Renderer data is sent to db
                    //await dispatch("loadCallEmail", { call_email_id: newCallEmail.body.id });
                    //console.log("loadCallEmail - pk loaded");
                if (state.call_email.location.geometry.coordinates > 0) {
                    await dispatch("saveLocation");
                    console.log("saveLocation - done");
                }
                if (state.call_email.schema.length > 0) {
                    await dispatch("saveFormData", { url: getters.call_email_form_url }
                    , {
                        root: true
                    });
                    console.log("saveFormData - done");
                }

            } catch (err) {
                console.log(err);
                swal("Error", "There was an error saving the record", "error");
            }
            await swal("Saved", "The record has been saved", "success");
                    window.location.href = "/internal/call_email/" + state.call_email.id;
        },
          
        async createLocation({
            state
        }) {
            console.log("createLocation");
            
            try {
                const newLocation = await Vue.http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email, 
                    state.call_email.id + "/new_location/"
                    ), {
                        town_suburb: state.call_email.location.properties.town_suburb,
                        street: instance.properties.street,
                        state: instance.properties.state,
                        postcode: instance.properties.postcode,
                        wkb_geometry: instance.geometry,
                    });
                newLocation
                
            } catch (err) {
                console.error(err);
            }
        },
        async saveLocation({
            state
        }) {
            console.log("saveLocation");
            
            try {
                const savedLocation = await Vue.http.post(helpers.add_endpoint_join(
                api_endpoints.call_email, 
                state.call_email.id + "/update_location/"
                ), {
                    town_suburb: state.call_email.location.properties.town_suburb,
                    street: instance.properties.street,
                    state: instance.properties.state,
                    postcode: instance.properties.postcode,
                    wkb_geometry: instance.geometry,
                });
            } catch (err) {
                console.error(err);
            }
        },
        setCallID({
            commit,
        }, id) {
            console.log("setCallID");
            commit("updateCallID", id);
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