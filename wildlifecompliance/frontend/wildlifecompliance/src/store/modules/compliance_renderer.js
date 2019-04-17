import Vue from 'vue';
/*
import {
    UPDATE_RENDERER_TABS,
    UPDATE_RENDERER_SECTIONS,
    UPDATE_VISIBLE_COMPONENT,
    TOGGLE_FINALISED_TABS,
    UPDATE_FORM_DATA,
    UPDATE_FORM_FIELD,
    REMOVE_FORM_FIELD,
} from '@/store/mutation-types';
*/
export const complianceRendererStore = {
    namespaced: true,
    state: {
        tabs: [],
        sections: {},
        visible_components: [],
        visibility: {
            //'exclude_decisions': ['issued', 'declined'],
            //'exclude_processing_status': ['discarded']
        },
        form_data: {},
    },
    getters: {
        renderer_tabs: state => state.tabs,
        renderer_form_data: state => state.form_data,
        /*
        visibleActivities: (state, getters, rootState, rootGetters) => (
            hide_decisions, hide_processing_statuses, for_user_role) => {
            return rootGetters.application.schema.filter(
                activity => getters.isActivityVisible(
                    activity.id, hide_decisions, hide_processing_statuses, for_user_role)
            );
        },
        isActivityVisible: (state, getters, rootState, rootGetters) => (
            activity_id, hide_decisions, hide_processing_statuses, for_user_role) => {
            return rootGetters.isApplicationActivityVisible(activity_id,
                hide_decisions,
                hide_processing_statuses,
                for_user_role
            );
        },
        unfinishedActivities: (state, getters, rootState, rootGetters) => {
            return getters.visibleActivities(
                state.visibility.exclude_decisions, // Hide by decision
                state.visibility.exclude_processing_status  // Hide by processing_status
            ).filter(activity => !rootGetters.application.has_amendment ||
                rootGetters.application.amendment_requests.find(
                    request => request.licence_activity.id == activity.id
                )
            );
        },
        */
        isComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
        sectionsForTab: (state) => (tab_id) => {
            return state.sections[tab_id] ? state.sections[tab_id] : [];
        },
        getFormValue: (state) => (component_name) => {
            return state.form_data[component_name] ? state.form_data[component_name].value : null;
        }
    },
    mutations: {
        updateRendererTabs (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        updateRendererSections (state, sections) {
            Vue.set(state, 'sections', {...sections});
        },
        updateVisibleComponent (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
        toggleFinalisedTabs (state, visible) {
            Vue.set(state.visibility, 'exclude_decisions', visible ? [] : ['issued', 'declined']);
        },
        updateFormData (state, form_data) {
            if(form_data == null) {
                Vue.set(state, 'form_data', {});
            }
            else {
                Vue.set(state, 'form_data', {...form_data});
            }
        },
        updateFormField (state, { key, value }) {
            let currentValue = state.form_data[key] ? {...state.form_data[key]} : {};
            for(let idx in value) {
                currentValue[idx] = value[idx];
            }
            Vue.set(state.form_data, key, currentValue);
        },
        removeFormField (state, key) {
            Vue.delete(state.form_data, key);
        },
    },
    actions: {
        setRendererTabs({ commit }, tabs) {
            commit(updateRendererTabs, tabs);
        },
        setRendererSections({ commit }, sections) {
            commit(updateRendererSections, sections);
        },
        toggleVisibleComponent({ commit, getters }, { component_id, visible }) {
            commit(updateVisibleComponent,
                {key: component_id, value: visible});
        },
        toggleFinalisedTabs({ commit }, visible) {
            commit(toggleFinalisedTabs, visible);
        },
        setFormData({ commit }, form_data) {
            commit(updateFormData, form_data);
        },
        setFormValue({ commit }, params) {
            commit(updateFormField, params);
        },
        removeFormInstance({ state, commit }, instanceId) {
            for(let key in state.form_data) {
                if(!key.includes(instanceId)) {
                    continue;
                }
                commit(removeFormField, key);
            }
        },
        saveFormData({ dispatch, commit, getters }, { url }) {
            return new Promise((resolve, reject) => {
                Vue.http.post(url, getters.renderer_form_data).then(res => {
                    resolve();
                },
                err => {
                    console.log(err);
                    reject();
                });
            })
        },
    }
}
