import Vue from 'vue';
import {
    UPDATE_APPLICATION,
    UPDATE_ORIGINAL_APPLICATION,
    UPDATE_ORG_APPLICANT,
    UPDATE_PROXY_APPLICANT,
} from '@/store/mutation-types';


export const applicationStore = {
    state: {
        original_application: {},
        application: {
            "schema": [],
            "licence_type_data": {
                "activity": []
            }
        },
    },
    getters: {
        application: state => state.application,
        original_application: state => state.original_application,
        amendment_requests: state => state.application.amendment_requests,
        application_id: state => state.application.id,
        licence_type_data: state => state.application.licence_type_data,
        org_address: state => state.application.org_applicant != null && state.application.org_applicant.address != null ? state.application.org_applicant.address : {},
        proxy_address: state => state.application.proxy_applicant != null && state.application.proxy_applicant.address != null ? state.application.proxy_applicant.address : {},
        application_readonly: state => state.application.readonly,
        applicant_type: state => {
            if (state.application.org_applicant){
                return 'org';
            } else if (state.application.proxy_applicant){
                return 'proxy';
            }
            return 'submitter';
        },
        checkActivityStatus: (state, getters, rootState, rootGetters) => (status_list, status_count=1, required_role=null) => {
            if(status_list.constructor !== Array) {
                status_list = [status_list];
            }
            const activities_list = getters.licence_type_data.activity;
            return activities_list.filter(activity =>
                status_list.includes(activity.processing_status.id)
                && (required_role === null || rootGetters.hasRole(required_role, activity.id))
            ).length >= status_count;
        },
        isFinalised: (state, getters) => {
            return getters.checkActivityStatus([
                'declined',
                'accepted'
            ], getters.licence_type_data.activity.length);
        },
        isPartiallyFinalised: (state, getters) => {
            const final_statuses = [
                'declined',
                'accepted'
            ];
            const activity_count = getters.licence_type_data.activity.length;
            return getters.checkActivityStatus(final_statuses) && !getters.checkActivityStatus(final_statuses, activity_count);
        },
        isApplicationLoaded: state => Object.keys(state.application).length && state.application.licence_type_data.activity.length,
        isApplicationActivityVisible: (state, getters, rootState, rootGetters) =>
            (activity_id, exclude_statuses, exclude_processing_statuses, for_user_role) => {
            if(!state.application.activities) {
                return 0;
            }
            return getters.filterActivityList({
                activity_list: state.application.activities,
                activity_id: activity_id,
                exclude_statuses: exclude_statuses,
                exclude_processing_statuses: exclude_processing_statuses,
                for_user_role: for_user_role,
                licence_activity_id_key: 'licence_activity'
            }).length;
        },
        licenceActivities: (state, getters) => (activity_status, for_user_role) => {
            return getters.filterActivityList({
                activity_list: getters.licence_type_data.activity,
                only_processing_statuses: activity_status,
                for_user_role: for_user_role,
            });
        },
        filterActivityList: (state, getters, rootState, rootGetters) =>
            ({activity_list,
              activity_id,
              exclude_statuses,
              only_processing_statuses,
              exclude_processing_statuses,
              for_user_role,
              licence_activity_id_key='licence_activity'
            }) => {

            if(!activity_list.length) {
                return [];
            }
            return activity_list.filter(
                activity =>
                (!activity_id || activity[licence_activity_id_key] == activity_id) &&
                (!exclude_statuses ||
                    !(exclude_statuses.constructor === Array ? exclude_statuses : [exclude_statuses]
                        ).includes(activity.decision_action)) &&
                (!only_processing_statuses ||
                    (only_processing_statuses.constructor === Array ? only_processing_statuses : [only_processing_statuses]
                        ).includes(activity.processing_status.id ? activity.processing_status.id : activity.processing_status)) &&
                (!exclude_processing_statuses ||
                    !(exclude_processing_statuses.constructor === Array ? exclude_processing_statuses : [exclude_processing_statuses]
                        ).includes(activity.processing_status.id ? activity.processing_status.id : activity.processing_status)) &&
                (!for_user_role || rootGetters.hasRole(for_user_role, activity.id))
            );
        },
    },
    mutations: {
        [UPDATE_APPLICATION] (state, application) {
            Vue.set(state, 'application', {...application});
        },
        [UPDATE_ORIGINAL_APPLICATION] (state, application) {
            Vue.set(state, 'original_application', {...application});
        },
        [UPDATE_ORG_APPLICANT] (state, { key, value }) {
            if(state.application.org_applicant == null) {
                Vue.set(state.application, "org_applicant", {});
            }
            Vue.set(state.application.org_applicant, key, value);
        },
        [UPDATE_PROXY_APPLICANT] (state, { key, value }) {
            if(state.application.proxy_applicant == null) {
                Vue.set(state.application, "proxy_applicant", {});
            }
            Vue.set(state.application.proxy_applicant, key, value);
        },
    },
    actions: {
        refreshAddresses({ commit, state, getters }) {
            if (getters.applicant_type === 'org') {
                commit(UPDATE_ORG_APPLICANT, {key: 'address', value: state.org_address});
            };
            if (getters.applicant_type === 'proxy') {
                commit(UPDATE_PROXY_APPLICANT,  {key: 'address', value: state.proxy_address});
            };
        }, 
        loadApplication({ dispatch, commit }, { url }) {
            return new Promise((resolve, reject) => {
                Vue.http.get(url).then(res => {
                    dispatch('setOriginalApplication', res.body);
                    dispatch('setApplication', res.body);
                    for(let form_data_record of res.body.data) {
                        dispatch('setFormValue', {
                            key: form_data_record.field_name,
                            value: {
                                "value": form_data_record.value,
                                "comment_value": form_data_record.comment,
                                "deficiency_value": form_data_record.deficiency,
                                "schema_name": form_data_record.schema_name,
                                "component_type": form_data_record.component_type,
                                "instance_name": form_data_record.instance_name,
                            }
                        });
                    }
                    resolve();
                },
                err => {
                    console.log(err);
                    reject();
                });
            })
        },
        revertApplication({ dispatch, commit, state }) {
            commit(UPDATE_APPLICATION, state.original_application);
            dispatch('refreshAddresses');
        },
        setOriginalApplication({ commit }, application) {
            commit(UPDATE_ORIGINAL_APPLICATION, application);
        },
        setApplication({ dispatch, commit }, application) {
            commit(UPDATE_APPLICATION, application);
            dispatch('refreshAddresses');
        },
        refreshApplicationFees({ dispatch, state, getters, rootGetters }) {
            Vue.http.post('/api/application/estimate_price/', {
                    'application_id': getters.application_id,
                    'field_data': rootGetters.renderer_form_data,
            }).then(res => {
                dispatch('setApplication', {
                    ...state.application,
                    application_fee: res.body.fees.application,
                    licence_fee: res.body.fees.licence
                });
            }, err => {
                console.log(err);
            });
        },
    }
}
