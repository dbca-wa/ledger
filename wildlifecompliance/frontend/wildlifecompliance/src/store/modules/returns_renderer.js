import Vue from 'vue';
import {
    UPDATE_RETURNS_TABS,
    UPDATE_VISIBLE_COMPONENT,
} from '@/store/mutation-types';

export const returnsRendererStore = {
    state: {
        tabs: [],
        visible_components: [],
    },
    getters: {
        returns_tabs: state => state.tabs,
        isReturnComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
    },
    mutations: {
        [UPDATE_RETURNS_TABS] (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        [UPDATE_VISIBLE_COMPONENT] (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
    },
    actions: {
        toggleVisibleComponent({ commit, getters }, { component_id, visible }) {
            commit(UPDATE_VISIBLE_COMPONENT,
                {key: component_id, value: visible});
        }
    }
}
