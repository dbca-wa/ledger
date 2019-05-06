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
            //id: null,
            schema: [],
            classification: {},
            /*
            location: {
                geometry: {
                    "type": "Point",
                    "coordinates": []
                },
                */
            location: {
                    properties: {
                        town_suburb: null,
                        street: null,
                        state: null,
                        postcode: null,
                        country: null,
                    },
                    geometry: {
                        "type": "Point",
                        "coordinates": [],
                    },
                },
                //properties: {},
                //},
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
        /*
        updateCallReportTypeID(state, call_report_type) {
            //Vue.set(state.classification_types, classification_entry.id, classification_entry.name);
            state.call_email.report_type_id = call_report_type;
        },
        */
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
        updateLocationID(state, locationID) {
            state.call_email.location_id = locationID;
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
                await dispatch("setCallEmail", returnedCallEmail.body);
                if (!state.call_email.location) {
                    await dispatch("setLocation", 
                    {
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        geometry: {
                            coordinates: [],
                        },
                    }
                    );
                    console.log("empty location loaded");
                }
                
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
                //dispatch("setLocation", returnedCallEmail.body);

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
        /*

        setCallReportTypeID({
            commit,
        },
        call_report_type
        ) {
            commit("updateCallReportTypeID", call_report_type);
        },
        */
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

                if (state.call_email.location.geometry.coordinates.length > 0) {
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
        /*
        async createCallEmail({ dispatch, state, getters}) {
            console.log("createCallEmail");
            console.log({...state.call_email});
            
            try {
                if (state.call_email.location.geometry.coordinates.length > 0) {
                    await dispatch("createLocation");
                } 
                
                const newCallEmail = await Vue.http.post(api_endpoints.call_email, 
                    {...state.call_email});
                console.log("newCallEmail.body.id");
                console.log(newCallEmail.body.id);
                await dispatch("setCallID", newCallEmail.body.id);
                
                if (state.call_email.schema.length > 0) {
                    await dispatch("saveFormData", { url: getters.call_email_form_url }
                    , {
                        root: true
                    });
                    console.log("saveFormData - done");
                }

            } catch (err) {
                console.log(err);
                await swal("Error", "There was an error saving the record", "error");
                return window.location.href = "/internal/call_email/";
            }
            await swal("Saved", "The record has been saved", "success");
            return window.location.href = "/internal/call_email/" + state.call_email.id;
        },
        */
        
        async createCallEmail({ dispatch, state, getters}) {
            console.log("createCallEmail");
            console.log({...state.call_email});
            
            try {
                
                const newCallEmail = await Vue.http.post(api_endpoints.call_email, 
                    {...state.call_email});
                console.log("newCallEmail.body.id");
                console.log(newCallEmail.body.id);
                await dispatch("setCallID", newCallEmail.body.id);
                
                if (state.call_email.schema.length > 0) {
                    await dispatch("saveFormData", { url: getters.call_email_form_url }
                    , {
                        root: true
                    });
                    console.log("saveFormData - done");
                }

            } catch (err) {
                console.log(err);
                await swal("Error", "There was an error saving the record", "error");
                return window.location.href = "/internal/call_email/";
            }
            await swal("Saved", "The record has been saved", "success");
            return window.location.href = "/internal/call_email/" + state.call_email.id;
        },
        async createLocation({
            state, dispatch
        }) {
            console.log("createLocation");
            try {
                let callLocation = null;
                if (state.call_email.location) {
                    callLocation = await Vue.http.post(
                        api_endpoints.location, 
                        {...state.call_email.location}
                        );
                    } else {
                        callLocation = await Vue.http.post(
                            api_endpoints.location, 
                            {
                                town_suburb: null,
                                street: null,
                                state: null,
                                postcode: null,
                                country: null,
                                wkb_geometry: null,
                            }
                            );
                    }

                console.log(callLocation.body.id);
                await dispatch("setLocationID", callLocation.body.id);
            } catch (err) {
                console.error(err);
            }
            console.log("createLocation - done");

        },

        async saveLocation({
            state
        }) {
            console.log("saveLocation");
            try {
                if (state.call_email.location) {
                    await Vue.http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email, 
                    state.call_email.id + "update_location/"
                    ),        
                    {...state.call_email.location}
                    );
                } else {
                    await Vue.http.post(
                        api_endpoints.location, 
                        {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                            wkb_geometry: null,
                        }
                        );
                }
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
        setLocationID({
            commit,
        }, locationID) {
            console.log("setLocationID");
            commit("updateLocationID", locationID);
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