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
        application: {},
    },
    getters: {
        application: state => state.application,
        original_application: state => state.original_application,
        application_id: state => state.application.id,
        licence_type_data: state => state.application.licence_type_data,
        org_address: state => state.application.org_applicant != null && state.application.org_applicant.address != null ? state.application.org_applicant.address : {},
        proxy_address: state => state.application.proxy_applicant != null && state.application.proxy_applicant.address != null ? state.application.proxy_applicant.address : {},
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
    },
    mutations: {
        [UPDATE_APPLICATION] (state, application) {
            state.application = application;
        },
        [UPDATE_ORIGINAL_APPLICATION] (state, application) {
            state.application = application;
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
        }
    }
}
