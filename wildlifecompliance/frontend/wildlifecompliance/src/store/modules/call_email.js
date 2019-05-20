import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import moment from 'moment';

export const callemailStore = {
    namespaced: true,
    state: {
        call_email: {
            schema: [],
            classification: {
                id: null,
            },
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
            report_type: {
                id: null,
            },
        },
        classification_types: [],
        report_types: [],
        referrers: [],
    },
    getters: {
        call_email: state => state.call_email,
        classification_types: state => state.classification_types,
        report_types: state => state.report_types,
        referrers: state => state.referrers,
        call_latitude(state) {
            if (state.call_email.location) {
                if (state.call_email.location.geometry) {
                    if (state.call_email.location.geometry.coordinates.length > 0) {
                        return state.call_email.location.geometry.coordinates[1];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
        call_longitude(state) {
            if (state.call_email.location) {
                if (state.call_email.location.geometry) {
                    if (state.call_email.location.geometry.coordinates.length > 0) {
                        return state.call_email.location.geometry.coordinates[0];
                    } else {return "";}
                } else {return "";}
            } else {return "";}
        },
    },
    mutations: {
        updateCallEmail(state, call_email) {
            Vue.set(state, 'call_email', {
                ...call_email
            });
        },
        updateSchema(state, schema) {
            //state.call_email.schema = schema;
            Vue.set(state.call_email, 'schema', schema);
        },        
        updateClassificationTypes(state, classification_entry) {
            if (classification_entry) {
                state.classification_types.push(classification_entry);
            } else {
                state.classification_types = [];
            }
        },
        updateReferrers(state, referrer_entry) {
            if (referrer_entry) {
                state.referrers.push(referrer_entry);
            } else {
                state.referrers = [];
            }
        },
        updateReportTypes(state, report_type_entry) {
            if (report_type_entry) {
                state.report_types.push(report_type_entry);
            } else {
                state.report_types = [];
            }
        },
        updateClassification(state, classification) {
            if (classification) {
                Vue.set(state.call_email, 'classification', classification);
            }
        },
        updateReportType(state, report_type) {
            if (report_type) {
                console.log("report_type");
                console.log(report_type);
                Vue.set(state.call_email, 'report_type', report_type);
                console.log("state.call_email.report_type");
                console.log(state.call_email.report_type);
            }
        },
        updateLocation(state, location) {
            console.log("location");
            console.log(location);
            Vue.set(state.call_email, 'location', location);
        },
        updateLocationPoint(state, point) {
            console.log("point");
            console.log(point);
                state.call_email.location.geometry.coordinates = point;
        },
        updateLocationAddress(state, location_properties) {
            state.call_email.location.properties = location_properties;
        },
        updateLocationAddressEmpty(state) {
            state.call_email.location.properties.town_suburb = "";
            state.call_email.location.properties.street = "";
            state.call_email.location.properties.state = "";
            state.call_email.location.properties.postcode = "";
            state.call_email.location.properties.country = "";
        },
        updateLocationDetailsFieldEmpty(state) {
            state.call_email.location.properties.details = "";
        }
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
                        
                await dispatch("setCallEmail", returnedCallEmail.body);
                // Set empty (not null) location to force map display
                
                if (!returnedCallEmail.body.location) {
                    
                    console.log("null location");
                    await dispatch("setLocation", 
                    {
                        "type": "Feature",
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        id: null,
                        geometry: {
                            "type": "Point",
                            "coordinates": [],
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
        // async loadClassification({
        //     dispatch,
        // }) {
        //     console.log("loadClassification");
        //     try {
        //     const returnedClassification = await Vue.http.get(
        //         api_endpoints.classification 
        //         );
        //     // Clear existing classification entries
        //     await dispatch("setClassificationEntry", null);

        //     for (let classification_entry of returnedClassification.body.results) {
        //         dispatch("setClassificationEntry", classification_entry);
        //     }
        //     } catch (err) {
        //         console.error(err);
        //     }
        // },
        // async loadReferrers({
        //     dispatch,
        // }) {
        //     console.log("loadReferrers");
        //     try {
        //     const returnedReferrers = await Vue.http.get(
        //         api_endpoints.referrers
        //         );
        //     // Clear existing classification entries
        //     await dispatch("setReferrerEntry", null);

        //     for (let referrer_entry of returnedReferrers.body.results) {
        //         dispatch("setReferrerEntry", referrer_entry);
        //     }
        //     } catch (err) {
        //         console.error(err);
        //     }
        // },
        // async loadReportTypes({
        //     state,
        //     dispatch,
        // }) {
        //     console.log("loadReportTypes");
        //     try {
        //     const returnedReportTypes = await Vue.http.get(
        //         helpers.add_endpoint_json(
        //             api_endpoints.report_types,
        //             'get_distinct_queryset')
        //         //api_endpoints.report_types
        //         );
        //     // Clear existing report_type entries
        //     await dispatch("setReportTypeEntry", null);
            
        //     for (let report_type_entry of returnedReportTypes.body) {
        //         await dispatch("setReportTypeEntry", report_type_entry);
        //     }
        //     // insert current CallEmail report type if not in report_types
        //     let reportTypeMatches = 0;
        //     if (state.call_email.report_type) {
        //         state.report_types.findIndex((report_type) => {
        //             if (report_type.id === state.call_email.report_type.id) {
        //                 reportTypeMatches += 1;
        //             }
        //         });
        //     console.log("reportTypeMatches");
        //     console.log(reportTypeMatches);
        //     if (!(reportTypeMatches > 0)) {
        //         await dispatch("setReportTypeEntry", state.call_email.report_type);
        //         }
        //     }
        //     } catch (err) {
        //         console.error(err);
        //     }
        // },        
        async saveCallEmail({ dispatch, state, rootGetters}, { route, crud }) {
            console.log("saveCallEmail");
            let callId = null;
            try {
                let fetchUrl = null;
                if (crud === 'create' || crud === 'duplicate') {
                    fetchUrl = api_endpoints.call_email;
                } else {
                    fetchUrl = helpers.add_endpoint_join(
                        api_endpoints.call_email, 
                        state.call_email.id + "/call_email_save/"
                        )
                }

                let payload = new Object();
                Object.assign(payload, state.call_email);
                //delete payload.report_type;
                //delete payload.schema;
                //delete payload.location;
                if (payload.occurrence_date_from) {
                    payload.occurrence_date_from = moment(payload.occurrence_date_from).format('YYYY-MM-DD');
                } 
                if (payload.occurrence_date_to) {
                    payload.occurrence_date_to = moment(payload.occurrence_date_to).format('YYYY-MM-DD');
                } 
                if (crud == 'duplicate') {
                    payload.id = null;
                    payload.location_id = null;
                    if (payload.location) {
                        payload.location.id = null;
                    }
                }

                if (state.call_email.schema) {
                if (state.call_email.schema.length > 0) {
                    payload.renderer_data = rootGetters.renderer_form_data;
                    }
                }
                
                console.log("payload");
                console.log(payload);
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
                        type: "Feature",
                        properties: {
                            town_suburb: null,
                            street: null,
                            state: null,
                            postcode: null,
                            country: null,
                        },
                        id: null,
                        geometry: {
                            "type": "Point",
                            "coordinates": [],
                        },
                    }
                    );
                    console.log("empty location loaded");
                }
                callId = savedCallEmail.body.id;

            } catch (err) {
                console.log(err);
                await swal("Error", "There was an error saving the record", "error");
                return window.location.href = "/internal/call_email/";
            }
            if (crud === 'duplicate') {
                return window.location.href = "/internal/call_email/" + callId;
            }
            else if (crud !== 'create') {
                await swal("Saved", "The record has been saved", "success");
            }
            if (route) {
                return window.location.href = "/internal/call_email/";
            } else {
                return callId;
            }
        },
        setCallID({
            commit,
        }, id) {
            console.log("setCallID");
            commit("updateCallID", id);
        },
        setSchema({
            commit,
        }, schema) {
            console.log("setSchema");
            commit("updateSchema", schema);
        },
        setLocation({
            commit,
        }, location) {
            commit("updateLocation", location);
        },
        setLocationAddress({
            commit,
        }, location_properties) {
            commit("updateLocationAddress", location_properties);
        },
        setLocationAddressEmpty({
            commit,
        }) {
            commit("updateLocationAddressEmpty");
        },
        setLocationDetailsFieldEmpty({
            commit,
        }) {
            commit("updateLocationDetailsFieldEmpty");
        },
        
        setLocationPoint({
            commit,
        }, point) {
            console.log("setLocationPoint");
            commit("updateLocationPoint", point);
        },
        setClassificationEntry({
            commit,
        },
        classification_entry
        ) {
            commit("updateClassificationTypes", classification_entry);
        },
        setReferrerEntry({
            commit,
        },
            referrer_entry
        ) {
            commit("updateReferrers", referrer_entry);
        },        
        setReportTypeEntry({
            commit,
        },
        report_type_entry
        ) {
            commit("updateReportTypes", report_type_entry);
        },
        setCallEmail({
            commit,
        }, call_email) {
            commit("updateCallEmail", call_email);
        },
        setReportType({
            commit,
        }, report_type) {
            commit("updateReportType", report_type)
        },
        setClassification({
            commit,
        }, classification) {
            commit("updateClassification", classification)
        },
    },
};
