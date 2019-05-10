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
            classification: {
                id: null,
            },
            location: {
                properties: {
                    town_suburb: null,
                    street: null,
                    state: 'WA',
                    postcode: null,
                    country: 'Australia',
                },
                geometry: {
                    "type": "Point",
                    "coordinates": [null, null],
                },
            },
            report_type: {
                id: null,
            },
        },
        classification_types: [],
        report_types: [],
    },
    getters: {
        call_email: state => state.call_email,
        report_type: state => state.call_email.report_type.report_type,
        classification_types: state => state.classification_types,
        report_types: state => state.report_types,
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
            Vue.set(state.call_email, 'id', id);
        },
        updateCaller(state, caller) {
            state.call_email.caller = caller;
        },
        updateAssignedTo(state, assigned_to) {
            state.call_email.assigned_to = assigned_to;
        },
        updateClassification(state, classification_entry) {
            state.classification_types.push(classification_entry);
        },
        updateReportType(state, report_type_entry) {
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
        updateLocationProperties(state, location_properties) {
            state.call_email.location.properties = location_properties;
        },
        updateLocationPropertiesEmpty(state) {
            state.call_email.location.properties = {
                town_suburb: null,
                street: null,
                state: null,
                postcode: null,
                country: null,
            };
        },
        updateLocationID(state, locationID) {
            state.call_email.location_id = locationID;
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
                // Set empty (not null) location to force map display
                
                if (!returnedCallEmail.body.location) {
                    
                    console.log("null location");
                    await dispatch("setLocation", 
                    {
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        id: null,
                        geometry: {
                            coordinates: [null, null],
                            "type": "Point",
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

        async saveCallEmail({ dispatch, state, rootGetters}, { route, crud }) {
            console.log("saveCallEmail");
            
            try {
                let fetchUrl = null;
                if (crud == 'create') {
                    fetchUrl = api_endpoints.call_email;
                } else {
                    fetchUrl = helpers.add_endpoint_join(
                        api_endpoints.call_email, 
                        state.call_email.id + "/call_email_save/"
                        )
                }

                let payload = new Object();
                Object.assign(payload, state.call_email);
                delete payload.report_type;
                delete payload.schema;

                if (state.call_email.schema) {
                if (state.call_email.schema.length > 0) {
                    payload.renderer_data = rootGetters.renderer_form_data;
                    }
                }
                
                const savedCallEmail = await Vue.http.post(fetchUrl, 
                    payload
                    )
                console.log("savedCallEmail.body");
                console.log(savedCallEmail.body);
                await dispatch("setCallEmail", savedCallEmail.body);
                
                // Set empty (not null) location to force map display
                if (!savedCallEmail.body.location) {
                    
                    console.log("null location");
                    await dispatch("setLocation", 
                    {
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        id: null,
                        geometry: {
                            coordinates: [null, null],
                            "type": "Point",
                        },
                    }
                    );
                    console.log("empty location loaded");
                }
                

            } catch (err) {
                console.log(err);
                await swal("Error", "There was an error saving the record", "error");
                return window.location.href = "/internal/call_email/";
            }
            await swal("Saved", "The record has been saved", "success");
            if (route) {
                //return window.location.href = "/internal/call_email/" + state.call_email.id;
                return window.location.href = "/internal/call_email/";
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
        setLocationProperties({
            commit,
        }, location_properties) {
            console.log("setLocationProperties");
            commit("updateLocationProperties", location_properties);
        },
        setLocationPropertiesEmpty({
            commit,
        }) {
            console.log("setLocationPropertiesEmpty");
            commit("updateLocationPropertiesEmpty");
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

    },
        
};