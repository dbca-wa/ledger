import Vue from 'vue';
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
        selected_activity_tab_id: state => state.selected_activity_tab_id,
        selected_activity_tab_name: state => state.selected_activity_tab_name,
        hasRole: (state, getters, rootState, rootGetters) => (role, activity_id) => {
            return rootGetters.application.user_roles.find(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            );
        },
        visibleConditionsFor: (state, getters, rootState, rootGetters) => (for_role, processing_status, tab_id) => {
            return rootGetters.licence_type_data.activity.filter(activity =>
                activity.name && activity.processing_status.id == processing_status && getters.hasRole(for_role, activity.id) &&
                (!tab_id || tab_id == activity.id)
            );
        },
        licenceActivities: (state, getters, rootState, rootGetters) => (activity_status, for_user_role) => {
            return rootGetters.licence_type_data.activity.filter(
                activity => (activity_status.constructor === Array ? activity_status : [activity_status]).includes(activity.processing_status.id)
                    && activity.name && getters.hasRole(for_user_role, activity.id)
            )
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
            Vue.set(state, 'user', {...user});
        },
    },
    actions: {
        setActivityTab({ commit }, { id, name }) {
            commit(UPDATE_SELECTED_TAB_ID, id);
            commit(UPDATE_SELECTED_TAB_NAME, name);
        },
        loadCurrentUser({ dispatch, commit }, { url }) {
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
