import Vue from 'vue';
import {
    updateSelectedTabID,
    updatedSelectedTabName,
    updateCurrentUser,
} from '@/store/mutation-types';

export const complianceUserStore = {
    state: {
        selected_tab_id: 0,
        selected_tab_name: '',
        current_user: {},
    },
    namespaced: true,
    getters: {
        current_user: state => state.current_user,
        selected_tab_id: state => state.selected_tab_id,
        selected_tab_name: state => state.selected_tab_name,

        hasRole: (state, getters, rootState, rootGetters) => (role, activity_id) => {
            /*
            if (rootGetters.application.user_roles == null) {
                return false;
            }
            return rootGetters.application.user_roles.find(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            );
            */
            return true;
        },
        /*
        visibleConditionsFor: (state, getters, rootState, rootGetters) => (for_role, processing_status, tab_id) => {
            return rootGetters.licence_type_data.activity.filter(activity =>
                activity.name && activity.processing_status.id == processing_status && getters.hasRole(for_role, activity.id) &&
                (!tab_id || tab_id == activity.id)
            );
        },
        */
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
        updateSelectedTabID(state, tab_id) {
            state.selected_tab_id = tab_id;
        },
        updatedSelectedTabName(state, tab_name) {
            state.selected_tab_name = tab_name;
        },
        updateCurrentUser(state, user) {
            Vue.set(state, 'user', {
                ...user
            });
        },
    },
    actions: {
        /*
        setActivityTab({
            commit
        }, {
            id,
            name
        }) {
            commit(UPDATE_SELECTED_TAB_ID, id);
            commit(UPDATE_SELECTED_TAB_NAME, name);
        },
        */
        loadCurrentUser({
            dispatch,
            commit
        }, {
            url
        }) {
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
        setCurrentUser({
            dispatch,
            commit
        }, user) {
            commit(updateCurrentUser, user);
        },
    }
}