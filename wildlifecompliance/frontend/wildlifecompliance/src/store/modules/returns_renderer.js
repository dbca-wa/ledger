import Vue from 'vue';
import {
    UPDATE_RETURNS_TABS,
    UPDATE_SELECTED_TAB_ID,
    UPDATE_VISIBLE_COMPONENT,
} from '@/store/mutation-types';

export const returnsRendererStore = {
    state: {
        tabs: [],
        visible_components: [],
        selected_returns_tab_id: 0,
    },
    getters: {
        returns_tabs: state => state.tabs,
        selected_returns_tab_id: state => state.selected_returns_tab_id,
        isReturnComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
    },
    mutations: {
        [UPDATE_RETURNS_TABS] (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        [UPDATE_SELECTED_TAB_ID] (state, tab_id) {
            state.selected_returns_tab_id = tab_id;
        },
        [UPDATE_VISIBLE_COMPONENT] (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
    },
    actions: {
        toggleVisibleComponent({ commit, getters }, { component_id, visible }) {
            commit(UPDATE_VISIBLE_COMPONENT,
                {key: component_id, value: visible});
        },
        setReturnsTab({ commit }, { id, name }) {
            commit(UPDATE_SELECTED_TAB_ID, id);
        },
    }
}
