import Vue from 'vue';
import {
    UPDATE_RENDERER_TABS,
    UPDATE_VISIBLE_COMPONENT
} from '@/store/mutation-types';

export const rendererStore = {
    state: {
        tabs: [],
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
        isComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
    },
    mutations: {
        [UPDATE_RENDERER_TABS] (state, tabs) {
            state.tabs = tabs;
        },
        [UPDATE_VISIBLE_COMPONENT] (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
    },
    actions: {
        setRendererTabs({ commit }, tabs) {
            commit(UPDATE_RENDERER_TABS, tabs);
        },
        toggleVisibleComponent({ commit, getters }, component_id) {
            commit(UPDATE_VISIBLE_COMPONENT,
                {key: component_id, value: !getters.isComponentVisible(component_id)});
        }
    }
}
