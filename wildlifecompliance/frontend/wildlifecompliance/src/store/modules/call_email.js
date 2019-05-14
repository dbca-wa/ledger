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
        referrers: [],
    },
    getters: {
        call_email: state => state.call_email,
        report_type: state => state.call_email.report_type.report_type,
        classification_types: state => state.classification_types,
        report_types: state => state.report_types,
        referrers: state => state.referrers,
    },
    mutations: {
        updateCallEmail(state, call_email) {
            Vue.set(state, 'call_email', {
                ...call_email
            });
        },
        updateSchema(state, schema) {
            state.call_email.schema = schema;
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
            // Clear existing classification entries
            await dispatch("setClassificationEntry", null);

            for (let classification_entry of returnedClassification.body.results) {
                dispatch("setClassificationEntry", classification_entry);
            }
            } catch (err) {
                console.error(err);
            }
        },
        async loadReferrers({
            dispatch,
        }) {
            console.log("loadReferrers");
            try {
            const returnedReferrers = await Vue.http.get(
                api_endpoints.referrers
                );
            // Clear existing classification entries
            await dispatch("setReferrerEntry", null);

            for (let referrer_entry of returnedReferrers.body.results) {
                dispatch("setReferrerEntry", referrer_entry);
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
                helpers.add_endpoint_json(
                    api_endpoints.report_types,
                    'get_distinct_queryset')
                //api_endpoints.report_types
                );
            // Clear existing report_type entries
            await dispatch("setReportTypeEntry", null);
            
            for (let report_type_entry of returnedReportTypes.body) {
                dispatch("setReportTypeEntry", report_type_entry);
            }
            } catch (err) {
                console.error(err);
            }
        },        
        async updateSchema({dispatch, state}) {
            console.log("updateSchema");
            try {
                let payload = new Object();
                payload.id = state.call_email.id;
                payload.report_type_id = state.call_email.report_type_id;

                const updatedCallEmail = await Vue.http.post(
                    helpers.add_endpoint_join(
                        api_endpoints.call_email, 
                        state.call_email.id + "/update_schema/"),
                    payload
                    );

                await dispatch("setSchema", updatedCallEmail.body.schema);

            } catch (err) {
                console.error(err);
            }

        },
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
                delete payload.report_type;
                delete payload.schema;
                //delete payload.location;
                if (payload.occurrence_date_from) {
                    payload.occurrence_date_from = moment(payload.occurrence_date_from).format('YYYY-MM-DD');
                } 
                if (payload.occurrence_date_to) {
                    payload.occurrence_date_to = moment(payload.occurrence_date_to).format('YYYY-MM-DD');
                } 
                if (crud == 'duplicate') {
                    payload.id = null;

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
    },
};
