import Vue from 'vue';
import {
    UPDATE_RENDERER_TABS,
    UPDATE_RENDERER_SECTIONS,
    UPDATE_VISIBLE_COMPONENT
} from '@/store/mutation-types';

export const rendererStore = {
    state: {
        tabs: [],
        sections: {},
        visible_components: []
    },
    getters: {
        renderer_tabs: state => state.tabs,
        visibleActivities: (state, getters, rootState, rootGetters) => (
            hide_decisions, hide_processing_statuses) => {
            return rootGetters.application.schema.filter(
                activity => getters.isActivityVisible(
                    activity.id, hide_decisions, hide_processing_statuses)
            );
        },
        isActivityVisible: (state, getters, rootState, rootGetters) => (
            activity_id, hide_decisions, hide_processing_statuses) => {
            return rootGetters.isApplicationActivityVisible(activity_id,
                hide_decisions,
                hide_processing_statuses
            );
        },
        unfinishedActivities: (state, getters, rootState, rootGetters) => {
            return getters.visibleActivities(
                ['issued', 'declined'],  // Hide by decision
                //['discarded']  // Hide by processing_status
            ).filter(activity => !rootGetters.application.has_amendment ||
                rootGetters.application.amendment_requests.find(
                    request => request.licence_activity.id == activity.id
                )
            );
        },
        isComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
        sectionsForTab: (state) => (tab_id) => {
            return state.sections[tab_id] ? state.sections[tab_id] : [];
        },
    },
    mutations: {
        [UPDATE_RENDERER_TABS] (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        [UPDATE_RENDERER_SECTIONS] (state, sections) {
            Vue.set(state, 'sections', {...sections});
        },
        [UPDATE_VISIBLE_COMPONENT] (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
    },
    actions: {
        setRendererTabs({ commit }, tabs) {
            commit(UPDATE_RENDERER_TABS, tabs);
        },
        setRendererSections({ commit }, sections) {
            commit(UPDATE_RENDERER_SECTIONS, sections);
        },
        toggleVisibleComponent({ commit, getters }, { component_id, visible }) {
            commit(UPDATE_VISIBLE_COMPONENT,
                {key: component_id, value: visible});
        }
    }
}
