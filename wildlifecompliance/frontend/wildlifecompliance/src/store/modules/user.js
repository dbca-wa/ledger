import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import {
    UPDATE_SELECTED_TAB_ID,
    UPDATE_SELECTED_TAB_NAME,
    UPDATE_CURRENT_USER,
} from '@/store/mutation-types';

export const userStore = {
    state: {
        selected_activity_tab_id: 0,
        selected_activity_tab_name: '',
        current_user: {},
        
    },
    getters: {
        current_user: state => state.current_user,
        compliance_allocated_group: state => state.compliance_allocated_group,
        selected_activity_tab_id: state => state.selected_activity_tab_id,
        selected_activity_tab_name: state => state.selected_activity_tab_name,
        hasRole: (state, getters, rootState, rootGetters) => (role, activity_id) => {
            if(rootGetters.application.user_roles == null) {
                return false;
            }
            return rootGetters.application.user_roles.find(
                role_record =>
                (role.constructor === Array ? role : [role]
                    ).includes(role_record.role) && (!activity_id || activity_id == role_record.activity_id)
            );
        },
        visibleConditionsFor: (state, getters, rootState, rootGetters) => (for_role, processing_status, tab_id) => {
            return rootGetters.licence_type_data.activity.filter(activity =>
                activity.name && activity.processing_status.id == processing_status && getters.hasRole(for_role, activity.id) &&
                (!tab_id || tab_id == activity.id)
            );
        },
        canViewDeficiencies: (state, getters) => {
            return getters.hasRole('licensing_officer') || getters.application.can_current_user_edit;
        },
        canEditDeficiencies: (state, getters) => {
            return getters.hasRole('licensing_officer');
        },
        canViewComments: (state, getters) => {
            return getters.hasRole('licensing_officer') || getters.hasRole('assessor');
        },
    },
    mutations: {
        [UPDATE_SELECTED_TAB_ID] (state, tab_id) {
            state.selected_activity_tab_id = tab_id;
        },
        [UPDATE_SELECTED_TAB_NAME] (state, tab_name) {
            state.selected_activity_tab_name = tab_name;
        },
        [UPDATE_CURRENT_USER] (state, user) {
            Vue.set(state, 'current_user', {...user});
        },

    },
    actions: {
        setActivityTab({ commit }, { id, name }) {
            commit(UPDATE_SELECTED_TAB_ID, id);
            commit(UPDATE_SELECTED_TAB_NAME, name);
        },
        loadCurrentUser({ dispatch }, { url }) {
            console.log(url);
            return new Promise((resolve, reject) => {
                Vue.http.get(url).then(res => {
                    dispatch('setCurrentUser', res.body);
                    resolve();
                },
                err => {
                    console.log(err);
                    reject();
                });
            })
        },
        
        setCurrentUser({ dispatch, commit }, user) {
            commit(UPDATE_CURRENT_USER, user);
        },
    }
}
