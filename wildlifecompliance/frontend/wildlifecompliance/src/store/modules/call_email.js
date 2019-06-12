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
            allocated_group: {
                members: [],
            },
        },
        classification_types: [],
        report_types: [],
        referrers: [],
        status_choices: [],
    },
    getters: {
        call_email: state => state.call_email,
        classification_types: state => state.classification_types,
        report_types: state => state.report_types,
        status_choices: state => state.status_choices,
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
        updateStatusChoices(state, choices) {
            for (var i = 0; i < choices.length; i++) {
                state.status_choices.push(choices[i]);
            }
        },
        updateClassificationChoices(state, choices) {
            for (var i = 0; i < choices.length; i++) {
                state.classification_types.push(choices[i]);
            }
        },
        updateCallEmail(state, call_email) {
            if (!call_email.location) {
                /* When location is null, set default object */
                call_email.location =
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
                };
            }
            if (!call_email.email_user){
                /* When email_user is null, set default object */
                call_email.email_user = {
                    first_name: '',
                    last_name: '',
                    dob: null,
                    residential_address: {
                        line1: '',
                        locality: '',
                        state: 'WA',
                        postcode: '',
                        country: 'AU'
                    }
                };
            } else if (!call_email.email_user.residential_address){
                /* When residential_address is null, set default object */
                call_email.email_user.residential_address = {
                    line1: '',
                    locality: '',
                    state: 'WA',
                    postcode: '',
                    country: 'AU'
                };
            }
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
        // updateAllocatedTo(state, member_ids) {
        //     console.log("updateAllocatedTo");
        //     if (member_ids) {
        //         state.call_email.allocated_to = [];
        //         for (let member_id of member_ids) {
        //             state.call_email.allocated_to.push(member_id);
        //         }
        //     }
        // },
        // updateAllocatedGroup(state, id) {
        //     console.log("updateAllocatedGroup");
        //     if (id) {
        //         Vue.set(state.call_email, 'allocated_group_id', id);
        //     }
        // },
        updateClassification(state, classification) {
            if (classification) {
                Vue.set(state.call_email, 'classification', classification);
            }
        },
        updateReportType(state, report_type) {
            if (report_type) {
                Vue.set(state.call_email, 'report_type', report_type);
            }
        },
        updateEmailUser(state, email_user){
            if (email_user){
                Vue.set(state.call_email, 'email_user', email_user);
            }
        },
        updateEmailUserEmpty(state){
            let email_user_empty = {
                first_name: '',
                last_name: '',
                dob: null,
                residential_address: {
                    line1: '',
                    locality: '',
                    state: 'WA',
                    postcode: '',
                    country: 'AU'
                }
            };
            Vue.set(state.call_email, 'email_user', email_user_empty);
        },
        updateResidentialAddress(state, address){
            console.log("updateResidentialAddress");
            console.log(address);
            Vue.set(state.call_email.email_user, 'residential_address', address);
        },
        updateLocation(state, location) {
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
        },
        updateAllocatedGroupList(state, members) {
            // for (let member of members) {
            //     state.allocated_group.members.push(member);
            // }
            Vue.set(state.call_email, 'allocated_group', {});
            Vue.set(state.call_email.allocated_group, 'members', members);
            // state.call_email.allocated_group.members = [];
            // Object.assign(state.call_email.allocated_group.members, members);
        },
        updateAllocatedGroupId(state, id) {
            state.call_email.allocated_group_id = id;
        },
        updateRegionId(state, id) {
            state.call_email.region_id = id;
        },
    },
    actions: {
        async loadCallEmail({ dispatch, }, { call_email_id }) {
            console.log("loadCallEmail");
            console.log(call_email_id);
            try {
                const returnedCallEmail = await Vue.http.get(
                    helpers.add_endpoint_json(
                        api_endpoints.call_email, 
                        call_email_id)
                    );

                /* Set CallEmail object */
                await dispatch("setCallEmail", returnedCallEmail.body);

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
                console.log(err);
            }
        },
        async saveCallEmailPerson({dispatch, state}){
            try{
                let fetchUrl = helpers.add_endpoint_join(api_endpoints.call_email, state.call_email.id + "/call_email_save_person/");
                const savedEmailUser = await Vue.http.post(fetchUrl, state.call_email);
                await dispatch("setEmailUser", savedEmailUser.body);
                await swal("Saved", "The record has been saved", "success");
            } catch (err) {
                console.log(err);
                if (err.body.non_field_errors){
                    await swal("Error", err.body.non_field_errors[0], "error");
                } else {
                    await swal("Error", "There was an error saving the record", "error");
                }
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
                const savedCallEmail = await Vue.http.post(fetchUrl, payload)
                console.log("savedCallEmail.body");
                console.log(savedCallEmail.body);
                await dispatch("setCallEmail", savedCallEmail.body);
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
        setAllocatedGroupList({ commit }, data) {
            console.log("setAllocatedGroupList");
            commit('updateAllocatedGroupList', data);
        },
        setRegionId({ commit }, id) {
            commit('updateRegionId', id);
        },
        
        async loadAllocatedGroup({ dispatch }, { region_district_id, group_permission } ) {
            console.log(region_district_id);
            console.log(group_permission);
            let url = helpers.add_endpoint_join(
                api_endpoints.region_district,
                region_district_id + '/get_group_id_by_region_district/'
                );
            console.log(url);
            let returned = await Vue.http.post(
                url, 
                { 'group_permission': group_permission
            });
            console.log(returned.body);
            if (returned.body.group_id) {
                await dispatch('setAllocatedGroupId', returned.body.group_id);
            }
            if (returned.body.allocated_group) {
                await dispatch('setAllocatedGroupList', returned.body.allocated_group);
            }
        },
        setAllocatedGroupId({ commit, }, id) {
            console.log("setAllocatedGroupId");
            commit("updateAllocatedGroupId", id);
        },
        setCallID({ commit, }, id) {
            console.log("setCallID");
            commit("updateCallID", id);
        },
        setSchema({ commit, }, schema) {
            console.log("setSchema");
            commit("updateSchema", schema);
        },
        setEmailUser({ commit, }, email_user) {
            commit("updateEmailUser", email_user);
        },
        setEmailUserEmpty({ commit, }){
            commit("updateEmailUserEmpty");
        },
        setResidentialAddress({ commit }, address){
            commit("updateResidentialAddress", address);
        },
        setLocation({ commit, }, location) {
            commit("updateLocation", location);
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
        setLocationPoint({ commit, }, point) {
            console.log("setLocationPoint");
            commit("updateLocationPoint", point);
        },
        setClassificationEntry({ commit, }, classification_entry) {
            commit("updateClassificationTypes", classification_entry);
        },
        setReferrerEntry({ commit, }, referrer_entry) {
            commit("updateReferrers", referrer_entry);
        },
        setReportTypeEntry({ commit, }, report_type_entry) {
            commit("updateReportTypes", report_type_entry);
        },
        setCallEmail({ commit, }, call_email) {
            commit("updateCallEmail", call_email);
        },
        setReportType({ commit, }, report_type) {
            commit("updateReportType", report_type)
        },
        setClassification({ commit, }, classification) {
            commit("updateClassification", classification)
        },
    },
};
